from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .serlializers import ChatSerializer , MessageSerializer , GetUsers
from wsmChat.chat.models import *
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser , FormParser

from rest_framework.decorators import api_view
from accounts.models import CustomUser

from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action


class ChatViewSet(viewsets.ViewSet):
    """
    """
    serializer_class = ChatSerializer

    @action(detail=False, methods=['post'], url_name='member')
    def create_chat_member(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_member = get_object_or_404(User, id=serializer.user_id)

        if not serializer.chat_id:
            chat  = get_object_or_404(Chat, id=serializer.chat_id)
        else:
            chat = Chat()
            chat.save()
        chat_member = UserChat(chat=chat, user=new_member)
        chat_member.save()

        return Response(
            {
                'message' : 'added a new member'
            },
            status=status.HTTP_200_OK
        )        

    def get_all_chats(self, request):
        chats = Chat.objects.filter(members__user=request.auth_user).members.order_by('chat')
        

# class Get_User_Serializer(generics.ListAPIView):
#     serializer_class = GetUsers
#     permission_classes = [AllowAny]

#     def get_queryset(self):
#         return CustomUser.objects.all()



# class ChatListCreateView(generics.ListCreateAPIView):
#     serializer_class = ChatSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return chat.objects.filter(participants = self.request.user)
    
#     def perform_create(self, serializer):
#         serializer.save()
#         # Chat.participants.add(self.request.user)


# class MessagesListCreateView(generics.ListCreateAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser,FormParser]

#     def perform_create(self, serializer):
#       serializer.save(sender = self.request.user)

#     def get_queryset(self):
#         chat_id = self.kwargs['chat_id']
#         user = self.request.user

#         try:
#             chat_instance = chat.objects.get(id = chat_id)
#         except chat.DoesNotExist:
#             raise PermissionDenied("chat Does not exist") 
        
#         if user not in chat_instance.participants.all():
#             raise PermissionDenied("User is not the part of chat")
        
#         return messages.objects.filter(chat = chat_instance).order_by('timestamp')

# # class ProtectedView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         return Response({"message": f"Hello, {request.user.email}!"})

