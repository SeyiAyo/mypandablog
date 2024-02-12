from django.forms import ModelForm
from .models import Comment, Post
from .widgets import MarkdownEditorWidget
from django import forms


class CommentForm(ModelForm):
    #contents = forms.CharField(widget=forms.Textarea(attrs={'id': 'id_content', 'rows': '10', 'cols': '40', 'placeholder': 'Write a comment...', 'class': 'form-control'}))
    class Meta:
        model = Comment
        fields = ['name', 'email', 'contents']
        
        
        
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'intro', 'content', 'category', 'status', 'image', 'slug']
        widgets = {
            'intro': MarkdownEditorWidget(),
            'content': MarkdownEditorWidget(),
        }