from django.forms import ModelForm
from .models import Comment, Post, Newsletter
from django import forms


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'contents']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Your email'
            }),
            'contents': forms.Textarea(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Your comment',
                'rows': 4
            })
        }
        
        
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'intro', 'content', 'category', 'status', 'image', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }),
            'intro': forms.Textarea(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500',
                'rows': 3
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            })
        }


class NewsletterForm(forms.ModelForm):
    """Form for newsletter subscriptions."""
    class Meta:
        model = Newsletter
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Your email address'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Your name (optional)'
            })
        }