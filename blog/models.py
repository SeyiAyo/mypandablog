from django.db import models
from ckeditor.fields import RichTextField

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    
    class Meta:
        ordering = ["title",]
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/%s/' % self.slug
    
    
class Post(models.Model):
    ACTIVE = 'active'
    DRAFT = 'draft'
    
    CHOICES_STATUS = (
        (ACTIVE, 'Active'),
        (DRAFT, 'Draft'),
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    category = models.ForeignKey(Category, related_name="posts", on_delete=models.CASCADE)
    author = models.CharField(max_length=255, default="Sensei Panda")
    
    # intro = models.TextField()
    intro = RichTextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    # content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=ACTIVE)
    image = models.ImageField(upload_to="uploads/", null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at",]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/%s/%s/' % (self.category.slug, self.slug)
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(default="")
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '%s - %s' % (self.post.title, self.name)
    
    class Meta:
        ordering = ["-created_at",]