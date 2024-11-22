from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import format_html


def avatar_image_path(instance, filename):
    file_ext = filename.split('.')[-1]
    time_str = str(datetime.now().time()).split('.')[0].replace(':', '_')
    return f"avatars/{instance.user.username}_{time_str}.{file_ext}"


class User(AbstractUser):
    address = models.TextField(verbose_name='آدرس', null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='شماره تماس')
    

class UserAvatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_avatar', verbose_name='کاربر')
    avatar = models.ImageField(upload_to=avatar_image_path, verbose_name='تصویر آواتار')
    create_date = models.DateField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    update_date = models.DateField(auto_now=True, verbose_name='تاریخ آخرین ویرایش')

    class Meta:
        verbose_name = 'تصویر آواتار کاربر'
        verbose_name_plural = 'تصاویر آواتار کاربران'

    def __str__(self):
        return self.user.username
    
    def avatar_img_tag(self):
        return format_html(f'''
            <a href='{self.avatar.url}'>
                <img src='{self.avatar.url}' width='100' height='100' style='border-radius: 50%;'>
            </a>
        ''')
    avatar_img_tag.short_description = "تصویر آواتار"


