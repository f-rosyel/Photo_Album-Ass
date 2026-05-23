"""
Role-Based Access Control helpers.

Roles
-----
  Anonymous  – can only view public albums/photos
  Authenticated (standard user)
             – can create albums, upload photos to own albums,
               edit/delete own content
  Album Admin (staff or album owner)
             – can edit/delete any album or photo

Mixins are used in CBVs to enforce these rules.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AlbumOwnerOrAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allow access only to the album's owner or a staff user."""

    def get_album_object(self):
        """Sub-classes must implement this to return the Album instance."""
        raise NotImplementedError

    def test_func(self):
        album = self.get_album_object()
        user  = self.request.user
        return user.is_staff or album.owner == user


class PhotoOwnerOrAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allow access only to the photo's uploader, the album owner, or staff."""

    def get_photo_object(self):
        raise NotImplementedError

    def test_func(self):
        photo = self.get_photo_object()
        user  = self.request.user
        return (
            user.is_staff
            or photo.album.owner == user
            or photo.uploader == user
        )


class PublicOrAuthenticatedMixin:
    """
    For read-only views: public albums are visible to everyone;
    private albums only to authenticated users who own them or are staff.
    """

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Photo views pass through to album-level check
        album = getattr(obj, 'album', obj)

        if not album.is_public:
            if not request.user.is_authenticated:
                from django.conf import settings
                from django.shortcuts import redirect
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            if not (request.user.is_staff or album.owner == request.user):
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
