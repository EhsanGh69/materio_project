from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth import authenticate, login

from .models import User
from .forms import UserRegister, UserLogin



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





