from django.shortcuts import render
from rest_framework import generics ,permissions ,response ,status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from channels.layers import get_channel_layer
from rest_framework.decorators import api_view ,permission_classes
from .serlializers import CallSerializer,CallUpdateSerializer,ICEcandidatesSerializer
from .models import Call , ICECandidate
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
        
class CallDetailView(generics.RetrieveUpdateAPIView):
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
    call = get_object_or_404(Call,id=call_id)

    if request.user not in [call.caller, call.receiver]:
        return response.Response(
            {'error': 'You are not part of this call'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ICEcandidatesSerializer(
        data=request.data, 
        context={'request': request, 'call': call}
    )
    
    if serializer.is_valid():
        ice_candidate = serializer.save()
        
        # Send ICE candidate to the other participant
        other_user = call.receiver if call.caller == request.user else call.caller
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{other_user.id}",
            {
                'type': 'call_notification',
                'message': {
                    'type': 'ice_candidate',
                    'call_id': str(call.id),
                    'candidate': ice_candidate.candidate,
                    'sdp_mid': ice_candidate.sdp_mid,
                    'sdp_mline_index': ice_candidate.sdp_mline_index,
                    'from_user': request.user.id
                }
            }
        )
        
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_ice_candidates(request, call_id):
    """Get ICE candidates for a call"""
    call = get_object_or_404(Call, id=call_id)

    # Check if user is part of this call
    if request.user not in [call.caller, call.receiver]:
        return response.Response(
            {'error': 'You are not part of this call'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get candidates from the other user
    other_user = call.receiver if call.caller == request.user else call.caller
    candidates = ICECandidate.objects.filter(call=call, user=other_user)
    
    serializer = ICEcandidatesSerializer(candidates, many=True)
    return response.Response(serializer.data)
    