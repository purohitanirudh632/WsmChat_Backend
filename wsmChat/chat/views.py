from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .serlializers import ChatSerializer , MessageSerializer
from .models import chat,messages
# from rest_framework import serializers


class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return chat.objects.filter(participants = self.request.user)
    
    def perform_create(self, serializer):
        serializer.save()
        # Chat.participants.add(self.request.user)


class MessagesCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
      serializer.save(sender = self.request.user)



# class ProtectedView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response({"message": f"Hello, {request.user.email}!"})

