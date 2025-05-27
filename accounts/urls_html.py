# accounts/urls_html.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, CustomLoginView, profile_view


urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', profile_view, name='profile'),
]