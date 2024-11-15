"""
Django settings for mypandablog project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dutyiwb0-kx^dli$a1iw$bql%s0t1*@swpyw^zu8+f6)1uaicn')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['mailstation.tech', 'mypandablog-brxj.zeet-panda-team.zeet.app', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://mypandablog-brxj.zeet-panda-team.zeet.app', 'https://mailstation.tech']
CSRF_ALLOWED_ORIGINS = ['https://mypandablog-brxj.zeet-panda-team.zeet.app', 'https://mailstation.tech']
CORS_ORIGINS_WHITELIST = ['https://mypandablog-brxj.zeet-panda-team.zeet.app', 'https://mailstation.tech']
CORS_ALLOWED_ORIGINS = ['https://mypandablog-brxj.zeet-panda-team.zeet.app', 'https://mailstation.tech']

# SECURE_SSL_REDIRECT = True

# Use secure cookies in production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Use HTTPOnly cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Cookie settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
    'ckeditor',
    'taggit',
    'crispy_forms',
    'hitcount',
    'compressor',
    'markdown',
    'markdown_deux',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'mypandablog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, ''), os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mypandablog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Changed to avoid conflict
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'blog/static',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development
DEFAULT_FROM_EMAIL = 'noreply@mypandablog.com'
SERVER_EMAIL = 'server@mypandablog.com'
EMAIL_SUBJECT_PREFIX = '[MyPandaBlog] '

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Message settings
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Authentication URLs and Settings
LOGOUT_REDIRECT_URL = 'frontpage'
ACCOUNT_LOGOUT_ON_GET = True  # Allow logout on GET request for simplicity
ACCOUNT_SIGNUP_REDIRECT_URL = 'profile'
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_PASSWORD_MIN_LENGTH = 8
ACCOUNT_RATE_LIMITS = {
    # 5 failed attempts in 5 minutes
    'login_failed': '5/5m',
    # 3 sign ups per IP per day
    'signup': '3/d',
    # 3 password reset requests per IP per day
    'reset_password': '3/d',
}

# Custom forms
# ACCOUNT_FORMS = {
#     'login': 'blog.forms.CustomLoginForm',
#     'signup': 'blog.forms.CustomSignupForm',
#     'reset_password': 'blog.forms.CustomPasswordResetForm',
# }

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# CKEditor
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}

# Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Static files
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# Django Compressor
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
