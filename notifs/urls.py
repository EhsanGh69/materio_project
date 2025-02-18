from django.urls import path

from . import views

app_name = 'notifs'

urlpatterns = [
    path('reject_post/<int:pk>', views.post_reject, name='reject_post'),
    path('remove_post/<int:pk>', views.remove_post, name='remove_post'),
    path('edit_reject_notif/<int:pk>', views.edit_reject_notif, name='edit_reject_notif'),

    path('all_comments/', views.all_comments, name='all_comments'),
    path('paginate_comments/', views.paginate_comments, name='paginate_comments'),
    path('accept_comment/<int:pk>', views.accept_comment, name='accept_comment'),
    path('remove_comment/<int:pk>', views.remove_comment, name='remove_comment'),
]
