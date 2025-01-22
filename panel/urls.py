from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.users_list, name='users'),
    path('panel_navbar/', views.panel_navbar, name='panel_navbar'),
    path('change_status/<int:pk>', views.change_status, name='change_status'),
    path('remove_user/<int:pk>', views.remove_user, name='remove_user'),
    path('change_access/<int:pk>', views.change_access, name='change_access'),
    path('all_cats/', views.all_categories, name='all_cats'),
    path('add_cat/', views.AddCategory.as_view(), name='add_cat'),
    path('edit_cat/<int:pk>/', views.EditCategory.as_view(), name='edit_cat'),
    path('remove_cat/<int:pk>', views.remove_category, name='remove_cat'),
    path('all_posts/', views.all_posts, name='all_posts'),
    path('paginate_posts/', views.paginate_posts, name='paginate_posts'),
    path('remove_post/<int:pk>', views.remove_post, name='remove_post'),
]
