from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserAvatar


UserAdmin.fieldsets[1][1]['fields'] = (
    "first_name", 
    "last_name", 
    "email",
    "phone_number",
    "address"
)

UserAdmin.list_display += ("phone_number", )

admin.site.register(User, UserAdmin)


@admin.register(UserAvatar)
class UserAvatarAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar_img_tag', 'create_date', 'update_date']
    ordering = ['create_date', 'user']
    list_filter = ['user', 'create_date']
    search_fields = ['user']

