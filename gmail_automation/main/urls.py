from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="home-page"),
    path('gmail-auth/', views.gmail_auth, name='gmail-auth'),
    path('gmail-auth/callback/', views.gmail_auth_callback, name='gmail-auth-callback'),
    path('read-emails/', views.read_emails, name='read-emails'),
    path('show-email/<str:email_id>/', views.show_email, name='show-email'),
    path('reply-email/<str:email_id>/', views.reply_email, name='reply-email')
]
