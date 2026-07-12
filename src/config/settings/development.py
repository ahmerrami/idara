"""Development settings."""

from .base import *  # noqa: F401,F403

SECRET_KEY = 'django-insecure-vb0q$gw^s8&t@tzp3fpk04*)xnpwdy#4+djh^z^r-^s!sc117w'
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
