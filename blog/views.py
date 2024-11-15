from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Prefetch
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
    return render(request, 'about.html')

def contact(request):
    """Display the contact page."""
    return render(request, 'contact.html')

def post_detail(request, category_slug, post_slug):
    """Display a single post with its comments and recommendations."""
    post = get_object_or_404(Post.objects.select_related('category'), 
                            category__slug=category_slug,
                            slug=post_slug,
                            status=Post.ACTIVE)
    
    # Get post comments
    comments = post.comments.all().order_by('-created_at')
    
    # Handle comment form submission
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            
            # Get sentiment of comment
            sentiment = get_sentiment(comment.contents)
            comment.sentiment = sentiment
            
            comment.save()
            messages.success(request, 'Your comment has been posted.')
            return redirect('post_detail', category_slug=category_slug, post_slug=post_slug)
    else:
        form = CommentForm()
    
    # Get recommended posts
    recommended_posts = recommend_posts(post)
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'recommended_posts': recommended_posts
    }
    
    return render(request, 'post_detail.html', context)

def category_detail(request, slug):
    """Display posts for a specific category."""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status=Post.ACTIVE).select_related(
        'category'
    ).prefetch_related(
        Prefetch('comments', Comment.objects.order_by('-created_at'))
    ).order_by('-created_at')
    
    # Get all categories for sidebar
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
    
    return render(request, 'category_detail.html', {
        'category': category,
        'posts': posts,
        'categories': categories
    })

def search(request):
    """Search posts by query string."""
    query = request.GET.get('query', '')
    posts = Post.objects.filter(status=Post.ACTIVE).select_related('category')
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(intro__icontains=query) |
            Q(content__icontains=query)
        )
    
    # Get all categories for sidebar
    categories = Category.objects.all().annotate(
        post_count=Count('posts', filter=Q(posts__status=Post.ACTIVE))
    )
    
    return render(request, 'search.html', {
        'query': query, 
        'posts': posts, 
        'categories': categories
    })

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
    return render(request, 'privacy_policy.html')

def terms_conditions(request):
    """Display the terms and conditions page."""
    return render(request, 'terms_conditions.html')

def robots_txt(request):
    """Serve robots.txt file."""
    content = """
    User-agent: *
    Disallow: /admin/
    Disallow: /search/
    Allow: /
    """
    return HttpResponse(content, content_type='text/plain')