from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('change_password/', views.ChangePassword.as_view(), name='change_password'),
    path('account_info/', views.AccountInfo.as_view(), name='account_info'),
    path('edit_account/', views.EditAccount.as_view(), name='edit_account'),
    path('remove_avatar/', views.remove_avatar, name='remove_avatar'),

    path('create_post/', views.CreatePost.as_view(), name='create_post'),
    path('edit_draft_post/<str:slug>', views.EditDraftPost.as_view(), name='edit_draft_post'),
    path('edit_reject_post/<str:slug>', views.EditDraftPost.as_view(), name='edit_reject_post'),
    path('remove_post_image/<int:pk>', views.remove_post_image, name='remove_post_image'),
    path('remove_draft_post/<int:pk>', views.remove_draft_post, name='remove_draft_post'),
    path('my_posts/', views.my_posts, name='my_posts'),
    path('my_posts_table/', views.my_posts_table, name='my_posts_table'),
    path('my_posts_search/', views.my_posts_table, name='my_posts_search'),
    path('my_fav_posts/', views.my_fav_posts, name='my_fav_posts'),
    path('fav_posts_paginate/', views.fav_posts_paginate, name='fav_posts_paginate'),
]
