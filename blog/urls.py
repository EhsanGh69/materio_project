from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog_footer/', views.blog_footer, name='blog_footer'),
    path('all_categories/', views.all_categories, name='all_categories'),
    path('post_detail/<str:slug>', views.post_detail, name='post_detail'),
    path('create_comment/<int:post_id>', views.create_comment, name='create_comment'),
    path('create_answer/<int:comment_id>', views.create_answer, name='create_answer'),
    path('post_like_count/<int:post_id>', views.post_like_count, name='post_like_count'),
    path('post_like/<int:post_id>', views.post_like, name='post_like'),

    path('all_posts/', views.all_posts, name='all_posts'),
    path('all_posts/show_more/', views.all_posts, name='show_more_all_posts'),

    path('category_posts/<str:cat_name>', views.category_posts, name='category_posts'),
    path('category_posts/show_more/<str:cat_name>', views.category_posts, name='show_more_cat_posts'),

    path('author_posts/<str:username>', views.author_posts, name='author_posts'),
    path('author_posts/show_more/<str:username>', views.author_posts, name='show_more_auth_posts'),

    path('tag_posts/<str:tag>', views.tag_posts, name='tag_posts'),
    path('tag_posts/show_more/<str:tag>', views.tag_posts, name='show_more_tag_posts'),

    path('search/', views.search_posts, name='search'),
    path('search/show_more/', views.search_posts, name='show_more_search'),
]
