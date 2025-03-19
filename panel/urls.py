from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path('', views.home, name='home'),
    path('panel_navbar/', views.panel_navbar, name='panel_navbar'),

    path('users/', views.users_list, name='users'),
    path('paginate_users/', views.paginate_users, name='paginate_users'),
    path('user_details/<str:username>', views.user_details, name='user_details'),
    path('create_user/', views.CreateUser.as_view(), name='create_user'),
    path('update_user/<str:username>', views.UpdateUser.as_view(), name='update_user'),
    path('change_status/<int:pk>', views.change_status, name='change_status'),
    path('remove_user/<int:pk>', views.remove_user, name='remove_user'),

    path('all_cats/', views.all_categories, name='all_cats'),
    path('add_cat/', views.AddCategory.as_view(), name='add_cat'),
    path('edit_cat/<int:pk>/', views.EditCategory.as_view(), name='edit_cat'),
    path('remove_cat/<int:pk>', views.remove_category, name='remove_cat'),
    path('get_sub_cats/<int:cat_id>', views.get_sub_cats, name='get_sub_cats'),

    path('all_posts/', views.all_posts, name='all_posts'),
    path('paginate_posts/', views.paginate_posts, name='paginate_posts'),
    path('view_post/<str:slug>', views.view_post, name='view_post'),
    path('search_sort_posts/', views.paginate_posts, name='search_sort_posts'),
    path('get_status_count/', views.all_posts, name='get_status_count'),
    path('post_settings/<str:slug>', views.post_settings, name='post_settings'),

    path('get_related_tags/<int:cat_id>', views.get_related_tags, name='get_related_tags'),
    path('add_tag/<int:pk>', views.post_tags, name='add_tag'),
    path('edit_tag/<int:pk>', views.post_tags, name='edit_tag'),
    path('remove_tag/<int:pk>', views.post_tags, name='remove_tag'),
]
