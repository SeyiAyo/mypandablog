from django.contrib import admin
from .models import Post, Category, Comment, Recommendation
from .forms import PostForm



class CommentItemInline(admin.TabularInline):
    model = Comment
    raw_id_fields = ['post']



class PostAdmin(admin.ModelAdmin):
    search_fields = ['title', 'intro', 'content']
    list_display = ['title', 'slug', 'category', 'created_at', 'updated_at', 'status']
    list_filter = ['category', 'created_at', 'status']
    inlines = [CommentItemInline]
    prepopulated_fields = {'slug': ('title',)}
    form = PostForm
    
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['post', 'recommended_post']    
    
    
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title']
    prepopulated_fields = {'slug': ('title',)}
    
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'created_at']

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.site_header = 'MyPandaBlog Administration'
admin.site.register(Comment, CommentAdmin)
admin.site.register(Recommendation, RecommendationAdmin)