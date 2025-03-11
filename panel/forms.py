from django import forms

from blog.models import Category
from account.models import User


class AddCategoryForm(forms.ModelForm):
    use_required_attribute = False
    class Meta:
        model = Category
        fields = "__all__"


class UpdateUserForm(forms.ModelForm):
    use_required_attribute = False

    username = forms.CharField(
        label='نام کاربری',
        error_messages={
            'required': 'لطفاً نام کاربری را وارد نمایید',
        }
    )

    email = forms.CharField(
        label='آدرس ایمیل',
        error_messages={
            'required': 'لطفاً آدرس ایمیل را وارد نمایید',
        }
    )

    phone_number = forms.CharField(
        label='شماره تماس',
        error_messages={
            'required': 'لطفاً شماره تماس را وارد نمایید',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

