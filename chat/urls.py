from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .views import *


router =DefaultRouter()
router.register(r'chat',chatViewset,basename='chat')
router.register(r'group',GroupViewSet,basename='group')
router.register(r'messages',MessageViewset,basename='messages')
router.register(r'user-chat',UserChatViewset,basename='userchat')
router.register(r'user-group',UserGroupViewset,basename='usergroup')

urlpatterns = [
    path('api/',include(router.urls)),
]
