from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

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
        self.create_user(email,password,**extra_fields)



class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='media/', null=True, blank=True, default='/media/chat_media/15/avatar.png')

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


# class Profile(models.Model):
#     user = models.ForeignKey(CustomUser, )
#     first_name = models.CharField(max_length=230)
#     last_name = models.CharField(max_length=230)
#     description = models.TextField()
#     contact_no = models.IntegerField(max_length=10)

