from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from sweetify.views import sweetify

from account.models import User


@login_required
def home(request):
    user_avatar = request.user.user_avatar
    print(user_avatar.avatar.url)
    return render(request, "home.html", {
        "users": User.objects.all()
    })

@login_required
def panel_navbar(request):
    user_avatar = request.user.user_avatar.avatar.url

    return render(request, "partials/navbar.html", { "user_avatar": user_avatar })

@login_required
def change_status(request, pk):
    user = get_object_or_404(User, id=pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    sweetify.success(request, "وضعیت کاربر با موفقیت تغییر یافت")
    return redirect("panel:home")


@login_required
def remove_user(request, pk):
    user = get_object_or_404(User, id=pk)
    user.delete()
    sweetify.warning(request, "کاربر با موفقیت حذف شد")
    return redirect("panel:home")


@login_required
def change_access(request, pk):
    user = get_object_or_404(User, id=pk)
    if user.is_staff:
        user.is_staff = False
    else:
        user.is_staff = True
    user.save()
    sweetify.info(request, "سطح دسترسی کاربر با موفقیت تغییر یافت")
    return redirect("panel:home")


