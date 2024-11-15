from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Category, Comment
from .forms import CommentForm
from django.shortcuts import render, get_object_or_404
from .models import Post
from .utils import get_sentiment, recommend_posts
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch

@cache_page(60 * 15)  # Cache for 15 minutes
def frontpage(request):
    """Display the blog's front page with paginated posts."""
    posts = Post.objects.filter(status=Post.ACTIVE).select_related('category').prefetch_related(
        Prefetch('comments', Comment.objects.order_by('-created_at'), to_attr='recent_comments')
    )
    
    # Limit recent comments to 5 per post
    for post in posts:
        post.recent_comments = post.recent_comments[:5]
        
    categories = Category.objects.all()
    
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    try:
        post = paginator.page(page)
    except PageNotAnInteger:
        post = paginator.page(1)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)
        
    context = {
        'posts': post,
        'categories': categories
    }
    
    return render(request, 'frontpage.html', context)


@cache_page(60 * 60 * 24)  # Cache for 24 hours
def about(request):
    """Display the about page."""
    posts = Post.objects.filter(status=Post.ACTIVE)
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories
    }
    
    return render(request, 'about.html', context)

@cache_page(60 * 60 * 24)  # Cache for 24 hours
def contact(request):
    """Display the contact page."""
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    return render(request, 'contact.html', context)

@cache_page(60 * 60 * 24)  # Cache for 24 hours
def privacy_policy(request):
    """Display the privacy policy page."""
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    return render(request, 'privacy_policy.html', context)

@cache_page(60 * 60 * 24)  # Cache for 24 hours
def terms_conditions(request):
    """Display the terms and conditions page."""
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    return render(request, 'terms.html', context)

def post_detail(request, slug):
    """
    Display a single post with its comments and recommendations.
    
    Args:
        request: HTTP request object
        slug: URL slug of the post
        
    Returns:
        Rendered post detail template with post data and form
    """
    cache_key = f'post_detail_{slug}'
    post = cache.get(cache_key)
    
    if post is None:
        post = get_object_or_404(
            Post.objects.select_related('category').prefetch_related(
                Prefetch('comments', queryset=Comment.objects.order_by('-created_at'))
            ),
            slug=slug
        )
        cache.set(cache_key, post, 60 * 15)  # Cache for 15 minutes
    categories = Category.objects.all()
    
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

    sentiment = get_sentiment(post.content)
    
    # Get recommendations using the updated recommend_posts function
    recommended_posts = recommend_posts(post)

    context = {
        'post': post,
        'categories': categories,
        'form': form,
        'sentiment': sentiment,
        'recommendations': recommended_posts
    }
    return render(request, 'post_detail.html', context)



def category_detail(request, slug):
    """
    Display posts for a specific category.
    
    Args:
        request: HTTP request object
        slug: URL slug of the category
        
    Returns:
        Rendered category detail template with filtered posts
    """
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(status=Post.ACTIVE, category=category).select_related('category')
    categories = Category.objects.all()
    
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    try:
        post = paginator.page(page)
    except PageNotAnInteger:
        post = paginator.page(1)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'posts': post,
        'categories': categories
    }
    
    return render(request, 'category_detail.html', context)


def search(request):
    """
    Search posts by query string.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered search results template
    """
    query = request.GET.get('query', '')
    
    posts = Post.objects.filter(status=Post.ACTIVE).filter(
        Q(title__icontains=query) | 
        Q(intro__icontains=query) |
        Q(content__icontains=query)
    ).select_related('category').distinct()
    categories = Category.objects.all()
    
    return render(request, 'search.html', {'query': query, 'posts': posts, 'categories': categories})


def robots_txt(request):
    text = [
        "User-Agent: *",
        "Disallow: /admin/",
    ]

    return HttpResponse("\n".join(text), content_type="text/plain")