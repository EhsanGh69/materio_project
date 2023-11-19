from django.urls import path

from .views import ChangePassword, AccountInfo, EditAccount

app_name = 'account'

urlpatterns = [
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('account_info/', AccountInfo.as_view(), name='account_info'),
    path('edit_account/', EditAccount.as_view(), name='edit_account'),
]
