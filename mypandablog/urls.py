"""
URL configuration for mypandablog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from blog.views import (
    frontpage, about, contact, post_detail, category_detail, search,
    privacy_policy, terms_conditions, robots_txt, newsletter_signup
)

from blog.sitemaps import PostSitemap, CategorySitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap
}

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Blog pages
    path('', frontpage, name='frontpage'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('search/', search, name='search'),
    
    # Legal pages
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', terms_conditions, name='terms_conditions'),
    
    # Blog content
    path('category/<slug:slug>/', category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:post_slug>/', post_detail, name='post_detail'),
    
    # Newsletter
    path('newsletter/signup/', newsletter_signup, name='newsletter_signup'),
    
    # Robots and sitemap
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)