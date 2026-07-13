"""URL configuration for the migrated backend."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from fournisseurs.admin.facture_admin import fournisseur_admin

urlpatterns = [
    path('api/fournisseurs/', include('fournisseurs.urls')),
    path('clients/', include('clients.urls')),
    path('accounts/', include('accounts.urls')),
    path('fournisseurs/', fournisseur_admin.urls),
    path('', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns = [
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        *urlpatterns,
    ]
