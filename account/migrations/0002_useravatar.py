# Generated by Django 4.2.6 on 2024-11-20 16:25

import account.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAvatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(upload_to=account.models.avatar_image_path, verbose_name='تصویر آواتار')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('update_date', models.DateField(auto_now=True, verbose_name='تاریخ آخرین ویرایش')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_avatar', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'تصویر آواتار کاربر',
                'verbose_name_plural': 'تصاویر آواتار کاربران',
            },
        ),
    ]
