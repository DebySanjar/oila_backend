"""
Production settings for PythonAnywhere/Railway/Render
"""
from .settings import *
import os

# SECURITY
DEBUG = False
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',  # PythonAnywhere
    '*.railway.app',  # Railway
    '*.onrender.com',  # Render
    'localhost',
    '127.0.0.1',
]

# CORS - Allow Flutter app
CORS_ALLOWED_ORIGINS = [
    "https://yourusername.pythonanywhere.com",
]
CORS_ALLOW_ALL_ORIGINS = True  # Development only - remove in production!

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database - Use environment variable
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For PostgreSQL (Railway/Render):
# import dj_database_url
# DATABASES['default'] = dj_database_url.config(conn_max_age=600)
