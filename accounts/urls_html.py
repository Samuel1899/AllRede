# accounts/urls_html.py
from django.urls import path
from django.contrib.auth import views as auth_views
# Importe user_profile_view aqui, junto com as outras views
from .views import register_view, CustomLoginView, profile_view, user_profile_view


urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', profile_view, name='profile'),
    # NOVA URL para perfis de outros usuários:
    path('profile/<str:username>/', user_profile_view, name='user_profile'),
]