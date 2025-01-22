from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, Http404, JsonResponse
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from account.models import User
from .models import Post, Category, Comment, UserLike


def index(request: HttpRequest):
    top_cats = Category.objects.annotate(num_posts=Count('cat_posts')).order_by('-num_posts')[:9]
    top_auths = User.objects.annotate(num_posts=Count('user_posts')).order_by('-num_posts')[:9]
    hot_posts = Post.objects.annotate(num_comments=Count('post_comments')).order_by('-num_comments')[:6]
    fav_posts = Post.objects.order_by('-like_count')[:6]
    
    return render(request, 'blog/index.html', {
        "hot_posts": hot_posts,
        "fav_posts": fav_posts,
        "top_cats": top_cats,
        "top_auths": top_auths
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

    return render(request, 'blog/category_posts.html', {
        "cat_name": cat_obj.name,
        "cat_posts": cat_posts
    })


def author_posts(request: HttpRequest, username):
    user = get_object_or_404(User, username=username)
    
    return render(request, 'blog/author_posts.html', {
        "auth": user,
        "auth_posts": Post.objects.filter(status='confirm', author=user)
    })


def post_detail(request: HttpRequest, slug):
    post = get_object_or_404(Post, slug=slug, status='confirm')
    post_comments = post.post_comments.filter(is_accept=True, is_answer=False).all()
    request.session['next_url'] = request.path
    return render(request, 'blog/post_detail.html', {
        "post": post,
        "post_comments": post_comments
    })


@login_required
def create_comment(request: HttpRequest, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        try:
            Comment.objects.create(creator=request.user, post=post, body=message)
            return JsonResponse({'success': True})
        except Exception:
            return JsonResponse({'success': False})
    else:
        return Http404()
    

@login_required
def create_answer(request: HttpRequest, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == 'POST':
        answer = request.POST.get('message')
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, pk=post_id) 
        try:
            Comment.objects.create(creator=request.user, post=post, body=answer, 
                                   is_answer=True, main_comment=comment)
            return JsonResponse({'success': True})
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
        return render(request, 'blog/tag_posts.html', {
            "tag": tag,
            "tag_posts": posts_by_tag
        })
    else:
        return Http404()


def search_posts(request: HttpRequest):
    query = request.GET.get('q')
    results = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query) |
            Q(tags__contains=[query]) | Q(category__name__icontains=query)
        )
    paginator = Paginator(results, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if 'search' in request.path:
        return render(request, 'blog/search_posts.html', {
            'num_pages': paginator.num_pages,
            'query': query,
            'page_obj': page_obj
        })
    else:
        return render(request, 'blog/components/posts_loop.html', {
            'page_obj': page_obj
        }) 

        
