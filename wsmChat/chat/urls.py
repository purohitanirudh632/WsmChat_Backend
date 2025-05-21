from django.urls import path
from .views import  ChatListCreateView,MessagesCreateView

urlpatterns = [
    path('/chats',ChatListCreateView.as_view(),name='chat'),
    path('/messages',MessagesCreateView.as_view(),name ='messages')
]