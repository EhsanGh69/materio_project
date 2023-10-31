from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    address = models.TextField(verbose_name='آدرس')
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='شماره تماس')
    

