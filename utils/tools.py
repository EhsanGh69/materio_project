import random
import string

from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Permission




def get_codenames(role: str, app_name: bool = False) -> list:
    if role == 'posts_manager':
        if app_name:
            return ['blog.view_post', 'blog.change_post', 'blog.delete_post', 'notifs.add_notification', 
                    'notifs.change_notification']
        return ['view_post', 'change_post', 'delete_post', 'add_notification', 'change_notification']
    elif role == 'comments_manager':
        if app_name:
            return ['blog.change_comment', 'blog.delete_comment']
        return ['change_comment', 'delete_comment']
    elif role == 'notifs_manager':
        if app_name:
            ['notifs.view_notification', 'notifs.add_notification', 'notifs.delete_notification', 
             'notifs.change_ticket', 'notifs.delete_ticket']
        return ['view_notification', 'add_notification', 'delete_notification', 'change_ticket', 'delete_ticket']


def set_user_roles(roles, user):
    if 'admin' in roles:
        user.is_staff = True
        user.save()
        return True
    
    for role in roles:
        code_names = get_codenames(role)
        for code_name in code_names:
            perm_obj = get_object_or_404(Permission, codename=code_name)
            user.user_permissions.add(perm_obj)


def get_user_roles(perms):
    roles = []
    if 'blog.view_post' in perms:
        roles.append('posts_manager')
    if 'blog.change_comment' in perms:
        roles.append('comments_manager')
    if 'notifs.view_notification' in perms:
        roles.append('notifs_manager')
    return roles
        


#* superuser decorator
def superuser_required(func_view):
    decorated_view_func = user_passes_test(
        lambda user: user.is_superuser,
        login_url='account:account_info',
        redirect_field_name=None
    )(func_view)
    return decorated_view_func


#* superuser mixin
class SuperUserRequiredMixin(UserPassesTestMixin):
    login_url = 'account:account_info'

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect(self.login_url)



#* staff decorator
def staff_required(func_view):
    decorated_view_func = user_passes_test(
        lambda user: user.is_staff,
        login_url='account:account_info',
        redirect_field_name=None
    )(func_view)
    return decorated_view_func


#* staff mixin
class StaffRequiredMixin(UserPassesTestMixin):
    login_url = 'account:account_info'

    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        return redirect(self.login_url)


#* generate random string
def random_str(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def none_numeric_value(value):
    try:
        is_numeric = type(int(value)) is int
    except Exception:
        return True
    if is_numeric :
            raise ValidationError("مقدار این فیلد نمی‌تواند عددی می‌باشد", params={"value": value})
    

def password_validation(password, username):
    nums = [str(num) for num in range(0, 10)]
    list_control = []
    chars = {'.', '-', '_', '@'}
    if username is not None and password is not None :
        username_letters = set(username.lower()) - chars
        password_letters = set(password.lower()) - chars
        for char in password:
            if char in nums:
                list_control.append('n')
            else:
                list_control.append('l')
        # checking password combination
        if 'n' not in list_control or 'l' not in list_control:
            return 'combine_err'
        # checking password similarity to username
        elif username_letters.union(password_letters) == username_letters:
            return 'similar_err'
        else:
            return 'not_err'


def img_size_ext_check(imgFile, validSize):
    valid_exts = ['png', 'jpg', 'jpeg', 'gif']
    if imgFile.size > validSize:
        return "اندازه فایل بارگذاری شده بیش از حد مجاز است"
    elif imgFile.name.split('.')[1] not in valid_exts:
        return "فرمت فایل بارگذاری شده غیرمجاز است"
    else:
        return 'valid'


def cache_count_status(status, count):
    if status == 'confirm':
        cache.set('confirm_count', count)
    elif status == 'check':
        cache.set('check_count', count)
    else:
        cache.set('reject_count', count)


def users_filter(users, query):
    return users.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )


def posts_filter(posts, query):
    return posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query) |
            Q(tags__contains=[query]) | Q(category__name__icontains=query) |
            Q(author__username__icontains=query) | Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        )


def search_sort_posts(posts, query=None, field=None):
    global results
    if query and not field:
        results = posts_filter(posts, query)
    elif field and not query:
        results = posts.order_by(field)
    elif field and query:
        results = posts_filter(posts, query).order_by(field)
    
    return results


def get_comment_answers(accept_mains, accept=False):
    not_accept_comment_answers = []
    accept_comment_answers = []
    for main in accept_mains:
        not_accept_answers = []
        accept_answers = []
        if main.answers.exists():
            for answer in main.answers.all():
                if not answer.is_accept:
                    not_accept_answers.append(answer)
                else:
                    accept_answers.append(answer)
            if not_accept_answers:
                not_accept_comment_answers.append({ "main_comment": main, "answers": not_accept_answers })
        accept_comment_answers.append({ "main_comment": main, "answers": accept_answers })
    
    if accept:
        return accept_comment_answers
    else:
        return not_accept_comment_answers
            

