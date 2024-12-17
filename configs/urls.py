from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from account.views import Login, Register, logout_user

urlpatterns = [
    path('', include('panel.urls')),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls'))
]

handler404 = 'configs.views.custom_404'

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
