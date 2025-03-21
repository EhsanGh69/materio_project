from django import forms
from django.core import validators
from ckeditor.widgets import CKEditorWidget

from .models import User
from blog.models import Post
from utils.tools import none_numeric_value, password_validation



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
        widget=forms.PasswordInput(render_value=True),
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
        widget=forms.PasswordInput(render_value=True),
        required=False,
        label='تأیید رمز عبور'
    )

    phone_number = forms.CharField(
        widget=forms.TextInput(),
        required=False,
        label='شماره همراه',
        validators=[
            validators.RegexValidator(
                regex=r'09(1[0-9]|3[1-9]|2[1-9])-?[0-9]{3}-?[0-9]{4}',
                message='شماره همراه وارد شده معتبر نمی‌باشد'
            )
        ]
    )

    email = forms.EmailField(
        widget=forms.EmailInput(),
        required=False,
        label='آدرس ایمیل',
        # validators=[
        #     validators.RegexValidator(
        #         regex=r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$",
        #         message='آدرس ایمیل وارد شده معتبر نمی‌باشد'
        #     )
        # ]
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
        # range(48, 58) --> 0 - 9 | range(65, 91) --> A - Z 
        # range(97, 123) --> a - z | [45, 46, 64, 95] --> .,@,-,_
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
        username = self.cleaned_data.get('username')
        validation_result = password_validation(password, username)

        if not password:
            raise forms.ValidationError('لطفاً رمز عبور را وارد نمایید')
        if validation_result == 'combine_err':
            raise forms.ValidationError('رمز عبور باید ترکیبی از حروف و اعداد باشد')
        elif validation_result == 'similar_err':
            raise forms.ValidationError('رمز عبور نباید شبیه نام کاربری باشد')
            
        return password
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not confirm_password and password:
            raise forms.ValidationError('لطفاً رمز عبور را تأیید نمایید')
        if password and password != confirm_password:
            raise forms.ValidationError('تأیید رمز عبور با رمز عبور یکسان نیست')
        
        return confirm_password
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError('لطفاً شماره تماس را وارد نمایید')
        is_exists_phone_number = User.objects.filter(phone_number=phone_number).exists()
        if is_exists_phone_number:
            raise forms.ValidationError('شماره تماس وارد شده از قبل وجود دارد')
        
        return phone_number
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('لطفاً آدرس ایمیل را وارد نمایید')

        is_exists_email = User.objects.filter(email=email).exists()
        if is_exists_email:
            raise forms.ValidationError('کاربری با ایمیل واردشده از قبل ثبت نام کرده است')
        
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


class ChangePassword(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='رمز عبور کنونی'
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='رمز عبور جدید',
        validators=[
            validators.MinLengthValidator(
                limit_value=8,
                message='رمز عبور باید حداقل هشت کاراکتر باشد'
            )
        ]
    )

    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='تأیید رمز عبور جدید'
    )

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not old_password:
            raise forms.ValidationError('لطفاً رمز عبور کنونی خود را وارد نمایید')
        
        return old_password
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if not new_password:
            raise forms.ValidationError('لطفاً رمز عبور جدید خود را وارد نمایید')
        
        return new_password
    
    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_new_password = self.cleaned_data.get('confirm_new_password')
        if not confirm_new_password and new_password:
            raise forms.ValidationError('لطفاً رمز عبور جدید خود تأیید نمایید')
        if new_password and confirm_new_password != new_password:
            raise forms.ValidationError('تأیید رمز عبور جدید با رمز عبور جدید یکسان نیست')
        
        return confirm_new_password


class AccountSettings(forms.Form):
    use_required_attribute = False

    phone_number = forms.CharField(
        widget=forms.TextInput(),
        required=False,
        label='شماره همراه',
        validators=[
            validators.RegexValidator(
                regex=r'09(1[0-9]|3[1-9]|2[1-9])-?[0-9]{3}-?[0-9]{4}',
                message='شماره همراه وارد شده معتبر نمی‌باشد'
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

    address = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label='آدرس'
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError('لطفاً شماره تماس خود را وارد نمایید')
        
        return phone_number
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('لطفاً آدرس ایمیل خود را وارد نمایید')
        
        return email


class CreatePostForm(forms.ModelForm):
    use_required_attribute = False

    title = forms.CharField(
        error_messages={
            'required': 'لطفا برای پست خود عنوانی بنویسید',
        }
    )

    content = forms.CharField(
        widget=CKEditorWidget(),
        error_messages={
            'required': 'شما هنوز برای محتوای پست خود چیزی ننوشته اید', 
        }
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'image']


