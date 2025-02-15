from django.urls import path

from . import views

app_name = 'notifs'

urlpatterns = [
    path('reject_post/<int:pk>', views.post_reject, name='reject_post'),
    path('remove_post/<int:pk>', views.remove_post, name='remove_post'),
]
