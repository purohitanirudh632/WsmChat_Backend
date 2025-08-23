from django.shortcuts import render
from rest_framework import generics ,permissions
from rest_framework.permissions import IsAuthenticated 
from django.db.models import Q
from channels.layers import get_channel_layer
from rest_framework.decorators import api_view ,permission_classes
from .serlializers import CallSerializer,CallUpdateSerializer
from .models import Call
from asgiref.sync import async_to_sync
# Create your views here.
class CallListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CallSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Call.objects.filter(Q(caller =user)|Q(receiver = user)).select_related('caller','receiver')
    def perform_create(self, serializer):

        call = CallSerializer.save()

        channel_layer =  get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{call.receiver.id}",
            {
                'type': 'call_notification',
                'message': {
                    'type': 'incoming_call',
                    'call_id': str(call.id),
                    'caller': {
                        'id': call.caller.id,
                        'username': call.caller.username,
                        'name': f"{call.caller.first_name} {call.caller.last_name}".strip()
                    },
                    'call_type': call.call_type,
                    'created_at': call.created_at.isoformat()
                }
            }

        )
        
class CallDetailAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CallUpdateSerializer
    lookup_field ='id'

    def get_queryset(self):
        user= self.request.user
        return Call.objects.filter(Q(caller =user)|Q(receiver =user)).select_related('caller','receiver')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CallSerializer
        return CallUpdateSerializer

    def perform_update(self, serializer):
        call =serializer.save()
        # Notify both participants about status change
        channel_layer= get_channel_layer()

# Determine the other participant
        other_user = call.receiver if call.caller == self.request.user else call.caller

        message = {
            'type':'call_status_update',
            'call_id':str(call.id),
            'status':call.status,
            "updated_by": self.request.user.id
        }      

        #Add SDP Data if present
        if call.caller_sdp and self.request.user == call.caller:
            message['sdp'] = {'type':'offer','sdp':call.caller_sdp}
        elif call.receiver_sdp and self.request.user == call.receiver_sdp:
            message['sdp'] = {'type':'offer','sdp':call.receiver_sdp}


        #send to group

        async_to_sync(channel_layer.group_send)(f"user_{other_user.id}",{
            'type':'call_notification',
            "message":message
        })

@api_view(['post'])
@permission_classes([IsAuthenticated])

def  add_ice_candidate(request,call_id):
    