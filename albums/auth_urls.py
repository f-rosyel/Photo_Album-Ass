from django.urls import path
from albums.views import RegisterView

urlpatterns = [
    path('', RegisterView.as_view(), name='register'),
]
