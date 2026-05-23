from django import forms
from .models import Album, Photo


class AlbumForm(forms.ModelForm):
    class Meta:
        model   = Album
        fields  = ['title', 'description', 'cover_image', 'is_public']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Album title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description…'}),
            'is_public':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model  = Photo
        fields = ['image', 'title', 'caption']
        widgets = {
            'title':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo title (optional)'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Caption…'}),
        }


class UserRegistrationForm(forms.Form):
    username   = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email      = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1  = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2  = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned
