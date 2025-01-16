from django.urls import path

from .views import index, blog_footer, all_categories, category_posts

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path('blog_footer/', blog_footer, name='blog_footer'),
    path('all_categories/', all_categories, name='all_categories'),
    path('category_posts/<str:cat_name>', category_posts, name='category_posts'),
]
