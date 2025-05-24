from django.db import models
from django.conf import settings

# Create your models here.
class chat(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"chat between :'{','.join(user.email for user in self.participants.all())}"

def upload_to(instance,filename):
    return f"chat_media/{instance.chat.id}/{filename}"
    
class messages(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    chat = models.ForeignKey('chat',on_delete=models.CASCADE,related_name='messages')
    text = models.CharField(max_length=1000,blank=True)
    image = models.ImageField(upload_to=upload_to,blank=True,null=True)
    document = models.FileField(upload_to=upload_to,blank=True,null=True)   
    timestamp = models.DateTimeField(auto_now_add=True)    

    def __str__(self):
        return f"{self.sender.email}: {self.text[:20] if self.text else 'Media Message'}"