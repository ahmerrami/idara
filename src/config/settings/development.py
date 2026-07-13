"""Development settings."""

import os

from .base import *  # noqa: F401,F403

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', SECRET_KEY)
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

CORS_ALLOWED_ORIGINS = [
    item.strip()
    for item in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
    if item.strip()
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
