from django.urls import path

from .views import home, change_status, remove_user, change_access, panel_navbar

app_name = "panel"

urlpatterns = [
    path('', home, name='home'),
    path('panel_navbar/', panel_navbar, name='panel_navbar'),
    path('change_status/<int:pk>', change_status, name='change_status'),
    path('remove_user/<int:pk>', remove_user, name='remove_user'),
    path('change_access/<int:pk>', change_access, name='change_access'),
]
