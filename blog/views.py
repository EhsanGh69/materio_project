from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest
from django.db.models import Count

from account.models import User
from .models import Post, Category


def index(request: HttpRequest):
    top_cats = Category.objects.annotate(num_posts=Count('cat_posts')).order_by('-num_posts')[:9]
    top_auths = User.objects.annotate(num_posts=Count('user_posts')).order_by('-num_posts')[:9]

    return render(request, 'blog/index.html', {
        "posts": Post.objects.all(),
        "fav_posts": Post.objects.all(),
        "top_cats": top_cats,
        "top_auths": top_auths
    })


def blog_footer(request: HttpRequest):
    tags = []
    posts = Post.objects.all()
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
        cat_posts.extend(cat_obj.cat_posts.all())
    else:
        cat_posts.extend(cat_obj.cat_posts.all())
        cat_posts.extend([post for cat in subcats for post in cat.cat_posts.all()])

    return render(request, 'blog/category_posts.html', {
        "cat_name": cat_name,
        "cat_posts": cat_posts
    })
