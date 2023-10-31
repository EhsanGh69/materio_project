from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from .views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
