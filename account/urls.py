from django.urls import path

from .views import ChangePassword, AccountInfo, EditAccount, remove_avatar, CreatePost, my_posts, my_posts_table

app_name = 'account'

urlpatterns = [
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('account_info/', AccountInfo.as_view(), name='account_info'),
    path('edit_account/', EditAccount.as_view(), name='edit_account'),
    path('remove_avatar/', remove_avatar, name='remove_avatar'),
    path('create_post/', CreatePost.as_view(), name='create_post'),
    path('my_posts/', my_posts, name='my_posts'),
    path('my_posts_table/', my_posts_table, name='my_posts_table'),
    path('my_posts_search/', my_posts_table, name='my_posts_search'),
]
