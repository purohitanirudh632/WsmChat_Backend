from django.urls import path
from .views import  ChatListCreateView,MessagesListCreateView

urlpatterns = [
    path('chats',ChatListCreateView.as_view(),name='chat'),
    path('messages',MessagesListCreateView.as_view(),name ='messages'),
    path('messages/<chat_id>',MessagesListCreateView.as_view(),name ='chatmessage')
]