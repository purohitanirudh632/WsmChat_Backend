from rest_framework import serializers
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated ,AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['name'] = user.name
        token['phone_number'] = str(user.phone_number)  # Convert to string
        token['is_active'] = user.is_active
        token['date_joined'] = user.date_joined.isoformat()  # Convert to
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        data['name'] = self.user.name
        data['phone_number'] = str(self.user.phone_number ) # Convert to string
        data['is_active'] = self.user.is_active
        data['date_joined'] = self.user.date_joined.isoformat()  # Convert to string
        
        return data
    
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta():
        model = CustomUser
        fields = ['email','name','password','phone_number','date_joined','is_active']
        read_only = ['date_joined' , 'is_active']

    def create(self,validated_data):
        user = CustomUser.objects.create_user(
            email = validated_data['email'],
            name = validated_data['name'],
            phone_number = validated_data['phone_number'],
            password = validated_data['password']
        )
        
        return user    
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','name','phone_number', 'date_joined','is_active']
        read_only_fields =  ['id','date_joined']    



class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    permisstions_classes = [AllowAny]

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username = email,password =password)

            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("user is now disabled")
            data['user']=user
            return data
        else:
            raise serializers.ValidationError("No username or password found")
    def create(self, validated_data):
        return validated_data.get('user')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password =serializers.CharField()
    def validate_old_password(self,value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("old password is incorrect")
        
        return value

