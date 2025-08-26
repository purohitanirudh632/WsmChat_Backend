from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display=('email','name','is_staff','is_active')
    # list_filter = ('is_staff','is_active')
    # fieldsets =(
    #     (None,{'fields':('email','name','password')}),
    #     ('permissions',{'fields':('is_staff','is_active','is_superuser','groups','user_permissions')}),
    # )
    # add_fieldsets=(
    #     (None,{
    #         'classes':('wide',),
    #         'fields':('email','name','password1','password2','is_staff','is_active')
    #     }),
    # )

    search_fields=('email',)
    ordering = ('email',)

admin.site.register(CustomUser,CustomUserAdmin)