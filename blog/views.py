from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, Http404, JsonResponse
from django.db.models import Count, Q, CharField
from django.db.models.functions import Cast
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from account.models import User
from .models import Post, Category, Comment, UserLike, PostVisit
from utils.tools import get_top_cats, get_top_auths, get_user_roles


def index(request: HttpRequest):
    all_cats = Category.objects.all()
    active_users = User.objects.filter(is_active=True).all()
    hot_posts = Post.objects.annotate(num_comments=Count('post_comments')).filter(status='confirm').order_by('-num_comments')[:6]
    fav_posts = Post.objects.filter(status='confirm', like_count__gt=0).order_by('-like_count')[:6]
    recent_posts = Post.objects.filter(status='confirm').order_by('-created_at')[:6]
    
    return render(request, 'blog/index.html', {
        "hot_posts": hot_posts,
        "fav_posts": fav_posts,
        "top_cats": get_top_cats(all_cats),
        "top_auths": get_top_auths(active_users),
        "recent_posts": recent_posts
    })


def blog_footer(request: HttpRequest):
    tags = []
    posts = Post.objects.filter(status='confirm').all()
    for post in posts:
        tags.extend(post.tags)

    return render(request, 'blog/partials/footer.html', {
        "categories": Category.objects.filter(is_subcat=False).all(),
        "tags": tags[:10]
    })


def all_posts(request: HttpRequest):
    posts = Post.objects.filter(status='confirm').order_by('-created_at')

    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if 'show_more' in request.path:
        return render(request, 'blog/components/posts_loop.html', {
            'page_obj': page_obj
        })
    else:
        return render(request, 'blog/all_posts.html', {
            'num_pages': paginator.num_pages,
            'page_obj': page_obj
        })


def all_categories(request: HttpRequest):

    return render(request, 'blog/all_categories.html', {
        "main_cats": Category.objects.filter(is_subcat=False).all()
    })


def category_posts(request: HttpRequest, cat_name):
    cat_posts = []
    cat_obj = get_object_or_404(Category, name=cat_name)
    subcats = cat_obj.subcats.all()

    if cat_obj.is_subcat or not subcats.count():
        cat_posts.extend(cat_obj.cat_posts.filter(status='confirm').all())
    else:
        cat_posts.extend(cat_obj.cat_posts.filter(status='confirm').all())
        cat_posts.extend([post for cat in subcats 
                          for post in cat.cat_posts.filter(status='confirm').all()])
        
    paginator = Paginator(cat_posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if 'show_more' in request.path:
        return render(request, 'blog/components/posts_loop.html', {
            'page_obj': page_obj
        })
    else:
        return render(request, 'blog/category_posts.html', {
            'num_pages': paginator.num_pages,
            "cat_name": cat_obj.name,
            'page_obj': page_obj
        })
        

def author_posts(request: HttpRequest, username):
    user = get_object_or_404(User, username=username)
    auth_posts = Post.objects.filter(status='confirm', author=user)

    paginator = Paginator(auth_posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if 'show_more' in request.path:
        return render(request, 'blog/components/posts_loop.html', {
            'page_obj': page_obj
        })
    else:
        return render(request, 'blog/author_posts.html', {
            'num_pages': paginator.num_pages,
            "auth": user,
            'page_obj': page_obj
        })


def post_detail(request: HttpRequest, slug):
    post = get_object_or_404(Post, slug=slug, status='confirm')
    post_comments = post.post_comments.filter(is_accept=True, is_answer=False).all()
    request.session['next_url'] = request.path
    
    user_ip = request.META.get('REMOTE_ADDR')
    visited = PostVisit.objects.filter(post=post, ip_address=user_ip).exists()
    if not visited:
        PostVisit.objects.create(post=post, ip_address=user_ip)

    return render(request, 'blog/post_detail.html', {
        "post": post,
        "post_comments": post_comments
    })


@login_required
def create_comment(request: HttpRequest, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    has_perm = bool(get_user_roles(user.get_all_permissions()))
    
    if request.method == 'POST':
        message = request.POST.get('message')
        try:
            if has_perm:
                Comment.objects.create(creator=user, post=post, body=message, is_accept=True)
            else:
                Comment.objects.create(creator=user, post=post, body=message)
            return JsonResponse({'success': True, 'has_perm': has_perm})
        except Exception:
            return JsonResponse({'success': False})
    else:
        return Http404()
    

@login_required
def create_answer(request: HttpRequest, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    user = request.user
    has_perm = bool(get_user_roles(user.get_all_permissions()))

    if request.method == 'POST':
        answer = request.POST.get('message')
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, pk=post_id) 
        try:
            if has_perm:
                Comment.objects.create(creator=user, post=post, body=answer, 
                                   is_answer=True, main_comment=comment, is_accept=True)
            else:
                Comment.objects.create(creator=user, post=post, body=answer, 
                                   is_answer=True, main_comment=comment)
            return JsonResponse({'success': True, 'has_perm': has_perm})
        except Exception:
            return JsonResponse({'success': False})
    else:
        return Http404()


def post_like_count(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
        
    return JsonResponse({'success': True, 'like_count': post.like_count})


@login_required
def post_like(request: HttpRequest, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user.is_authenticated:
        user_like, created = UserLike.objects.get_or_create(user=request.user)
        if post not in user_like.posts.all():
            user_like.posts.add(post)
            post.like_count += 1
            post.save()
        else:
            user_like.posts.remove(post)
            post.like_count -= 1
            post.save() 
        
    return JsonResponse({'success': True})


def tag_posts(request: HttpRequest, tag):
    posts_by_tag = []
    posts = Post.objects.filter(status='confirm').all()
    for post in posts:
        if tag in post.tags or tag in post.title or tag in post.category.name:
            posts_by_tag.append(post)

    if posts_by_tag:
        paginator = Paginator(posts_by_tag, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if 'show_more' in request.path:
            return render(request, 'blog/components/posts_loop.html', {
                'page_obj': page_obj
            })
        else:
            return render(request, 'blog/tag_posts.html', {
                'num_pages': paginator.num_pages,
                "tag": tag,
                'page_obj': page_obj
            })
    else:
        return Http404()


def search_posts(request: HttpRequest):
    query = request.GET.get('q')
    page_number = request.GET.get('page')
    posts = Post.objects.filter(status='confirm', is_draft=False).order_by('-created_at')
    # results = posts.filter(
    #         Q(title__icontains=query) | Q(content__icontains=query) |
    #         Q(tags__contains=[query]) | Q(category__name__icontains=query)
    #     )

    # for sqlite db
    results = posts.annotate(tags_text=Cast('tags', CharField())).filter(
            Q(title__icontains=query) | Q(content__icontains=query) |
            Q(tags__icontains=query) | Q(category__name__icontains=query)
        )
    paginator = Paginator(results, 4)
    page_obj = paginator.get_page(page_number)

    if 'show_more' in request.path:
        return render(request, 'blog/components/posts_loop.html', {
            'page_obj': page_obj
        }) 
    else:
        return render(request, 'blog/search_posts.html', {
            'num_pages': paginator.num_pages,
            'query': query,
            'page_obj': page_obj
        })
        

        
