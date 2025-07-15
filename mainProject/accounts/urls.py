from django.urls import path
from . import views
from .views import profile_view

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
      path("profile/", views.profile_view, name="profile"),
]
