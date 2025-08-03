from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display=('email','name','is_staff','is_active','phone_number','date_joined')
    list_filter = ('is_staff','is_active')
    fieldsets =(
        (None,{'fields':('email','name','password','phone_number','date_joined')}),
        ('permissions',{'fields':('is_staff','is_active','is_superuser','groups','user_permissions')}),
    )
    readonly_fields = ['date_joined']
    add_fieldsets=(
        (None,{
            'classes':('wide',),
            'fields':('email','name','phone_number','password1','password2','is_staff','is_active')
        }),
    )

    search_fields=('email',)
    ordering = ('email',)

admin.site.register(CustomUser,CustomUserAdmin)