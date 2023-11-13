from django import forms
from django.core import validators

from .models import User
from utils.tools import none_numeric_value



class UserRegister(forms.Form):
    use_required_attribute = False

    username = forms.CharField(
        widget=forms.TextInput(),
        required=False,
        label='نام کاربری',
        validators=[
            validators.MaxLengthValidator(
                limit_value=20,
                message='تعداد کاراکترهای واردشده بیش از حد مجاز است'
            ),
            validators.MinLengthValidator(
                limit_value=4,
                message='تعداد کاراکترهای واردشده کمتر از حد مجاز است'
            )
        ],
        help_text='''تعداد کاراکترهای مجاز بین ۴ تا ۲۰ می‌باشد
                    <br>
                    فقط شامل حروف، اعداد، و علامات @/./-/_
                  '''
    )

    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='رمز عبور',
        validators=[
            validators.MinLengthValidator(
                limit_value=8,
                message='رمز عبور باید حداقل هشت کاراکتر باشد'
            )
        ]
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='تأیید رمز عبور'
    )

    phone_number = forms.CharField(
        widget=forms.TextInput(),
        required=False,
        label='شماره همراه',
        validators=[
            validators.RegexValidator(
                regex=r'^0\d{10}$',
                message='شماره تماس وارد شده معتبر نمی‌باشد'
            )
        ]
    )

    email = forms.EmailField(
        widget=forms.EmailInput(),
        required=False,
        label='آدرس ایمیل',
        validators=[
            validators.RegexValidator(
                regex=r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$",
                message='آدرس ایمیل وارد شده معتبر نمی‌باشد'
            )
        ]
    )

    first_name = forms.CharField(
        widget=forms.TextInput(),
        validators=[none_numeric_value],
        required=False,
        label='نام'
    )

    last_name = forms.CharField(
        widget=forms.TextInput(),
        validators=[none_numeric_value],
        required=False,
        label='نام خانوادگی'
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('لطفاً نام کاربری را وارد نمایید')
        is_exists_username = User.objects.filter(username=username).exists()
        if is_exists_username:
            raise forms.ValidationError('نام کاربری واردشده از قبل وجود دارد')
        # range(48, 58) --> 0 - 9 | range(65, 91) --> A - Z | range(97, 123) --> a - z | [45, 46, 64, 95] --> .,@,-,_
        valid_ranges = [range(48, 58), range(65, 91), [45, 46, 64, 95]]
        for char in username:
            err_count = 0
            for valid_range in valid_ranges:
                if ord(char) not in valid_range:
                    err_count += 1
            if err_count == 4:
                raise forms.ValidationError('نام کاربری وارد شده دارای کاراکترهای غیرمجاز می‌باشد')
            
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('لطفاً رمز عبور را وارد نمایید')
        # checking password combination
        nums = [str(num) for num in range(0, 10)]
        list_control = []
        for char in password:
            if char in nums:
                list_control.append('n')
            else:
                list_control.append('l')
        if 'n' not in list_control or 'l' not in list_control:
            raise forms.ValidationError('رمز عبور باید ترکیبی از حروف و اعداد باشد')
        
        # checking password similarity to username
        chars = {'.', '-', '_', '@'}
        username = self.cleaned_data.get('username')
        username_letters = set(username.lower()) - chars
        password_letters = set(password.lower()) - chars
        if username_letters.union(password_letters) == username_letters:
            raise forms.ValidationError('رمز عبور نباید شبیه نام کاربری باشد')
        
        return password
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not confirm_password and password:
            raise forms.ValidationError('لطفاً رمز عبور خود را تأیید نمایید')
        if password and password != confirm_password:
            raise forms.ValidationError('تأیید رمز عبور با رمز عبور یکسان نیست')
        
        return confirm_password
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError('لطفاً شماره تماس خود را وارد نمایید')
        is_exists_phone_number = User.objects.filter(phone_number=phone_number).exists()
        if is_exists_phone_number:
            raise forms.ValidationError('شماره تماس وارد شده از قبل وجود دارد')
        
        return phone_number
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('لطفاً آدرس ایمیل خود را وارد نمایید')
        
        return email
    


class UserLogin(forms.Form):
    use_required_attribute = False

    username = forms.CharField(
        widget=forms.TextInput(),
        required=False,
        label='نام کاربری'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='رمز عبور'
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('لطفاً نام کاربری را وارد نمایید')
        
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('لطفاً رمز عبور خود را تأیید نمایید')
        
        return password
