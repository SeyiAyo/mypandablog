from django.shortcuts import render, redirect
from .models import Post, Category
from .forms import CommentForm

def frontpage(request):
    posts = Post.objects.filter(status=Post.ACTIVE)
    
    context = {
        'posts': posts
    }
    
    return render(request, 'frontpage.html', context)


def about(request):
    return render(request, 'about.html')


def post_detail(request, slug):
    post = Post.objects.get(slug=slug, status=Post.ACTIVE)
    
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
        'form': form
    }
    
    return render(request, 'post_detail.html', context)



def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    posts = category.posts.filter(status=Post.ACTIVE)
    
    context = {
        'category': category,
        'posts': posts
    }
    
    return render(request, 'category_detail.html', {'category': category, 'posts': posts})


def search(request):
    query = request.GET.get('query', '')
    
    posts = Post.objects.filter(title__icontains=query)
    
    return render(request, 'search.html', {'query': query, 'posts': posts})