from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="home-page"),
    path('read-emails/', views.read_emails, name='read-emails'),
    path('gmail-auth/', views.gmail_auth, name='gmail-auth'),
    path('gmail-auth/callback/', views.gmail_auth_callback, name='gmail-auth-callback'),
]
