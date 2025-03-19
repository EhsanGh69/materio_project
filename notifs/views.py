from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.utils.html import format_html
from sweetify.views import sweetify
from django.db.models import Q

from blog.models import Post, Comment
from account.models import User
from .models import Notification, Ticket
from utils.tools import get_comment_answers, users_filter, get_codenames, staff_required



@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
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
                subject=f'پست شما با عنوان «{post.title}» توسط ادمین رد شد',
                message=message
            )
        
        return JsonResponse({'success': True, 'redirect_url': reverse("panel:all_posts")})
    else:
        return HttpResponseNotAllowed()


@login_required
@permission_required(get_codenames("posts_manager", True), raise_exception=True)
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
@staff_required
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
            subject=f'پست شما با عنوان «{post.title}» توسط ادمین حذف شد',
            message=message
        )
        post.delete()

        return JsonResponse({'success': True, 'redirect_url': reverse("panel:all_posts")})
    else:
        HttpResponseNotAllowed()


@login_required
@permission_required(get_codenames("comments_manager", True), raise_exception=True)
def all_comments(request: HttpRequest):
    not_accept_mains = Comment.objects.filter(is_accept=False, is_answer=False).order_by('-created_at')
    accept_mains = Comment.objects.filter(is_accept=True, is_answer=False).order_by('-created_at')

    return render(request, 'panel/comments/all_comments.html', {
        'not_accept_mains': not_accept_mains,
        'not_accept_answers': get_comment_answers(accept_mains),
    })


@login_required
@permission_required(get_codenames("comments_manager", True), raise_exception=True)
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
@permission_required(get_codenames("comments_manager", True), raise_exception=True)
def accept_comment(request: HttpRequest, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.is_accept = True
    comment.save()
    sweetify.success(request, "نظر کاربر با موفقیت تایید شد")
    return redirect("notifs:all_comments")


@login_required
@permission_required(get_codenames("comments_manager", True), raise_exception=True)
def remove_comment(request: HttpRequest, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    sweetify.success(request, "نظر کاربر با موفقیت حذف شد")
    return redirect("notifs:all_comments")


@login_required
def persuit_ticket(request: HttpRequest, post_id):
    persuit_post = get_object_or_404(Post, pk=post_id)

    Ticket.objects.create(sender=request.user, 
                          title=f"پیگیری وضعیت پست: «{persuit_post.title}»",
                          body=format_html(f"""
                            <p><i class="text-dark">باسلام</i></p>
                            <p class="text-dark">لطفا پست</p>
                            <p><a style="text-decoration: underline;color: #0067f6;cursor: pointer;"
                                href="{reverse('panel:post_settings', kwargs={'slug': persuit_post.slug})}">
                                «{persuit_post.title}»
                            </a></p>
                            <p class="text-dark">را مورد بررسی قرار دهید</p>
                            """))
    sweetify.success(request, "تیکت پیگیری با موفقیت ارسال شد")
    return redirect("account:my_posts")


@login_required
def my_tickets(request: HttpRequest):
    titckets = Ticket.objects.filter(sender=request.user, isAnswer=False)
    return render(request, 'panel/account/my_tickets.html', {
        "titckets_count": titckets.count(),
        "answered_count": titckets.filter(answered=True).count(),
        "checking_count": titckets.filter(answered=False).count(),
    })


@login_required
def my_tickets_paginate(request: HttpRequest):
    page_number = request.GET.get('page')
    filter = request.GET.get('filter')
    user_tickets = Ticket.objects.filter(sender=request.user, isAnswer=False)
    if filter == 'answered':
        user_tickets = user_tickets.filter(answered=True)
    elif filter == 'checking':
        user_tickets = user_tickets.filter(answered=False)

    page_obj = Paginator(user_tickets, 5).get_page(page_number)
    
    return render(request, 'panel/account/my_tickets_paginate.html', {
        "page_obj": page_obj,
        "answer_tickets": Ticket.objects.filter(isAnswer=True),
        "filter": filter
    })


@login_required
def view_my_ticket(request: HttpRequest, pk):
    if request.user.is_superuser or request.user.has_perms(['notifs.view_ticket', 'notifs.change_ticket']):
        user_ticket = Ticket.objects.filter(id=pk)
    else:
        user_ticket = Ticket.objects.filter(sender=request.user, id=pk)
    post_title = ""

    if user_ticket.exists():
        for post in Post.objects.all():
            if post.title in user_ticket.first().title:
                post_title = post.title
        return render(request, 'panel/account/view_ticket.html', {
            "ticket": user_ticket.first(),
            "answers": Ticket.objects.filter(isAnswer=True),
            "post_title": post_title
        })
    else:
        return redirect("notifs:my_tickets")
    

@login_required
def send_ticket(request: HttpRequest):
    if request.method == 'POST':
        errors = {"title_err": "", "body_err": ""}
        title = request.POST.get('title')
        body = request.POST.get('body')
        if not title:
            errors['title_err'] = "لطفا موضوع تیکت خود را وارد کنید"
        if not body.strip():
            errors['body_err'] = "لطفا متن تیکت خود را وارد کنید"

        if any(errors.values()):
            return JsonResponse({'success': False, 'errors': errors})
        
        Ticket.objects.create(sender=request.user, title=title, body=body.strip())

        return JsonResponse({'success': True, 'redirect_url': reverse("notifs:my_tickets")})
    else:
        HttpResponseNotAllowed()


@login_required
@permission_required(get_codenames("notifs_manager", True), raise_exception=True)
def user_tickets(request: HttpRequest):
    tickets = Ticket.objects.filter(isAnswer=False)
    if not request.user.is_staff:
        tickets = Ticket.objects.exclude(
            Q(sender=request.user) | Q(sender__is_staff=True) | Q(sender__is_active=False)
        ).exclude(sender__in=User.objects.filter( 
            Q(user_permissions__codename="view_post") | Q(user_permissions__codename="change_comment") |
            Q(user_permissions__codename="view_notification")
        ).distinct())
    return render(request, 'panel/notifs/user_tickets.html', {
        'tickets_count': tickets.count(),
        'answered_count': tickets.filter(answered=True).count(),
        'checking_count': tickets.filter(answered=False).count(),
    })


@login_required
@permission_required(get_codenames("notifs_manager", True), raise_exception=True)
def user_tickets_paginate(request: HttpRequest):
    page_number = request.GET.get('page')
    filter = request.GET.get('filter')
    tickets = Ticket.objects.filter(isAnswer=False)

    if filter == 'checking':
        tickets = tickets.filter(answered=False)
    else:
        tickets = tickets.filter(answered=True)

    if not request.user.is_staff:
        tickets = Ticket.objects.exclude(
            Q(sender=request.user) | Q(sender__is_staff=True) | Q(sender__is_active=False)
        ).exclude(sender__in=User.objects.filter( 
            Q(user_permissions__codename="view_post") | Q(user_permissions__codename="change_comment") |
            Q(user_permissions__codename="view_notification")
        ).distinct())

    page_obj = Paginator(tickets, 5).get_page(page_number)

    return render(request, 'panel/notifs/user_tickets_paginate.html', {
        "page_obj": page_obj,
        "answer_tickets": Ticket.objects.filter(isAnswer=True),
        "filter": filter
    })


@login_required
@permission_required(get_codenames("notifs_manager", True), raise_exception=True)
def answer_ticket(request: HttpRequest, pk):
    main_ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        body = request.POST.get('body')
        error = ""
        if not body.strip():
            error = "لطفا پاسخ تیکت را بنویسید"

        if error:
            return JsonResponse({'success': False, 'error': error})
        
        Ticket.objects.create(sender=request.user, title=f"پاسخ# :{main_ticket.title}", body=body.strip(), 
                              isAnswer=True, main=main_ticket)
        main_ticket.answered = True
        main_ticket.save()

        return JsonResponse({'success': True, 'redirect_url': reverse("notifs:user_tickets")})
    else:
        HttpResponseNotAllowed()


@login_required
@permission_required(get_codenames("notifs_manager", True), raise_exception=True)
def remove_ticket(request: HttpRequest, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.delete()
    sweetify.success(request, "تیکت با موفقیت حذف شد")
    return redirect("notifs:user_tickets")


@login_required
def all_notifs(request: HttpRequest):
    if request.user.is_staff:
        notifs = Notification.objects.all()
    elif request.user.has_perms(get_codenames("notifs_manager", True)):
        notifs = Notification.objects.exclude(
            Q(reciever=request.user) | Q(reciever__is_staff=True) | Q(reciever__is_active=False)
        ).exclude(reciever__in=User.objects.filter( 
            Q(user_permissions__codename="view_post") | Q(user_permissions__codename="change_comment") |
            Q(user_permissions__codename="view_notification")
        ).distinct())
    else:
        notifs = Notification.objects.filter(reciever=request.user)
    return render(request, 'panel/notifs/all_notifs.html', {
        'notifs_count': notifs.count(),
        'seen_count': notifs.filter(seen=True).count(),
        'unseen_count': notifs.filter(seen=False).count()
    })


@login_required
def paginate_notifs(request: HttpRequest):
    page_number = request.GET.get('page')
    filter = request.GET.get('filter')
    if request.user.is_staff:
        notifs = Notification.objects.all()
    elif request.user.has_perms(get_codenames("notifs_manager", True)):
        notifs = Notification.objects.exclude(
            Q(reciever=request.user) | Q(reciever__is_staff=True) | Q(reciever__is_active=False)
        ).exclude(reciever__in=User.objects.filter( 
            Q(user_permissions__codename="view_post") | Q(user_permissions__codename="change_comment") |
            Q(user_permissions__codename="view_notification")
        ).distinct())
    else:
        notifs = Notification.objects.filter(reciever=request.user)

    if filter == 'seen':
        notifs = notifs.filter(seen=True)
    else:
        notifs = notifs.filter(seen=False)

    page_obj = Paginator(notifs, 5).get_page(page_number)

    return render(request, 'panel/notifs/all_notifs_paginate.html', {
        'page_obj': page_obj,
        'filter': filter
    })


@login_required
def view_notif(request: HttpRequest, pk):
    if request.user.is_staff:
        user_notif = Notification.objects.filter(id=pk)
    elif request.user.has_perms(get_codenames("notifs_manager", True)):
        notifs = Notification.objects.exclude(
            Q(reciever=request.user) | Q(reciever__is_staff=True) | Q(reciever__is_active=False)
        ).exclude(reciever__in=User.objects.filter( 
            Q(user_permissions__codename="view_post") | Q(user_permissions__codename="change_comment") |
            Q(user_permissions__codename="view_notification")
        ).distinct())
        user_notif = notifs.filter(id=pk)
    else:
        user_notif = Notification.objects.filter(reciever=request.user, id=pk)
        if user_notif.exists():
            notif_obj = user_notif.first()
            notif_obj.seen = True
            notif_obj.save()
    post_slug = ""

    if user_notif.exists():
        for post in Post.objects.all():
            if post.title in user_notif.first().subject:
                post_slug = post.slug
        return render(request, 'panel/notifs/view_notif.html', {
            "notif": user_notif.first(),
            "post_slug": post_slug
        })
    else:
        return redirect("notifs:my_tickets")


@login_required
@permission_required(get_codenames("notifs_manager", True), raise_exception=True)
def send_notif(request: HttpRequest):
    query = request.GET.get('q')
    users = User.objects.filter(is_active=True, is_superuser=False)
    if query:
        recievers = users_filter(users, query)

    if request.method == 'GET':
        return render(request, 'panel/notifs/notif_recievers.html', {
            'recievers': recievers
        })
    else:
        errors = {"reciever_err": "", "subject_err": "", "message_err": ""}
        username = request.POST.get('username')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not username:
            errors['reciever_err'] = "لطفا کاربر دریافت کننده اعلان را انتخاب کنید"
        if not subject:
            errors['subject_err'] = "لطفا موضوع اعلان را وارد کنید"
        if not message.strip():
            errors['message_err'] = "لطفا متن اعلان را بنویسید"

        if any(errors.values()):
            return JsonResponse({'success': False, 'errors': errors})
        
        reciever = users.filter(username=username).first()
        Notification.objects.create(reciever=reciever, subject=subject, message=message.strip())

        sweetify.success(request, "اعلان با موفقیت برای کاربر ارسال شد")
        return JsonResponse({'success': True, 'redirect_url': reverse("notifs:all_notifs")})


@login_required
@permission_required(get_codenames("notifs_manager", True), raise_exception=True)
def remove_notif(request: HttpRequest, pk):
    notif = get_object_or_404(Notification, pk=pk)
    notif.delete()
    sweetify.success(request, "اعلان با موفقیت حذف شد")
    return redirect("notifs:all_notifs")
