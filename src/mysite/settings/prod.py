# settings/prod.py
from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

# Sécurité
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

if config('SECURE_PROXY_SSL_HEADER_ENABLED', default=False, cast=bool):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

USE_X_FORWARDED_HOST = config('USE_X_FORWARDED_HOST', default=False, cast=bool)

_csrf_trusted = config('CSRF_TRUSTED_ORIGINS', default='').strip()
if _csrf_trusted:
    CSRF_TRUSTED_ORIGINS = [item.strip() for item in _csrf_trusted.split(',') if item.strip()]

# Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Configuration spécifique à la production
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/home/supratourstravel/mysite/media')
STATIC_ROOT = os.environ.get('STATIC_ROOT', '/home/supratourstravel/mysite/static')

# -------------------------------
# 🔥 BACKUP DIRECT VIA SFTP (Django Storages)
# -------------------------------

# Configuration Django Storages pour SFTP
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    # Storage pour les backups DB
    "dbbackup": {
        "BACKEND": "storages.backends.sftpstorage.SFTPStorage",
        "OPTIONS": {
            "host": "ivyerrami.ddns.net",
            "params": {
                "username": "webmaster",
                "key_filename": "/home/supratourstravel/.ssh/id_ed25519",
                "port": 40022,  # Port dans params
            },
            "root_path": "/home/webmaster/backups/pythonanywhere/db",
        },
    },
    # Storage pour les backups média
    "mediabackup": {
        "BACKEND": "storages.backends.sftpstorage.SFTPStorage",
        "OPTIONS": {
            "host": "ivyerrami.ddns.net",
            "params": {
                "username": "webmaster",
                "key_filename": "/home/supratourstravel/.ssh/id_ed25519",
                "port": 40022,  # Port dans params
            },
            "root_path": "/home/webmaster/backups/pythonanywhere/media",
        },
    },
}

# Configuration django-dbbackup (nouvelle syntaxe v4+)
DBBACKUP_STORAGE_ALIAS = "dbbackup"
DBBACKUP_MEDIAFILES_STORAGE_ALIAS = "mediabackup"

# Format SQL lisible au lieu de dump binaire
DBBACKUP_CONNECTORS = {
    'default': {
        'CONNECTOR': 'dbbackup.db.mysql.MysqlDumpConnector',
    }
}

# Extension et préfixe pour les noms de fichiers
DBBACKUP_FILENAME_TEMPLATE = 'backup-{databasename}-{datetime}.sql'
DBBACKUP_DATE_FORMAT = '%Y%m%d-%H%M%S'

# On ne garde plus rien localement
DBBACKUP_CLEANUP_KEEP = 0
DBBACKUP_CLEANUP_KEEP_MEDIA = 0
