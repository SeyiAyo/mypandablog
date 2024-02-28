from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Category
from .forms import CommentForm

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
    return render(request, 'contact.html')


def post_detail(request, slug):
    post = Post.objects.get(slug=slug, status=Post.ACTIVE)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        
        if form.is_valid():
            obj = form.save(commit=False)
            obj.post = post
            obj.save()
            
            return redirect('post_detail', slug=post.slug)
    else:        
        form = CommentForm()
    
    context = {
        'post': post,
        'form': form,
        'categories': categories
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