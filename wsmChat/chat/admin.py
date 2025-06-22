from django.contrib import admin
from .models import *

admin.site.register(Message)
admin.site.register(Chat)
admin.site.register(UserGroup)
admin.site.register(UserChat)
admin.site.register(MessageType)
