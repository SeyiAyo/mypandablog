from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Category
from .forms import CommentForm
from django.shortcuts import render, get_object_or_404
from .models import Post
from .utils import get_sentiment, recommend_posts
import pandas as pd


def frontpage(request):
    posts = Post.objects.filter(status=Post.ACTIVE)
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


def about(request):
    posts = Post.objects.filter(status=Post.ACTIVE)
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories
    }
    
    return render(request, 'about.html', context)

def contact(request):
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    return render(request, 'contact.html', context)

def privacy_policy(request):
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    return render(request, 'privacy_policy.html', context)

def terms_conditions(request):
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    return render(request, 'terms.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    categories = Category.objects.all()
    
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

    sentiment = get_sentiment(post.content)

    # Create a dataframe of all posts
    posts = Post.objects.all()
    posts_data = [{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'content': p.content,
        'created_at': p.created_at,
        'category': p.category.title if p.category else '',
        'author': p.author,
        'image_url': p.image.url if p.image else ''
    } for p in posts]
    posts_df = pd.DataFrame(posts_data)

    # Get recommendations for the post
    recommendations = recommend_posts(post.id, posts_df)

    # Convert recommended post titles to Post objects
    recommended_posts = Post.objects.filter(title__in=recommendations)

    context = {
        'post': post,
        'categories': categories,
        'form': form,
        'sentiment': sentiment,
        'recommendations': recommended_posts
    }
    return render(request, 'post_detail.html', context)



def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    posts = category.posts.filter(status=Post.ACTIVE)
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
    query = request.GET.get('query', '')
    
    posts = Post.objects.filter(status=Post.ACTIVE).filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(intro__icontains=query))
    categories = Category.objects.all()
    
    return render(request, 'search.html', {'query': query, 'posts': posts, 'categories': categories})


def robots_txt(request):
    text = [
        "User-Agent: *",
        "Disallow: /admin/",
    ]

    return HttpResponse("\n".join(text), content_type="text/plain")