from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView

from account.views import Login, Register, logout_user, ResetPassword, account_activate
from .views import custom_404, custom_403, custom_500

urlpatterns = [
    path('', include('blog.urls')),
    path('panel/', include('panel.urls')),
    path('notifs/', include('notifs.urls')),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', account_activate, name='activate'),
    path('logout/', logout_user, name='logout'),
    path('reset_password/', ResetPassword.as_view(), name='reset_password'),
    path('reset_password_confirm/<uidb64>/<token>/', 
        PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"), 
        name='reset_password_confirm'),
    path('password_reset_complete/', 
        PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"), 
        name='password_reset_complete'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls'))
]

handler404 = custom_404
handler403 = custom_403
handler500 = custom_500

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
