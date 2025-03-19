from django.contrib import admin

from .models import Post, Category, Comment, UserLike, PostVisit


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_draft', 'like_count', 'created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['creator', 'post', 'body', 'is_accept', 'is_answer', 'main_comment', 'created_at']

@admin.register(PostVisit)
class PostVisitAdmin(admin.ModelAdmin):
    list_display = ['post', 'ip_address', 'created_at']

admin.site.register(Category)
admin.site.register(UserLike)
