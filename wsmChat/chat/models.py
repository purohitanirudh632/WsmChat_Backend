from django.db import models
from django.conf import settings
from wsmChat.models import TimestampModel
from accounts.models import CustomUser as User

class Chat(TimestampModel):
    pass

def upload_to(instance,filename):
    return f"chat_media/{instance.chat.id}/{filename}"

class Group(TimestampModel):
    """
    Represents a group chat with multiple users
    """
    name = models.CharField(max_length=255)
    
    # Many-to-many relationship with users
    group_members = models.ManyToManyField(User, through='UserGroup', related_name='group_members')

    class Meta:
        db_table = 'groups'

    def __str__(self):
        return self.name


class UserChat(models.Model):
    """
    Intermediate model for User-Chat many-to-many relationship
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_members'
        unique_together = ('user', 'chat')

    def __str__(self):
        return f"{self.user.name} in {self.chat}"


class UserGroup(models.Model):
    """
    Intermediate model for User-Group many-to-many relationship
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'group_members'
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.name} in {self.group.name}"

class MessageType(TimestampModel):
    name = models.CharField()
    
    def __str__(self):
        return self.name
    
class Message(models.Model):
    """
    Represents messages in chats or groups
    """
    # MESSAGE_TYPES = [
    #     ('text', 'Text'),
    #     ('image', 'Image'),
    #     ('video', 'Video'),
    #     ('audio', 'Audio'),
    #     ('file', 'File'),
    #     ('location', 'Location'),
    # ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message can belong to either a chat or a group (but not both)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')

    type = models.ForeignKey(MessageType, on_delete=models.CASCADE,null=False, blank=False)

    content = models.TextField()
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    seen_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['-sent_at']
        constraints = [
            # Ensure message belongs to either chat or group, but not both
            models.CheckConstraint(
                check=(
                    models.Q(chat__isnull=False, group__isnull=True) |
                    models.Q(chat__isnull=True, group__isnull=False)
                ),
                name='message_belongs_to_chat_or_group'
            )
        ]

    def __str__(self):
        target = self.chat or self.group
        return f"Message from {self.user.name} in {target} at {self.sent_at}"

    def save(self, *args, **kwargs):
        # Automatically set delivered_at when message is created
        if not self.delivered_at:
            self.delivered_at = self.sent_at
        super().save(*args, **kwargs)

# class Messages(models.Model):
#     sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
#     chat = models.ForeignKey('chat',on_delete=models.CASCADE,related_name='messages')
#     text = models.CharField(max_length=1000,blank=True)
#     image = models.ImageField(upload_to=upload_to,blank=True,null=True)
#     document = models.FileField(upload_to=upload_to,blank=True,null=True)   
#     timestamp = models.DateTimeField(auto_now_add=True)    

#     def __str__(self):
#         return f"{self.sender.email}: {self.text[:20] if self.text else 'Media Message'}"