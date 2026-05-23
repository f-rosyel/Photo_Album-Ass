from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from cloudinary.models import CloudinaryField


class Album(models.Model):
    """A photo album owned by a user."""

    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = CloudinaryField('cover_image', blank=True, null=True)
    is_public   = models.BooleanField(default=True,
                    help_text='Public albums are visible to all users.')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('albums:album-detail', kwargs={'pk': self.pk})

    @property
    def photo_count(self):
        return self.photos.count()


class Photo(models.Model):
    """A single photo belonging to an album."""

    album       = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    uploader    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='photos')
    image       = CloudinaryField('image')
    title       = models.CharField(max_length=200, blank=True)
    caption     = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or f'Photo {self.pk}'

    def get_absolute_url(self):
        return reverse('albums:photo-detail', kwargs={'album_pk': self.album.pk, 'pk': self.pk})
