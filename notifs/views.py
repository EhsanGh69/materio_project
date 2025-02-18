from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from sweetify.views import sweetify

from blog.models import Post, Comment
from .models import Notification
from utils.tools import get_comment_answers



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
        return HttpResponseNotAllowed()


def edit_reject_notif(request: HttpRequest, pk):
    notif = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        message = request.POST.get('message')
        post_slug = request.POST.get('post_slug')
        if not message:
            return JsonResponse({'success': False, 'error': "لطفا متن پیام را بنویسید"})
        if not post_slug:
            return HttpResponseBadRequest()
        notif.message = message
        notif.save()
        return JsonResponse({'success': True, 'redirect_url': reverse("panel:view_post", args=[post_slug])})
    else:
        return JsonResponse({'success': True, 'notif': model_to_dict(notif)})


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


@login_required
@permission_required(['blog.view_comment', 'blog.change_comment', 'blog.delete_comment'], raise_exception=True)
def all_comments(request: HttpRequest):
    not_accept_mains = Comment.objects.filter(is_accept=False, is_answer=False).order_by('-created_at')
    accept_mains = Comment.objects.filter(is_accept=True, is_answer=False).order_by('-created_at')

    return render(request, 'panel/comments/all_comments.html', {
        'not_accept_mains': not_accept_mains,
        'not_accept_answers': get_comment_answers(accept_mains),
    })


@login_required
@permission_required('blog.view_comment', raise_exception=True)
def paginate_comments(request: HttpRequest):
    page_number = request.GET.get('page')
    accept_mains = Comment.objects.filter(is_accept=True, is_answer=False).order_by('-created_at')
    accept_comments = get_comment_answers(accept_mains, True)
    page_obj = Paginator(accept_comments, 6).get_page(page_number)
    query = request.GET.get('q')
    
    if query:
        query = request.GET.get('q')
        results = []
        for item in accept_comments:
            creator = item['main_comment'].creator
            creator_check = query in creator.first_name or query in creator.last_name
            post = item['main_comment'].post
            post_check = query in post.title or query in post.category.name
            if creator_check or post_check:
                results.append(item)
        page_obj = Paginator(results, 6).get_page(page_number)

    
    return render(request, 'panel/comments/accept_comments.html', { 
        'page_obj': page_obj,
        'query': query
    })


@login_required
@permission_required('blog.change_comment', raise_exception=True)
def accept_comment(request: HttpRequest, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.is_accept = True
    comment.save()
    sweetify.success(request, "نظر کاربر با موفقیت تایید شد")
    return redirect("notifs:all_comments")


@login_required
@permission_required('blog.delete_comment', raise_exception=True)
def remove_comment(request: HttpRequest, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    sweetify.success(request, "نظر کاربر با موفقیت حذف شد")
    return redirect("notifs:all_comments")


