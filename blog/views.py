from django.shortcuts import render, redirect
from .models import Post, Category
from .forms import CommentForm

def frontpage(request):
    posts = Post.objects.all()
    
    context = {
        'posts': posts
    }
    
    return render(request, 'frontpage.html', context)


def about(request):
    return render(request, 'about.html')

def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    
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
    posts = Post.objects.filter(category=category)
    
    context = {
        'category': category,
        'posts': posts
    }
    
    return render(request, 'category_detail.html', context)