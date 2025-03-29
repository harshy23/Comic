from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customeuser

# Register your models here.
class CustomeUserAdmin(UserAdmin):
    add_fieldsets=(
        (None ,{
            'classes':('wide',),
            'fields' : ('username' , 'email','first_name','last_name','password1','password2','city','state','address','phone','is_staff','is_active')
        }),
    )

admin.site.register(Customeuser,CustomeUserAdmin)
