from rest_framework import serializers
from .models import *
from accounts.models import CustomUser
from rest_framework.exceptions import ValidationError
from accounts.serializers import UserProfileSerializer
from django.db.models import Count
from uuid import UUID




#--------------------------------------------------Chat------------------------------------------------------------

class ChatSerializer(serializers.ModelSerializer):
    users = UserProfileSerializer(many=True , read_only =True)
    user_ids =  serializers.ListField(
        child = serializers.UUIDField(),
        write_only =True,
        required = False
    ) 
    message_count =serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id','name','created_at','updated_at','users','user_ids','message_count','last_message']
        read_only_fields = ['id','created_at','updated_at']

    def get_message_count(self,obj):
        return obj.messages.count()
    
    def get_last_message(self,obj):
        last_message =  obj.messages.first()
        if last_message:
            return {
                'id': last_message.id,
                'content':last_message.content,
                'type':last_message.type,
                'sent_at':last_message.sent_at,
                'sender':last_message.user.name
            }
        return None
    
    def create(self,validated_data):
         
         user_ids = validated_data.pop('user_ids',[])

         current_user = self.context['request'].user
         all_user_ids = set(user_ids + [current_user.id])
         existing_chats = Chat.objects.annotate(user_count=Count('users',distinct=True)).filter(user_count=len(all_user_ids)).filter(users__in=all_user_ids).distinct()
         print(existing_chats)
         for chat in existing_chats:
             print(chat.users.all())
                # Get the set of user IDs in the current chat   
             chat_user_ids = set(chat.users.values_list('id', flat=True))
             if chat_user_ids == all_user_ids:
                return chat
             
            # If no existing chat found, create a new one
         chat  = Chat.objects.create(**validated_data)
         for user_id in all_user_ids:
            try:
                user = CustomUser.objects.get(id=user_id)
                UserChat.objects.create(user=user,chat=chat)
            except CustomUser.DoesNotExist:
                continue

         return chat       


class UserChatSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    chat = ChatSerializer(read_only=True)

    class Meta:
        model = UserChat
        fields = ['id','user','chat','joined_at']
        read_only_fields = ['id','joined_at']



#--------------------------------------------Group------------------------------------------------

class GroupSerilaizer(serializers.ModelSerializer):
    users = UserProfileSerializer(many=True , read_only =True)
    user_ids = serializers.ListField(
        child = serializers.UUIDField(),
        write_only = True,
        required = False
    )
    admin_ids = serializers.ListField(
        child = serializers.UUIDField(),
        write_only =True,
        required = True
    )
    members_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()


    class Meta:
        model = Group
        fields = ['id','group_name','created_at','updated_at','users','user_ids','members_count','last_message','admin_ids']
        read_only_fields = ['id','created_at','updated_at']

    def get_members_count(self,obj):
        return obj.users.count()
    
    def get_last_message(self,obj):
        last_message = obj.messages.first()
        if last_message:
            return {
                'id': last_message.id,
                'type':last_message.type,
                'content':last_message.content,
                'send_at':last_message.send_at,
                'sender':last_message.user.name
            }

    def create(self,validated_data):
        user_ids = validated_data.pop('user_ids',[])
        admin_ids = validated_data.pop('admin_ids',[])
        group = Group.objects.create(**validated_data)

        for user_id in user_ids:
            try:
                user = CustomUser.objects.get(id =user_id)
                is_admin = user_id in admin_ids
                UserGroup.objects.create(user = user,group =group,is_admin =is_admin)
            except UserGroup.DoesNotExist:
                continue

        return group        


class UserGroupSerializer(serializers.ModelSerializer):
    user= UserProfileSerializer(read_only =True)
    group = GroupSerilaizer(read_only =True)

    class Meta:
        model =UserGroup
        fields = ['id','user','group','joined_at']
        read_only_fields = ['id','joined_at']




#-----------------------------------------------------------Messages---------------------------------------------------------

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields =['id','sender','chat','group','type','content','sent_at','delivered_at','seen_at']
        read_only_fields = ['id','sent_at','delivered_at']

    def validated(self,data):
        chat = data.get('chat')
        group = data.get('group')

        if not chat and not group:
            raise serializers.ValidationError('Message should be at least in chat or group')
        
        if chat and group:
            raise serializers.ValidationError("Message can't be in both chat and group")
        
        return data
        
    def create(self,validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Messages

        fields = ['chat','group','type','content']
        # read_only_fields =[]

    def validate(self,data):
        chat = data.get('chat')
        group = data.get('group')

        if not chat and not group:
            raise serializers.ValidationError("Messagge must be in chat or group")
        
        if chat and group:
            raise serializers.ValidationError("Message must not be in both chat and group")
        
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)












# ------------------------------------------------------------#Old Code-------------------------------------------------------------------  




# class GetUsers(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ["name" , "email"]
        


# class MessageSerializer(serializers.ModelSerializer):
#     sender = serializers.StringRelatedField(read_only=True)

#     class Meta:
#         model = Messages
#         fields = ['id','Chat','sender','text','image','document','timestamp']


# class ChatSerializer(serializers.ModelSerializer):
#     # participants = serializers.ListField(child = serializers.EmailField(), write_only = True)
#     # Messages = serializers.StringRelatedField(many=True,read_only =True)
#     participants = RegisterSerializer(many=True, read_only=True)
#     participants_create = serializers.ListField(child=serializers.EmailField(), write_only=True)
    
#     class Meta:
#         model = Chat
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

# # check if Chat already exists
#         all_user_ids = sorted([user.id for user in users])
#         existing_chats = Chat.objects.annotate(participants_count=Count('participants')).filter(participants_count=len(all_user_ids))

#         for c in existing_chats:
#             chat_user_ids = sorted(list(c.participants.values_list('id',flat=True)))
#             if chat_user_ids == all_user_ids:
#                 print(chat_user_ids)
#                 return c
            

#         Chat = Chat.objects.create()
#         Chat.participants.set(users)
#         return Chat    