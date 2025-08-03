from django.urls import re_path
from . import consumers ,GroupConsumers

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<chat_id>[0-9a-f\-]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/group/(?P<group_id>[0-9a-f\-]+)/$', GroupConsumers.GroupChatConsumer.as_asgi()),
]