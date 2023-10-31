from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


UserAdmin.fieldsets[1][1]['fields'] = (
    "first_name", 
    "last_name", 
    "email",
    "phone_number",
    "address"
)

UserAdmin.list_display += ("phone_number", )

admin.site.register(User, UserAdmin)

