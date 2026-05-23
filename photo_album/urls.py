from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', include('albums.auth_urls')),
    path('', include('albums.urls')),
]

# Serve media locally during development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else '')
