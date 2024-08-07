"""
URL configuration for mypandablog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from blog.views import frontpage, about, post_detail, category_detail, search, robots_txt, contact, privacy_policy, terms_conditions
from django.contrib.sitemaps.views import sitemap

from blog.sitemaps import PostSitemap, CategorySitemap

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': {'posts': PostSitemap, 'categories': CategorySitemap}}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('admin/', admin.site.urls),
    path('', frontpage, name='frontpage'),
    path('about/', about, name='about'),
    path("search/", search, name="search"),
    path('contact/', contact, name='contact'),
    path("privacy_policy/", privacy_policy, name="privacy_policy"),
    path("terms_conditions/", terms_conditions, name="terms"),
    path('<slug:slug>/', post_detail, name='post_detail'),
    path('category/<slug:slug>/', category_detail, name='category_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)