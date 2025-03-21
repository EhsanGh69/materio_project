from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest, JsonResponse
from django.views.generic import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.core.cache import cache
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from sweetify.views import sweetify, SweetifySuccessMixin
from django.db.models import Q, Count

from utils.tools import (
    superuser_required, staff_required, cache_count_status, search_sort_posts, get_codenames,
    set_user_roles, get_user_roles, SuperUserRequiredMixin, StaffRequiredMixin, users_search_filter
)

from account.models import User
from blog.models import Category, Post, Comment
from notifs.models import Notification, Ticket
from account.forms import UserRegister
from .forms import AddCategoryForm, UpdateUserForm


@login_required
@superuser_required
def home(request: HttpRequest):
    users = User.objects.all()
    posts = Post.objects.all()
    comments = Comment.objects.all()
    tickets = Ticket.objects.all()
    hot_post = Post.objects.annotate(num_comments=Count('post_comments')).filter(status='confirm').order_by('-num_comments')
    fav_post = Post.objects.filter(status='confirm', like_count__gt=0).order_by('-like_count')
    visit_post = Post.objects.annotate(num_visits=Count('visits')).filter(status='confirm').order_by('-num_visits')
    return render(request, "panel/home.html", {
        "active_users_count": users.filter(is_active=True, is_superuser=False).count(),
        "inactive_users_count": users.filter(is_active=False).count(),
        "confirm_posts_count": posts.filter(status='confirm').count(),
        "check_posts_count": posts.filter(status='check').count(),
        "notaccept_comments_count": comments.filter(is_accept=False).count(),
        "notanswer_tickets_count": tickets.filter(answered=False).count(),
        "hot_post": hot_post[0] if hot_post else '',
        "fav_post": fav_post[0] if fav_post else '',
        "visit_post": visit_post[0] if visit_post else ''
    })


@login_required
def panel_navbar(request: HttpRequest):
    return render(request, "panel/partials/navbar.html")


@login_required
@superuser_required
def users_list(request: HttpRequest):
    return render(request, "panel/users/users_list.html", {
        'filter_fields': [
            {"value": "admin", "name": "ادمین"},
            {"value": "has_perms", "name": "دارای دسترسی معین"},
            {"value": "normal", "name": "عادی"},
            {"value": "inactive", "name": "غیرفعال"},
        ]
    })


@login_required
@superuser_required
def paginate_users(request: HttpRequest):
    page_number = request.GET.get('page')
    users = User.objects.all().order_by('date_joined')
    page_obj = Paginator(users, 5).get_page(page_number)
    query = request.GET.get('q')
    filter = request.GET.get('filter')
    search_filter = users_search_filter(users, query, filter)
    
    if search_filter:
        page_obj = Paginator(list(set(search_filter)), 5).get_page(page_number)
    elif query or filter and not search_filter:
        page_obj = []

    return render(request, 'panel/users/users_table.html', {
        'page_obj': page_obj,
        'query': query,
        'filter': filter
    })


@login_required
@superuser_required
def user_details(request: HttpRequest, username):
    user = get_object_or_404(User, username=username)
    roles = get_user_roles(user.get_all_permissions())
    
    return render(request, 'panel/users/user_details.html', {
        "user": user,
        "roles": roles
    })


class CreateUser(LoginRequiredMixin, SuperUserRequiredMixin, SweetifySuccessMixin, FormView):
    template_name = 'panel/users/create_user.html'
    form_class = UserRegister
    success_url = reverse_lazy('panel:users')
    success_message = 'کاربر جدید با موفقیت ایجاد شد'

    def form_valid(self, form):
        roles = self.request.POST.getlist('roles')
        c_d = form.cleaned_data
        user = User.objects.create(username=c_d['username'], password=make_password(c_d['password']),
                            phone_number=c_d['phone_number'], email=c_d['email'], 
                            first_name=c_d['first_name'], last_name=c_d['last_name'])
        if roles:
            set_user_roles(roles, user)
        return super().form_valid(form)
    

class UpdateUser(LoginRequiredMixin, SuperUserRequiredMixin, SweetifySuccessMixin, UpdateView):
    template_name = 'panel/users/create_user.html'
    model = User
    form_class = UpdateUserForm
    success_message = "اطلاعات کاربر با موفقیت ویرایش شد"

    def get_success_url(self):
        return reverse_lazy("panel:user_details", kwargs={"username": self.object.username})

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)
    
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        is_exists_email = User.objects.filter(email=email).exclude(pk=self.object.pk).exists()
        if is_exists_email:
            form.add_error('email', 'آدرس ایمیل وارد شده از قبل وجود دارد')
            return super().form_invalid(form)

        roles = self.request.POST.getlist('roles')
        check_roles = set(roles) == set(get_user_roles(self.object.get_all_permissions()))

        self.object.is_staff = False
        self.object.user_permissions.clear()
        self.object.save()
        if roles and not check_roles:
            set_user_roles(roles, self.object)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.is_staff:
            context['user_roles'] = ['admin']
        else:
            context['user_roles'] = get_user_roles(self.object.get_all_permissions())
        return context


@login_required
@superuser_required
def change_status(request: HttpRequest, pk):
    user = get_object_or_404(User, id=pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    sweetify.success(request, "وضعیت کاربر با موفقیت تغییر یافت")
    return JsonResponse({'success': True})
    

@login_required
@superuser_required
def remove_user(request, pk):
    user = get_object_or_404(User, id=pk)
    user.delete()
    sweetify.warning(request, "کاربر با موفقیت حذف شد")
    return redirect("panel:users")


@login_required
@staff_required
def all_categories(request):
    
    return render(request, 'panel/posts/categories.html', {
        'main_cats': Category.objects.filter(is_subcat=False).all()
    })

 
class AddCategory(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Category
    form_class = AddCategoryForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        is_subcat = request.POST.get('is_subcat')
        main = request.POST.get('main')
        if is_subcat and not main:
            form.add_error('main', 'لطفا موضوع اصلی را انتخاب کنید')
        
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        

class EditCategory(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Category
    form_class = AddCategoryForm
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cat_obj = model_to_dict(get_object_or_404(Category, pk=pk))
        return JsonResponse(cat_obj)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        name = request.POST.get('name')
        is_subcat = True if request.POST.get('is_subcat') == 'true' else False
        main = request.POST.get('main')
        if is_subcat and not main:
            form.add_error('main', 'لطفا موضوع اصلی را انتخاب کنید')

        if form.is_valid():
            pk = kwargs.get('pk')
            cat_obj = get_object_or_404(Category, pk=pk)
            cat_obj.name = name
            cat_obj.is_subcat = is_subcat
            if main != '': cat_obj.main = get_object_or_404(Category, pk=int(main))
            cat_obj.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        

@login_required
@staff_required
def remove_category(request, pk):
    cat_obj = get_object_or_404(Category, id=pk)
    cat_obj.delete()
    sweetify.warning(request, "موضوع با موفقیت حذف شد")
    return redirect("panel:all_cats")


@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
def all_posts(request: HttpRequest):
    posts = Post.objects.filter(is_draft=False).order_by('-created_at')
    
    if 'status_count' in request.path:
        return JsonResponse({
            'confirm_count': cache.get('confirm_count', posts.filter(status='confirm').count()),
            'check_count': cache.get('check_count', posts.filter(status='check').count()),
            'reject_count': cache.get('reject_count', posts.filter(status='reject').count()),
        }) 

    return render(request, 'panel/posts/all_posts.html', {
        'sort_fields': [
            {"value": "title", "name": "عنوان"},
            {"value": "author", "name": "نویسنده"},
            {"value": "category", "name": "موضوع"},
            {"value": "-confirm_date", "name": "تاریخ تایید"}
        ]
    }) 
        
    
@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
def paginate_posts(request: HttpRequest):
    status = request.GET.get('status')
    page_number = request.GET.get('page')
    posts = Post.objects.filter(status=status, is_draft=False).order_by('-created_at')
    if not request.user.is_staff:
        posts = Post.objects.filter(status=status, is_draft=False).exclude(
            Q(author=request.user) | Q(author__is_staff=True) | Q(author__is_active=False)
        ).exclude(author__in=User.objects.filter( 
            Q(user_permissions__codename="view_post") | Q(user_permissions__codename="change_comment") |
            Q(user_permissions__codename="view_notification")
        ).distinct())
        
    page_obj = Paginator(posts, 5).get_page(page_number)
    cache_count_status(status, posts.count())
    query = ''
    field = ''

    if 'search_sort' in request.path:
        query = request.GET.get('q')
        field = request.GET.get('field')
        results = search_sort_posts(posts, query, field)
        page_obj = Paginator(results, 5).get_page(page_number)
        cache_count_status(status, results.count())

    return render(request, 'panel/partials/posts_table.html', {
        'page_obj': page_obj,
        'status': status,
        'query': query,
        'field': field,
        'notifs': Notification.objects.all()
    })


@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
def view_post(request: HttpRequest, slug):
    post = get_object_or_404(Post, slug=slug)

    return render(request, 'panel/posts/view_post.html', {
        'post': post,
        'notifs': Notification.objects.all()
    })


@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
def post_settings(request: HttpRequest, slug):
    post = get_object_or_404(Post, slug=slug)
    main_cats = Category.objects.filter(is_subcat=False)

    if request.method == 'POST':
        errors = {"main_cat_err": "", "study_time_err": ""}
        main_cat = request.POST.get('main_cat')
        sub_cat = request.POST.get('sub_cat')
        study_time = request.POST.get('study_time')
        if not main_cat:
            errors['main_cat_err'] = "لطفا موضوع اصلی را انتخاب کنید"
        try:
            study_time = int(study_time)
            if study_time <= 0:
                errors['study_time_err'] = "مدت زمان مطالعه باید عددی مثبت و بزرگتر از صفر باشد"
        except (ValueError, TypeError):
            errors['study_time_err'] = "مدت زمان مطالعه باید مقداری عددی باشد"

        if any(errors.values()):
            return JsonResponse({'success': False, 'errors': errors})
        
        if sub_cat:
            sub_obj = get_object_or_404(Category, pk=sub_cat)
            post.category = sub_obj
        else:
            main_obj = get_object_or_404(Category, pk=main_cat)
            post.category = main_obj

        post_status = post.status
        
        post.study_time = study_time
        post.status = 'confirm'
        post.confirm_date = timezone.now()
        post.save()

        extra_notifs = Notification.objects.filter(reciever=post.author, 
                                                  subject__icontains=f'{post.title}')
        if extra_notifs:
            for obj in extra_notifs:
                obj.delete()

        if post.author.is_staff:
            post.is_draft = False
            post.save()

        if post_status == 'confirm':
            sweetify.success(request, "تغییرات با موفقیت ذخیره شد")
        else:
            sweetify.success(request, "پست با موفقیت منتشر شد")
        return JsonResponse({'success': True, 'redirect_url': reverse("panel:view_post", args=[post.slug])})
    else:
        return render(request, 'panel/posts/post_settings.html', {
            'post': post,
            'main_cats': main_cats
        })
    

@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
def get_sub_cats(request: HttpRequest, cat_id):
    sub_cats = get_object_or_404(Category, pk=cat_id).subcats.all().values("id", "name")
    
    return JsonResponse(list(sub_cats), safe=False)


@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
def get_related_tags(request: HttpRequest, cat_id):
    main_cat = get_object_or_404(Category, pk=cat_id)
    posts = Post.objects.filter(category=main_cat, status='confirm')
    tags = [tag for post in posts for tag in post.tags ]
    
    return JsonResponse(tags, safe=False)


@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
def post_tags(request: HttpRequest, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        tag_name = request.POST.get('tag_name')
        if not tag_name:
            return JsonResponse({'success': False, 'error': 'لطفا نام تگ را وارد نمایید'})
        
        if 'edit' in request.path:
            prev_tag = request.POST.get('prev_tag')
            tag_index = post.tags.index(prev_tag)
            post.tags[tag_index] = tag_name.strip().replace(' ', '_')
            post.save()
        else:
            post.tags.append(tag_name.strip().replace(' ', '_'))
            post.save()
        return JsonResponse({'success': True})
    else:
        tag_name = request.GET.get('tag_name')
        post.tags.remove(tag_name.strip())
        post.save()
        return JsonResponse({'success': True})
