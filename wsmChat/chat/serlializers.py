from rest_framework import serializers
from .models import chat,messages
from accounts.models import CustomUser
from rest_framework.exceptions import ValidationError
from accounts.serializers import RegisterSerializer
from django.db.models import Count
from wsmChat.chat.models import *

class ChatSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    chat_id = serializers.IntegerField(blank=True, null=True)
    
    class Meta:
        fields = ('__all__')



# class GetUsers(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ["name" , "email"]
        


# class MessageSerializer(serializers.ModelSerializer):
#     sender = serializers.StringRelatedField(read_only=True)

#     class Meta:
#         model = messages
#         fields = ['id','chat','sender','text','image','document','timestamp']


# class ChatSerializer(serializers.ModelSerializer):
#     # participants = serializers.ListField(child = serializers.EmailField(), write_only = True)
#     # messages = serializers.StringRelatedField(many=True,read_only =True)
#     participants = RegisterSerializer(many=True, read_only=True)
#     participants_create = serializers.ListField(child=serializers.EmailField(), write_only=True)
    
#     class Meta:
#         model = chat
#         fields = ['id','participants','created_at', 'participants_create']
#         read_only_fields = ['id','created_at']

#     def create(self,validated_data):
#         emails =validated_data.pop('participants_create')
#         print(emails)
#         request_user = self.context['request'].user
#         users = list(CustomUser.objects.filter(email__in =emails))

#         existing_emails = set(user.email for user in users)
#         requested_emails = set(emails)
#         missing_emails = requested_emails-existing_emails

#         if missing_emails:
#             raise ValidationError({
#                 'participants': [f"The following users do not exist: {', '.join(missing_emails)}"]
#             })
        
        
#         if request_user not in users:
#             users.append(request_user)

# # check if chat already exists
#         all_user_ids = sorted([user.id for user in users])
#         existing_chats = chat.objects.annotate(participants_count=Count('participants')).filter(participants_count=len(all_user_ids))

#         for c in existing_chats:
#             chat_user_ids = sorted(list(c.participants.values_list('id',flat=True)))
#             if chat_user_ids == all_user_ids:
#                 print(chat_user_ids)
#                 return c
            

#         Chat = chat.objects.create()
#         Chat.participants.set(users)
#         return Chat    