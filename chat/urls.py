from django.urls import path
from .views import  ChatListCreateView,MessagesListCreateView , Get_User_Serializer

urlpatterns = [
    path('',ChatListCreateView.as_view(),name='chat'),
    path('messages',MessagesListCreateView.as_view(),name ='messages'),
    path('messages/<chat_id>',MessagesListCreateView.as_view(),name ='chatmessage'),
    path('getusers',Get_User_Serializer.as_view(),name = 'getusers')
]