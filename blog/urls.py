from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog_footer/', views.blog_footer, name='blog_footer'),
    path('all_categories/', views.all_categories, name='all_categories'),
    path('category_posts/<str:cat_name>', views.category_posts, name='category_posts'),
    path('author_posts/<str:username>', views.author_posts, name='author_posts'),
    path('post_detail/<str:slug>', views.post_detail, name='post_detail'),
    path('create_comment/<int:post_id>', views.create_comment, name='create_comment'),
    path('create_answer/<int:comment_id>', views.create_answer, name='create_answer'),
    path('post_like_count/<int:post_id>', views.post_like_count, name='post_like_count'),
    path('post_like/<int:post_id>', views.post_like, name='post_like'),
    path('tag_posts/<str:tag>', views.tag_posts, name='tag_posts'),
    path('search/', views.search_posts, name='search'),
    path('show_more/', views.search_posts, name='show_more'),
]
