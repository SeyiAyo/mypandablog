from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Post, Category, Comment, Newsletter
from .forms import CommentForm, NewsletterForm
from .utils import get_sentiment, recommend_posts
from django.db.models import Count

@cache_page(60 * 15)  # Cache for 15 minutes
def frontpage(request):
    """View for the front page of the blog."""
    featured_posts = Post.objects.filter(status=Post.ACTIVE, featured=True).select_related(
        'category'
    ).order_by('-created_at')[:3]
    
    posts = Post.objects.filter(status=Post.ACTIVE).select_related(
        'category'
    ).prefetch_related(
        Prefetch('comments', Comment.objects.order_by('-created_at'))
    ).order_by('-created_at')
    
    categories = Category.objects.all().annotate(
        post_count=Count('posts', filter=Q(posts__status=Post.ACTIVE))
    )

    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
    }
    
    return render(request, 'frontpage.html', context)

@cache_page(60 * 60 * 24)  # Cache for 24 hours
def about(request):
    """Display the about page."""
    categories = Category.objects.all()
    return render(request, 'about.html', {'categories': categories})

@cache_page(60 * 60 * 24)  # Cache for 24 hours
def contact(request):
    """Display the contact page."""
    categories = Category.objects.all()
    return render(request, 'contact.html', {'categories': categories})

def post_detail(request, category_slug, post_slug):
    """Display a single post with its comments and recommendations."""
    cache_key = f'post_detail_{category_slug}_{post_slug}'
    post = cache.get(cache_key)
    
    if post is None:
        post = get_object_or_404(
            Post.objects.select_related('category').prefetch_related(
                Prefetch('comments', queryset=Comment.objects.select_related('user').order_by('-created_at'))
            ),
            category__slug=category_slug,
            slug=post_slug,
            status=Post.ACTIVE
        )
        cache.set(cache_key, post, 60 * 15)  # Cache for 15 minutes
    
    categories = Category.objects.all()
    form = CommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to comment.')
            return redirect('account_login')
            
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been posted.')
            return redirect('post_detail', category_slug=category_slug, post_slug=post_slug)

    sentiment = get_sentiment(post.content)
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
    """Display posts for a specific category."""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        status=Post.ACTIVE, 
        category=category
    ).select_related('category')
    
    categories = Category.objects.all()
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'posts': posts,
        'categories': categories
    }
    
    return render(request, 'category_detail.html', context)

def search(request):
    """Search posts by query string."""
    query = request.GET.get('query', '')
    
    if query:
        posts = Post.objects.filter(status=Post.ACTIVE).filter(
            Q(title__icontains=query) | 
            Q(intro__icontains=query) |
            Q(content__icontains=query)
        ).select_related('category').distinct()
    else:
        posts = []
        
    categories = Category.objects.all()
    
    return render(request, 'search.html', {
        'query': query, 
        'posts': posts, 
        'categories': categories
    })

@login_required
def profile(request):
    """Display user profile page."""
    # Get user's posts and comments
    user_posts = Post.objects.filter(
        author=request.user,
        status=Post.ACTIVE
    ).select_related('category').order_by('-created_at')
    
    user_comments = Comment.objects.filter(
        user=request.user
    ).select_related('post', 'post__category').order_by('-created_at')
    
    # Pagination for posts
    post_paginator = Paginator(user_posts, 5)
    post_page = request.GET.get('post_page')
    posts = post_paginator.get_page(post_page)
    
    # Pagination for comments
    comment_paginator = Paginator(user_comments, 10)
    comment_page = request.GET.get('comment_page')
    comments = comment_paginator.get_page(comment_page)
    
    context = {
        'user_posts': posts,
        'user_comments': comments,
    }
    
    return render(request, 'account/profile.html', context)

def newsletter_signup(request):
    """Handle newsletter signups."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not Newsletter.objects.filter(email=email).exists():
                form.save()
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            else:
                messages.info(request, 'You are already subscribed to our newsletter.')
        else:
            messages.error(request, 'Please enter a valid email address.')
    
    return redirect(request.META.get('HTTP_REFERER', 'frontpage'))

def privacy_policy(request):
    """Display the privacy policy page."""
    categories = Category.objects.all()
    return render(request, 'privacy_policy.html', {'categories': categories})

def terms_conditions(request):
    """Display the terms and conditions page."""
    categories = Category.objects.all()
    return render(request, 'terms.html', {'categories': categories})

def robots_txt(request):
    """Serve robots.txt file."""
    text = [
        "User-Agent: *",
        "Disallow: /admin/",
        "Sitemap: https://www.mypandablog.com/sitemap.xml"
    ]
    return HttpResponse("\n".join(text), content_type="text/plain")