"""Shared Django settings for all environments."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-local-dev-key')
SOCIETE = os.getenv('SOCIETE', 'Idara')

CORS_ALLOWED_ORIGINS = [
    item.strip()
    for item in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if item.strip()
]
ALLOWED_HOSTS = [
    item.strip()
    for item in os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')
    if item.strip()
]
BLOCKED_IPS = [
    item.strip()
    for item in os.getenv('BLOCKED_IPS', '').split(',')
    if item.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'rest_framework.authtoken',
    'authemail',
    'corsheaders',
    'accounts',
    'core',
    'fournisseurs',
    'import_export',
    'django_extensions',
    'dbbackup',
    'clients',
    'storages',
]

AUTH_USER_MODEL = 'accounts.MyUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- AJOUT ICI : Indispensable pour intercepter le CSS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.CurrentUserMiddleware',
    'fournisseurs.middleware.BlockIPMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'config.wsgi.application'

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# AJOUT ICI : Configuration recommandée pour Django 5.x afin de compresser/mettre en cache les styles
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_HOST = os.getenv('AUTHEMAIL_EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('AUTHEMAIL_EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('AUTHEMAIL_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('AUTHEMAIL_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'false').lower() == 'true'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/admin/'

AUTHEMAIL_EMAIL_VERIFICATION_URL = os.getenv(
    'AUTHEMAIL_EMAIL_VERIFICATION_URL',
    '/api/accounts/email/verify/',
)
AUTHEMAIL_PASSWORD_RESET_URL = os.getenv(
    'AUTHEMAIL_PASSWORD_RESET_URL',
    '/accounts/password/reset/confirm/',
)
AUTHEMAIL_EMAIL_FROM = os.getenv('AUTHEMAIL_EMAIL_HOST_USER', '')
AUTHEMAIL_EMAIL_SUBJECT_PREFIX = os.getenv(
    'AUTHEMAIL_EMAIL_SUBJECT_PREFIX',
    f'[{SOCIETE}] ',
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'