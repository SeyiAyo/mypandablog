from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.title
    
class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    category = models.ForeignKey(Category, related_name="posts", on_delete=models.CASCADE)
    
    intro = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '%s - %s' % (self.post.title, self.name)