from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest, JsonResponse
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms.models import model_to_dict
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from sweetify.views import sweetify

from utils.tools import superuser_required, cache_count_status, search_sort_posts

from account.models import User
from blog.models import Category, Post
from notifs.models import Notification
from .forms import AddCategoryForm


@login_required
@superuser_required
def home(request: HttpRequest):
    return render(request, "panel/home.html")


@login_required
@superuser_required
def users_list(request):
    return render(request, "panel/users/users_list.html", {
        "users": User.objects.all()
    })


@login_required
def panel_navbar(request):
    user_avatar = request.user.user_avatar.avatar.url
    return render(request, "panel/partials/navbar.html", { "user_avatar": user_avatar })


@login_required
@superuser_required
def change_status(request: HttpRequest, pk):
    user = get_object_or_404(User, id=pk)
    target_url = request.GET.get('target_url')
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    sweetify.success(request, "وضعیت کاربر با موفقیت تغییر یافت")

    if(target_url):
        return JsonResponse({'success': True})
    return redirect("panel:users")


@login_required
@superuser_required
def remove_user(request, pk):
    user = get_object_or_404(User, id=pk)
    user.delete()
    sweetify.warning(request, "کاربر با موفقیت حذف شد")
    return redirect("panel:users")


@login_required
@superuser_required
def change_access(request, pk):
    user = get_object_or_404(User, id=pk)
    if user.is_staff:
        user.is_staff = False
    else:
        user.is_staff = True
    user.save()
    sweetify.info(request, "سطح دسترسی کاربر با موفقیت تغییر یافت")
    return redirect("panel:users")


@login_required
@permission_required("blog.view_category", raise_exception=True)
def all_categories(request):
    
    return render(request, 'panel/posts/categories.html', {
        'main_cats': Category.objects.filter(is_subcat=False).all()
    })


class AddCategory(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "blog.add_category"
    raise_exception = True
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
        

class EditCategory(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "blog.change_category"
    raise_exception = True
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
@permission_required('blog.delete_category', raise_exception=True)
def remove_category(request, pk):
    cat_obj = get_object_or_404(Category, id=pk)
    cat_obj.delete()
    sweetify.warning(request, "موضوع با موفقیت حذف شد")
    return redirect("panel:all_cats")


@login_required
@permission_required('blog.view_post', raise_exception=True)
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
            {"value": "author", "name": "نام نویسنده"},
            {"value": "category", "name": "موضوع"}
        ]
    }) 
        
    
@login_required
@permission_required('blog.view_post', raise_exception=True)
def paginate_posts(request: HttpRequest):
    status = request.GET.get('status')
    page_number = request.GET.get('page')
    posts = Post.objects.filter(status=status, is_draft=False).order_by('-created_at')
    page_obj = Paginator(posts, 5).get_page(page_number)
    cache_count_status(status, posts.count())
    query = ''
    field = ''

    if 'search_sort' in request.path:
        query = request.GET.get('q')
        field = request.GET.get('field')
        results = search_sort_posts(posts, query, field)
        page_obj = Paginator(results, 2).get_page(page_number)
        cache_count_status(status, results.count())

    return render(request, 'panel/partials/posts_table.html', {
        'page_obj': page_obj,
        'status': status,
        'query': query,
        'field': field
    })


@login_required
@permission_required(['blog.view_post', 'blog.delete_post'], raise_exception=True)
def view_post(request: HttpRequest, slug):
    post = get_object_or_404(Post, slug=slug)

    return render(request, 'panel/posts/view_post.html', {
        'post': post
    })


@login_required
@permission_required(
    ['blog.view_post', 'blog.delete_post', 'blog.change_post'], raise_exception=True)
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
        
        post.study_time = study_time
        post.status = 'confirm'
        post.confirm_date = timezone.now()
        post.save()

        extra_notifs = Notification.objects.filter(reciever=post.author, 
                                                  subject__icontains=f'{post.title}')
        if extra_notifs:
            for obj in extra_notifs:
                obj.delete()
        sweetify.success(request, "پست با موفقیت تایید شد")
        return JsonResponse({'success': True, 'redirect_url': reverse("panel:view_post", args=[post.slug])})
    else:
        return render(request, 'panel/posts/post_settings.html', {
            'post': post,
            'main_cats': main_cats
        })
    

@login_required
@permission_required(
    ['blog.view_post', 'blog.change_post', 'blog.view_category'],
        raise_exception=True)
def get_sub_cats(request: HttpRequest, cat_id):
    sub_cats = get_object_or_404(Category, pk=cat_id).subcats.all().values("id", "name")
    
    return JsonResponse(list(sub_cats), safe=False)


@login_required
@permission_required(
    ['blog.view_post', 'blog.change_post'],
        raise_exception=True)
def get_related_tags(request: HttpRequest, cat_id):
    main_cat = get_object_or_404(Category, pk=cat_id)
    posts = Post.objects.filter(category=main_cat, status='confirm')
    tags = [tag for post in posts for tag in post.tags ]
    
    return JsonResponse(tags, safe=False)


@login_required
@permission_required(
    ['blog.view_post', 'blog.change_post'],
        raise_exception=True)
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

