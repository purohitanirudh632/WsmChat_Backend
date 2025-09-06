from rest_framework import serializers
from .models import Call,ICECandidate
from accounts.serializers import UserProfileSerializer
from accounts.models import  CustomUser

class CallSerializer(serializers.ModelSerializer):
    caller = UserProfileSerializer(write_only = True)
    reciver = UserProfileSerializer(write_only=True)
    reciver_id = serializers.IntegerField(write_only =True)

    class Meta:
        model = Call
        fields = ['id', 'caller', 'receiver', 'receiver_id', 'call_type', 
            'status', 'created_at', 'started_at', 'ended_at', 'duration']
        read_only_fields = ['id','caller','status', 'created_at', 'started_at', 'ended_at', 'duration']
    def create(self,validated_data):
        validated_data['caller'] = self.context['request'].user
        receiver_id = validated_data.pop('receiver_id')
        validated_data['receiver'] = CustomUser.objects.get(id = receiver_id)
        return super.create(validated_data)
    

class CallUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model= Call
        fields = ['status','caller_sdp','receiver_sdp']

    def validate_status(self,value):
        allowed_transitions = {
            'initiated': ['ringing', 'declined', 'missed'],
            'ringing': ['accepted', 'declined', 'missed'],
            'accepted': ['ended'],
        }

        current_status =self.instance.status
        if value not in allowed_transitions.get(current_status,[]):
            raise serializers.ValidationError(f"Cannot transition from {current_status} to {value}")
        return value


class ICEcandidatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICECandidate
        fields = ['id','candidate','created_at','sdp_mid','sdp_mline_index']
        read_only_fields = []

    def create(self,validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['call'] = self.context['call']
        return super.create(validated_data)


