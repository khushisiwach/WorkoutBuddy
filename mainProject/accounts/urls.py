from django.urls import path
from . import views 

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
     path('login/google/', views.google_login_redirect, name='google_login'),
    path('login/callback/', views.google_login_callback, name='google_callback'),
    path('google/callback/', views.google_login_callback, name='google_callback_direct'), 
    path('profile/', views.view_or_edit_profile, name='profile'),
    
]
