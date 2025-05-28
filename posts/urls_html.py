# posts/urls_html.py
from django.urls import path
# Certifique-se que like_post está importada
from .views_html import post_list_create_view, delete_post, add_comment_to_post, like_post

urlpatterns = [
    path('', post_list_create_view, name='home'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('post/<int:post_id>/comment/', add_comment_to_post, name='add_comment_to_post'),
    path('post/<int:post_id>/like/', like_post, name='like_post'), # <-- NOVA URL
]