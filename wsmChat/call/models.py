from django.db import models
from  accounts.models import CustomUser
from django.utils import timezone
import uuid

class Call(models.Model):
    CALL_TYPES = (
        ('voice', 'Voice Call'),
        ('video', 'Video Call'),
    )
    
    CALL_STATUS = (
    ('initiated', 'Initiated'),
    ('ringing', 'Ringing'),
    ('accepted', 'Accepted'),
    ('declined', 'Declined'),
    ('ended', 'Ended'),
    ('missed', 'Missed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    caller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='outgoing_calls')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='incoming_calls')
    call_type = models.CharField(max_length=10, choices=CALL_TYPES)
    status = models.CharField(max_length=20, choices=CALL_STATUS, default='initiated')
    
    # WebRTC session data
    caller_sdp = models.TextField(null=True, blank=True)
    receiver_sdp = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Call duration in seconds
    duration = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.call_type} call from {self.caller.username} to {self.receiver.username}"
    
    def save(self, *args, **kwargs):
        if self.status == 'accepted' and not self.started_at:
            self.started_at = timezone.now()
        elif self.status == 'ended' and self.started_at:
            if not self.ended_at:
                self.ended_at = timezone.now()
            self.duration = int((self.ended_at - self.started_at).total_seconds())
        super().save(*args, **kwargs)

class CallParticipant(models.Model):
    """Track additional participants for group calls (future feature)"""
    call = models.ForeignKey(Call, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['call', 'user']



class ICECandidate(models.Model):
    call = models.ForeignKey(Call,on_delete=models.CASCADE,related_name='ice_candidate')
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    candidate = models.TextField()
    sdp_mid = models.CharField(max_length=100)
    sdp_mline_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
