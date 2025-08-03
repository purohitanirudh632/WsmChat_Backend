from django.db import models
import uuid
from accounts.models import CustomUser
from django.utils import timezone
class call(models.Model):
    CALL_TYPES = (
    ('voice','Voice Call'),
    ('vedio','Vedio Call'),  
    )

    CALL_STATUS = (
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('accepted', 'accepted'),
        ('declined', 'Declined'),
        ('ended', 'Ended'),
        ('missed', 'Missed')
    )

    id = models.UUIDField(primary_key=True , default=uuid.uuid4 , editable=False)
    caller = models.ForeignKey(CustomUser , on_delete=models.CASCADE,related_name='outgoing_calls')
    receiver = models.ForeignKey(CustomUser , on_delete=models.CASCADE,related_name='incoming_calls')

    #WEBrtc Session data
    call_type = models.CharField(max_length=10,choices=CALL_TYPES)
    call_status = models.CharField(max_length=20,choices=CALL_STATUS,default='initiated')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Call duration in seconds
    duration = models.IntegerField(null=True, blank=True)

    class Meta:
        odering = [-'created_at']

    def __str__(self):
        return f"{self.call_type} from {self.caller} to {self.receiver} on {self.created_at}"

    def save(self,*args,**kwargs):
        if self.call_status == 'accepted' and not self.started_at:
            self.started_at =   timezone.now()
        elif self.call_status == 'ended' and self.started_at and  not self.ended_at:
                self.ended_at = timezone.now()

        self.duration = int((self.ended_at - self.started_at).total_seconds())  
        super.save(*args,**kwargs)        

        


# Create your models here.
