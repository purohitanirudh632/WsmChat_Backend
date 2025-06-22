from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    avatar = serializers.URLField(read_only=True)

    class Meta():
        model = CustomUser
        fields = ['email','name','password', 'avatar']

    def create(self,validated_data):
        user = CustomUser.objects.create_user(
            email = validated_data['email'],
            name = validated_data['name'],
            password = validated_data['password']
        )
        
        return user    