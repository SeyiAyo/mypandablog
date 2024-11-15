from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager

class Category(models.Model):
    """Category model for organizing blog posts."""
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(db_index=True, unique=True)
    description = models.TextField(blank=True)
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    
    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/category/{self.slug}/"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Post(models.Model):
    """Blog post model with modern features."""
    ACTIVE = 'active'
    DRAFT = 'draft'
    SCHEDULED = 'scheduled'
    
    CHOICES_STATUS = (
        (ACTIVE, 'Active'),
        (DRAFT, 'Draft'),
        (SCHEDULED, 'Scheduled'),
    )
    
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(db_index=True, unique=True)
    category = models.ForeignKey(Category, related_name="posts", on_delete=models.CASCADE)
    author = models.CharField(max_length=255)
    
    intro = RichTextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=DRAFT)
    
    # Media
    image = models.ImageField(upload_to="uploads/", null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    
    # SEO and metadata
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO meta title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    canonical_url = models.URLField(blank=True, help_text="Canonical URL if this is a repost")
    
    # Analytics and engagement
    views_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    bookmarks = models.ManyToManyField(User, related_name="bookmarked_posts", blank=True)
    featured = models.BooleanField(default=False)
    
    # Tags using django-taggit
    tags = TaggableManager(blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['status', 'published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/{self.category.slug}/{self.slug}/"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description:
            self.meta_description = strip_tags(self.intro)[:160] if self.intro else ""
        super().save(*args, **kwargs)
    
    @property
    def reading_time(self):
        """Calculate reading time in minutes based on content length."""
        text = strip_tags(self.content)
        words = len(text.split())
        minutes = round(words / 200)  # Average reading speed of 200 words per minute
        return max(1, minutes)  # Minimum 1 minute reading time
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()

class Comment(models.Model):
    """Enhanced comment model with threading and reactions."""
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="comments", null=True, blank=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    website = models.URLField(blank=True)
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.post.title} - {self.name}'
    
    @property
    def likes_count(self):
        return self.likes.count()

class UserProfile(models.Model):
    """Extended user profile for blog authors and readers."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    github = models.CharField(max_length=50, blank=True)
    linkedin = models.CharField(max_length=50, blank=True)
    email_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username

class Newsletter(models.Model):
    """Newsletter subscription model."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

class PostView(models.Model):
    """Track post views with session/user info."""
    post = models.ForeignKey(Post, related_name='post_views', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='post_views', null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]