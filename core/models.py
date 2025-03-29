from django.db import models

from django.contrib.auth.models import AbstractUser


# Create your models here.
class Customeuser(AbstractUser):
    city = models.CharField(max_length=100 ,blank=True ,null=True)
    state = models.CharField(max_length=100 ,blank=True ,null=True)
    address = models.TextField(blank=True ,null=True)
    phone = models.CharField(max_length=15 ,blank=True ,null=True)

    def __str__(self):
        return self.username
    
# In Django, both `AbstractUser` and `UserAdmin` serve different purposes related to user management, and it's important to understand their distinctions. Here's a concise breakdown:

# ### AbstractUser
# - **Purpose**: `AbstractUser` is a class used to create a custom user model in Django. It extends the default user model (`User`) provided by Django and allows developers to add their fields or override existing fields.
# - **Usage**: When you define a user model that extends `AbstractUser`, you can add additional fields such as `bio`, `profile_picture`, or what have you while still retaining the basic user functionality (like authentication).
# - **Inheritance**: It is commonly extended like this:
#   ```python
#   from django.contrib.auth.models import AbstractUser

#   class CustomUser(AbstractUser):
#       bio = models.TextField(blank=True, null=True)
#   ```
# - **Configuration**: You need to set `AUTH_USER_MODEL = 'yourapp.CustomUser'` in your settings to use your custom user model.

# ### UserAdmin
# - **Purpose**: `UserAdmin` is a class that comes with Django's admin interface to manage user objects. It's used to customize the way users are displayed and managed in the Django admin panel.
# - **Usage**: This class provides a framework for defining how users and their properties appear in the Django admin. You can customize the fields, list display, and form used in the admin.
# - **Customization**: Custom user models often require a custom `UserAdmin`. For example:
#   ```python
#   from django.contrib import admin
#   from django.contrib.auth.admin import UserAdmin
#   from .models import CustomUser

#   class CustomUserAdmin(UserAdmin):
#       model = CustomUser
#       list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
#       fieldsets = UserAdmin.fieldsets + (
#           (None, {'fields': ('bio',)}),
#       ) 

#   admin.site.register(CustomUser, CustomUserAdmin)
#   ```

# ### Summary
# - **`AbstractUser`**: Used for creating a custom user model with additional or modified fields.
# - **`UserAdmin`**: Used for customizing the admin panel interface for managing user accounts.

# If you need more details or examples, feel free to ask!
