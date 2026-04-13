# myPandaBlog

A personal blog platform built with Django 5.1.3.

## Features
- Categorized blog posts with featured content
- Tagging system (django-taggit)
- Comment system with sentiment analysis (TextBlob)
- Newsletter subscriptions
- Post view tracking (django-hitcount)
- Rich text editing (CKEditor 5)
- Customized admin interface (django-jazzmin)
- Post recommendations engine

## Tech Stack
- **Backend:** Django 5.1.3 (Python 3.12)
- **Database:** SQLite (db.sqlite3)
- **Frontend:** Django templates, Tailwind CSS, Alpine.js
- **Key packages:** django-jazzmin, django-ckeditor-5, django-taggit, django-crispy-forms, django-hitcount, django-compressor, textblob

## Project Structure
- `mypandablog/` — Django project config (settings, urls, wsgi)
- `blog/` — Main blog application (models, views, urls, utils)
- `templates/` — HTML templates
- `static/` — Source static assets (CSS, JS, images)
- `staticfiles/` — Collected static assets
- `media/` — User-uploaded content

## Running
- **Development:** `python manage.py runserver 0.0.0.0:5000` (workflow configured)
- **Production:** gunicorn on port 5000 via `mypandablog.wsgi:application`

## Environment
- `DJANGO_SECRET_KEY` — Django secret key (has fallback insecure default for dev)
- `REPLIT_DEV_DOMAIN` — Used to configure CSRF trusted origins automatically

## Notes
- `ALLOWED_HOSTS = ['*']` for Replit proxy compatibility
- Secure cookies disabled in DEBUG mode
- TextBlob is used for comment sentiment analysis (not in original requirements.txt, added manually)
