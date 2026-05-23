from django.contrib import admin
from .models import Album, Photo


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display  = ('title', 'owner', 'is_public', 'photo_count', 'created_at')
    list_filter   = ('is_public', 'created_at')
    search_fields = ('title', 'owner__username')
    raw_id_fields = ('owner',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'album', 'uploader', 'uploaded_at')
    list_filter   = ('uploaded_at',)
    search_fields = ('title', 'album__title', 'uploader__username')
    raw_id_fields = ('album', 'uploader')
