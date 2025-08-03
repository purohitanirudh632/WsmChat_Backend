from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
import uuid
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self ,email,password = None,**extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using =self._db)
        return user
    
    def create_superuser(self ,email,password = None,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active",True)
        return self.create_user(email,password,**extra_fields)



class CustomUser(AbstractBaseUser,PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    date_joined = models.DateTimeField(auto_now_add=True)
    phone_number =PhoneNumberField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'customuser'


    def __str__(self):
        return self.email