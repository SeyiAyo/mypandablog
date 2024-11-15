from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Category, Comment, Newsletter, PostView

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'post_count')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Number of Posts'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at', 'view_count', 'featured_image_preview')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'slug', 'category', 'status')
        }),
        ('Content', {
            'fields': ('content', 'featured_image', 'tags')
        }),
        ('Meta Information', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def view_count(self, obj):
        return PostView.objects.filter(post=obj).count()
    view_count.short_description = 'Views'
    
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.featured_image.url)
        return "No Image"
    featured_image_preview.short_description = 'Preview'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'email', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'email', 'content')
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    actions = ['approve_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    date_hierarchy = 'created_at'
    list_per_page = 50

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'ip_address')
    date_hierarchy = 'created_at'
    list_per_page = 100
    
    def has_add_permission(self, request):
        return False

admin.site.site_header = 'MyPandaBlog Administration'