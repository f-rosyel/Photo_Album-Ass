"""
Class-Based Views for the Photo Album app.

CRUD map
--------
  Album : ListView, DetailView, CreateView, UpdateView, DeleteView
  Photo : DetailView, CreateView, UpdateView, DeleteView
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)

from .forms import AlbumForm, PhotoForm, UserRegistrationForm
from .mixins import AlbumOwnerOrAdminMixin, PhotoOwnerOrAdminMixin, PublicOrAuthenticatedMixin
from .models import Album, Photo


# ─── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class    = UserRegistrationForm
    success_url   = reverse_lazy('albums:album-list')

    def form_valid(self, form):
        data = form.cleaned_data
        if User.objects.filter(username=data['username']).exists():
            form.add_error('username', 'Username already taken.')
            return self.form_invalid(form)
        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''),
            password=data['password1'],
        )
        login(self.request, user)
        messages.success(self.request, f'Welcome, {user.username}!')
        return super().form_valid(form)


# ─── Album Views ───────────────────────────────────────────────────────────────

class AlbumListView(ListView):
    """
    Home page.
    - Authenticated users see their own albums + all public albums.
    - Anonymous users see only public albums.
    """
    model               = Album
    template_name       = 'albums/album_list.html'
    context_object_name = 'albums'
    paginate_by         = 12

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            qs = Album.objects.filter(Q(is_public=True) | Q(owner=user))
        else:
            qs = Album.objects.filter(is_public=True)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs.select_related('owner').prefetch_related('photos')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


class AlbumDetailView(PublicOrAuthenticatedMixin, DetailView):
    model               = Album
    template_name       = 'albums/album_detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['photos']      = self.object.photos.select_related('uploader')
        ctx['can_manage']  = (
            self.request.user.is_authenticated and
            (self.request.user.is_staff or self.object.owner == self.request.user)
        )
        ctx['photo_form']  = PhotoForm()
        return ctx


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model         = Album
    form_class    = AlbumForm
    template_name = 'albums/album_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Album created successfully!')
        return super().form_valid(form)


class AlbumUpdateView(AlbumOwnerOrAdminMixin, UpdateView):
    model         = Album
    form_class    = AlbumForm
    template_name = 'albums/album_form.html'

    def get_album_object(self):
        return self.get_object()

    def form_valid(self, form):
        messages.success(self.request, 'Album updated.')
        return super().form_valid(form)


class AlbumDeleteView(AlbumOwnerOrAdminMixin, DeleteView):
    model         = Album
    template_name = 'albums/album_confirm_delete.html'
    success_url   = reverse_lazy('albums:album-list')

    def get_album_object(self):
        return self.get_object()

    def form_valid(self, form):
        messages.success(self.request, 'Album deleted.')
        return super().form_valid(form)


# ─── Photo Views ───────────────────────────────────────────────────────────────

class PhotoDetailView(PublicOrAuthenticatedMixin, DetailView):
    model               = Photo
    template_name       = 'albums/photo_detail.html'
    context_object_name = 'photo'

    def get_object(self):
        return get_object_or_404(
            Photo,
            pk=self.kwargs['pk'],
            album__pk=self.kwargs['album_pk'],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['can_manage'] = (
            self.request.user.is_authenticated and
            (
                self.request.user.is_staff
                or self.object.album.owner == self.request.user
                or self.object.uploader == self.request.user
            )
        )
        return ctx


class PhotoCreateView(LoginRequiredMixin, CreateView):
    model         = Photo
    form_class    = PhotoForm
    template_name = 'albums/photo_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.album = get_object_or_404(Album, pk=kwargs['album_pk'])
        # Only album owner, staff, or any authenticated user (if album is public) can upload
        if not (request.user.is_staff or self.album.owner == request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.album    = self.album
        form.instance.uploader = self.request.user
        messages.success(self.request, 'Photo uploaded!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('albums:album-detail', kwargs={'pk': self.album.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['album'] = self.album
        return ctx


class PhotoUpdateView(PhotoOwnerOrAdminMixin, UpdateView):
    model         = Photo
    form_class    = PhotoForm
    template_name = 'albums/photo_form.html'

    def get_object(self):
        return get_object_or_404(
            Photo,
            pk=self.kwargs['pk'],
            album__pk=self.kwargs['album_pk'],
        )

    def get_photo_object(self):
        return self.get_object()

    def form_valid(self, form):
        messages.success(self.request, 'Photo updated.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('albums:photo-detail',
                       kwargs={'album_pk': self.object.album.pk, 'pk': self.object.pk})


class PhotoDeleteView(PhotoOwnerOrAdminMixin, DeleteView):
    model         = Photo
    template_name = 'albums/photo_confirm_delete.html'

    def get_object(self):
        return get_object_or_404(
            Photo,
            pk=self.kwargs['pk'],
            album__pk=self.kwargs['album_pk'],
        )

    def get_photo_object(self):
        return self.get_object()

    def get_success_url(self):
        return reverse('albums:album-detail', kwargs={'pk': self.object.album.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Photo deleted.')
        return super().form_valid(form)
