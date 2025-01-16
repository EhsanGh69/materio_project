from datetime import datetime
from django.db import models
from django.utils.text import slugify

from account.models import User
from utils.tools import random_str



class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام')
    is_subcat = models.BooleanField(default=False, verbose_name='موضوع فرعی')
    main = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                             blank=True, related_name='subcats', verbose_name='موضوع اصلی')
    
    class Meta:
        verbose_name = 'موضوع'
        verbose_name_plural = 'موضوعات'
    
    def __str__(self):
        return self.name
    

def post_image_path(instance, filename):
    file_ext = filename.split('.')[-1]
    time_str = str(datetime.now().time()).split('.')[0].replace(':', '_')
    return f"post_images/{instance.title}_{time_str}_{random_str(10)}.{file_ext}"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='user_posts', verbose_name='نویسنده')
    title = models .CharField(max_length=250, verbose_name='عنوان')
    slug = models.SlugField(max_length=100, null=True, blank=True, verbose_name='عنوان در آدرس')
    content = models.TextField(verbose_name='متن')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                 related_name='cat_posts', verbose_name='دسته بندی')
    image = models.ImageField(upload_to=post_image_path, verbose_name='تصویر')
    tags = models.JSONField(blank=True, default=list, verbose_name='تگ ها')
    study_time = models.PositiveSmallIntegerField(default=0, verbose_name='زمان مطالعه', help_text='براساس دقیقه')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='زمان ویرایش')

    class Meta:
        verbose_name = 'پست'
        verbose_name_plural = 'پست‌ها'

    def save(self, *args, **kwargs):
        if not self.slug:
            post_slug = f'{random_str(10)}-{self.title}'
            self.slug = slugify(post_slug, allow_unicode=True)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} - {self.author.username}'
    

class Comment(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='user_comments', verbose_name='نویسنده')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='post_comments', verbose_name='پست')
    body = models.TextField(verbose_name='متن')
    is_accept = models.BooleanField(default=False, verbose_name='تایید شده')
    is_answer = models.BooleanField(default=False, verbose_name='پاسخ به کامنت')
    main_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                             blank=True, related_name='answers', verbose_name='کامنت اصلی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ارسال')

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت‌ها'
    
    def __str__(self):
        return f'{self.creator.username} - {self.post.title}'





