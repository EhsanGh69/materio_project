from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from .views import home, logout_user
from account.views import Login, Register

urlpatterns = [
    path('', home, name='home'),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
