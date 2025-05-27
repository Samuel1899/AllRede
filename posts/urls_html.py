# posts/urls_html.py
from django.urls import path
from .views_html import post_list_create_view, delete_post

urlpatterns = [
    # Esta linha define a URL raiz ('') como 'home' e a associa à sua view de posts.
    path('', post_list_create_view, name='home'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
]