from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import check_password
from sweetify.views import SweetifySuccessMixin

from .models import User
from .forms import UserRegister, UserLogin, ChangePassword, AccountSettings
from utils.tools import password_validation



class Register(FormView):
    template_name = 'account/register.html'
    form_class = UserRegister
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        phone_number = form.cleaned_data.get('phone_number')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        User.objects.create(username=username, password=password, phone_number=phone_number, email=email,
                                   first_name=first_name, last_name=last_name)
        return super().form_valid(form)
    

class Login(FormView):
    template_name = 'account/login.html'
    form_class = UserLogin
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.errors['__all__'] = form.error_class(["نام کاربری یا رمز عبور اشتباه است"])
            return super().form_invalid(form)


class ChangePassword(LoginRequiredMixin, SweetifySuccessMixin, FormView):
    template_name = 'account/change_password.html'
    form_class = ChangePassword
    success_url = reverse_lazy('account:account_info')
    success_message = "رمز عبور شما با موفقیت تغییر یافت"

    def form_valid(self, form):
        user = self.request.user
        old_password = form.cleaned_data.get('old_password')
        new_password = form.cleaned_data.get('new_password')
        check_old_password = check_password(old_password, user.password)
        validation_result = password_validation(new_password, user.username)
        if check_old_password and validation_result == 'not_err':
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(self.request, user)
            return super().form_valid(form)
        elif not check_old_password:
            form.add_error('old_password', 'رمز عبور کنونی اشتباه وارد شده است')
            return super().form_invalid(form)
        elif validation_result == 'combine_err':
            form.add_error('new_password', 'رمز عبور باید ترکیبی از حروف و اعداد باشد')
            return super().form_invalid(form)
        elif validation_result == 'similar_err':
            form.add_error('new_password', 'رمز عبور نباید شبیه نام کاربری باشد')
            return super().form_invalid(form)


class AccountInfo(LoginRequiredMixin, DetailView):
    template_name = 'account/account_info.html'
    context_object_name = "user"

    def get_object(self):
        pk = self.request.user.pk
        return get_object_or_404(User, pk=pk)
    

class EditAccount(LoginRequiredMixin, SweetifySuccessMixin, FormView):
    template_name = 'account/edit_account.html'
    form_class = AccountSettings
    success_url = reverse_lazy('account:account_info')
    success_message = 'اطلاعات حساب کاربری شما با موفقیت ویرایش شد'

    def get_initial(self):
        initial = super(EditAccount, self).get_initial()
        user = self.request.user
        initial.update({
            'phone_number': user.phone_number,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address
        })
        return initial
    
    def form_valid(self, form):
        user = self.request.user
        phone_number = form.cleaned_data.get('phone_number')
        is_exists_phone_number = User.objects.filter(phone_number=phone_number).exists()
        if phone_number != user.phone_number and is_exists_phone_number:
            form.add_error('phone_number', 'شماره تماس وارد شده از قبل وجود دارد')
            return super().form_invalid(form)
        return super().form_valid(form)
            
        
