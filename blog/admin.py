from django.contrib import admin

from .models import Post, Category, Comment, UserLike

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(UserLike)
