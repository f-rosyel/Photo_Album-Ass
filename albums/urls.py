from django.urls import path
from . import views

app_name = 'albums'

urlpatterns = [
    # Albums
    path('',                                            views.AlbumListView.as_view(),   name='album-list'),
    path('albums/create/',                              views.AlbumCreateView.as_view(), name='album-create'),
    path('albums/<int:pk>/',                            views.AlbumDetailView.as_view(), name='album-detail'),
    path('albums/<int:pk>/edit/',                       views.AlbumUpdateView.as_view(), name='album-update'),
    path('albums/<int:pk>/delete/',                     views.AlbumDeleteView.as_view(), name='album-delete'),

    # Photos (nested under album)
    path('albums/<int:album_pk>/photos/upload/',        views.PhotoCreateView.as_view(), name='photo-create'),
    path('albums/<int:album_pk>/photos/<int:pk>/',      views.PhotoDetailView.as_view(), name='photo-detail'),
    path('albums/<int:album_pk>/photos/<int:pk>/edit/', views.PhotoUpdateView.as_view(), name='photo-update'),
    path('albums/<int:album_pk>/photos/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo-delete'),
]
