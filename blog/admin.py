from django.contrib import admin
from .models import Post, Category, Comment, Newsletter, PostView

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at', 'status']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'intro', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'email', 'created_at', 'is_approved']
    list_filter = ['created_at', 'is_approved']
    search_fields = ['name', 'email', 'contents']
    date_hierarchy = 'created_at'

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'name']

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'ip_address', 'created_at']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    search_fields = ['post__title', 'ip_address']

admin.site.site_header = 'MyPandaBlog Administration'