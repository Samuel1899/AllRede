# accounts/urls_api.py
from django.urls import path
from .views import RegisterAPIView, CustomTokenLoginView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api-register'),
    path('login/', CustomTokenLoginView.as_view(), name='api-login'),
]