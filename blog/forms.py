from django.forms import ModelForm
from .models import Comment, Post
from .widgets import MarkdownEditorWidget



class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        
        
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'intro', 'content', 'category', 'status', 'image', 'slug']
        widgets = {
            'intro': MarkdownEditorWidget(),
            'content': MarkdownEditorWidget(),
        }