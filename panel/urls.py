from django.urls import path

from .views import home

app_name = "panel"

urlpatterns = [
    path('', home, name='home')
]