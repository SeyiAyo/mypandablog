from django.forms import ModelForm
from .models import Comment, Post, Newsletter
from django import forms
from allauth.account.forms import SignupForm, LoginForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'contents']
        
        
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'intro', 'content', 'category', 'status', 'image', 'slug']


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


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes and placeholders to form fields
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Choose a username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Your email address'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Confirm password'
        })

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password)
        except ValidationError as error:
            self.add_error('password1', error)
        return password


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes and placeholders to form fields
        self.fields['login'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Username or email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Password'
        })
        if 'remember' in self.fields:
            self.fields['remember'].widget.attrs.update({
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes and placeholders to form fields
        self.fields['email'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter your email address'
        })