from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from blog.models import Post
from .models import Notification



@login_required
@permission_required(['blog.change_post', 'notifs.add_notification'], raise_exception=True)
def post_reject(request: HttpRequest, pk):
    if request.method == 'POST':
        message = request.POST.get('message')

        if not message:
            return JsonResponse({'success': False, 'error': "لطفا علت رد کردن این پست را بنویسید"})

        post = get_object_or_404(Post, pk=pk)
        post.status = 'reject'
        post.save()

        Notification.objects.create(
                reciever=post.author,
                subject=f'رد پست با عنوان: {post.title}',
                message=message
            )
        
        return JsonResponse({'success': True, 'redirect_url': reverse("panel:all_posts")})
    else:
        HttpResponseNotAllowed()



@login_required
@permission_required(['blog.delete_post', 'notifs.add_notification'], raise_exception=True)
def remove_post(request: HttpRequest, pk):
    if request.method == 'POST':
        message = request.POST.get('message')

        if not message:
            return JsonResponse({'success': False, 'error': "لطفا علت حذف این پست را بنویسید"})

        post = get_object_or_404(Post, pk=pk)
        extra_notifs = Notification.objects.filter(reciever=post.author, 
                                                  subject__icontains=f'{post.title}')
        if extra_notifs:
            for obj in extra_notifs:
                obj.delete()

        Notification.objects.create(
            reciever=post.author,
            subject=f'حذف پست با عنوان: {post.title}',
            message=message
        )
        post.delete()

        return JsonResponse({'success': True, 'redirect_url': reverse("panel:all_posts")})
    else:
        HttpResponseNotAllowed()






