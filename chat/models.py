from django.db import models
from django.conf import settings
from accounts.models import CustomUser
import uuid

# Create your models here.


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



# -----------------------------------------------------------------------chat---------------------------------------------------------------------

class Chat(TimestampModel):
    id = models.UUIDField(primary_key=True , default=uuid.uuid4 , editable=False)
    name = models.CharField(max_length=235,blank=True,null=True)
    users = models.ManyToManyField(CustomUser,through='UserChat',related_name='chats')

    class Meta:
        db_table = 'chat'
    def __str__(self):
        return self.name or f"{self.id}"    
    

class UserChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser,to_field='id', on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat,on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'UserChat'
        unique_together = ('user','chat')  # to  avoid data integrity problem 

    def __str__(self):
        return f"{self.user.name} in {self.chat}"    




#------------------------------------------------------Group---------------------------------------------------


class Group(TimestampModel):
    id  = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    group_name = models.CharField(max_length=235)
    group_description = models.TextField()
    
    users = models.ManyToManyField(CustomUser , through='UserGroup',related_name='group')
    class Meta:
        db_table = 'groups'

    def __str__(self):
        return self.group_name   



class UserGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser,to_field='id',on_delete=models.CASCADE)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'UserGroup'
        unique_together = ('user' ,'group')

    def __str__(self):
        return f"{self.user.name} in {self.group.group_name}"     


#-----------------------------------------------------------Messages----------------------------------------------------------------------------------

class Message_type(TimestampModel):
        Type_Choices = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'File'),
        ('location', 'Location'),
    ]
        
        type = models.CharField(max_length=20 , choices=Type_Choices , unique=True ,default='Text')
        class Meta:
           db_table = 'Message_type'

        def __str__(self):
            return self.type   
    

class Messages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser,to_field='id',on_delete=models.CASCADE,null=True ,blank=True,related_name='messages')
    chat = models.ForeignKey(Chat,on_delete=models.CASCADE,null=True ,blank=True,related_name='messages')
    group = models.ForeignKey(Group,on_delete=models.CASCADE,null=True,blank=True,related_name='messages')
    type = models.ForeignKey(Message_type, on_delete=models.CASCADE,null=False ,blank=True)
    
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True ,blank=True)
    seen_at = models.DateTimeField(null=True ,blank=True)
    class Meta:
        db_table = 'messages'
        ordering = ['-sent_at']
        constraints  = [
            models.CheckConstraint(
                check = (models.Q(chat__isnull = True , group__isnull = False) | models.Q(chat__isnull = False , group__isnull = True)) 
                ,name = 'message_belongs_to_chat_or_group'
            )
        ]

# CHECK (
#   (chat_id IS NOT NULL AND group_id IS NULL)
#   OR
#   (chat_id IS NULL AND group_id IS NOT NULL)
# )         this will be the query made to db


    def __str__(self):
        target = self.chat or self.group
        return f"Message from {self.user.name} in {target} at {self.sent_at}"

    def save(self,*args , **kwargs):
        if not self.delivered_at:
            self.delivered_at = self.sent_at
        super().save(*args,**kwargs)  












# class chat(models.Model):
#     participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"chat between :'{','.join(user.email for user in self.participants.all())}"

# def upload_to(instance,filename):
#     return f"chat_media/{instance.chat.id}/{filename}"
    
# class messages(models.Model):
#     sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
#     chat = models.ForeignKey('chat',on_delete=models.CASCADE,related_name='messages')
#     text = models.CharField(max_length=1000,blank=True)
#     image = models.ImageField(upload_to=upload_to,blank=True,null=True)
#     document = models.FileField(upload_to=upload_to,blank=True,null=True)   
#     timestamp = models.DateTimeField(auto_now_add=True)    

#     def __str__(self):
#         return f"{self.sender.email}: {self.text[:20] if self.text else 'Media Message'}"