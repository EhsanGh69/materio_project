from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest, JsonResponse
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms.models import model_to_dict
from django.db.models import Q
from django.core.paginator import Paginator
from sweetify.views import sweetify

from utils.tools import superuser_required

from account.models import User
from blog.models import Category, Post
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
def change_status(request, pk):
    user = get_object_or_404(User, id=pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    sweetify.success(request, "وضعیت کاربر با موفقیت تغییر یافت")
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
@permission_required("blog.view_category")
def all_categories(request):
    
    return render(request, 'panel/posts/categories.html', {
        'main_cats': Category.objects.filter(is_subcat=False).all()
    })


class AddCategory(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "blog.add_category"
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
@permission_required('blog.delete_category')
def remove_category(request, pk):
    cat_obj = get_object_or_404(Category, id=pk)
    cat_obj.delete()
    sweetify.warning(request, "موضوع با موفقیت حذف شد")
    return redirect("panel:all_cats")


@login_required
@permission_required('blog.view_post')
def all_posts(request: HttpRequest):
    posts = Post.objects.all()
    return render(request, 'panel/posts/all_posts.html', {
        'confirm_count': posts.filter(status='confirm').count(),
        'check_count': posts.filter(status='check').count(),
        'reject_count': posts.filter(status='reject').count()
    }) 
        
    
@login_required
@permission_required('blog.view_post')
def paginate_posts(request: HttpRequest):
    status = request.GET.get('status')
    page_number = request.GET.get('page')
    posts = Post.objects.filter(status=status)
    page_obj = Paginator(posts, 5).get_page(page_number)

    return render(request, 'panel/partials/posts_table.html', {
        'page_obj': page_obj,
        'status': status
    })



@login_required
@permission_required('blog.delete_post')
def remove_post(request: HttpRequest, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    sweetify.warning(request, "پست با موفقیت حذف شد")
    return redirect("panel:all_posts")


# @login_required
# @permission_required('blog.view_post')
# def view_post(request: HttpRequest, pk):
#     post = get_object_or_404(Post, pk=pk)
    
#     sweetify.warning(request, "پست با موفقیت حذف شد")
#     return redirect("panel:all_posts")




