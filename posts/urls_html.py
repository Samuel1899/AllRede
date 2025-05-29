# C:\Users\Meu computador\Desktop\AllRede\posts\urls_html.py

from django.urls import path
from .views_html import post_list_create_view, delete_post, add_comment_to_post, like_post

urlpatterns = [
    path('', post_list_create_view, name='home'), # A home do seu site
    path('<int:post_id>/delete/', delete_post, name='delete_post'),
    path('<int:post_id>/comment/', add_comment_to_post, name='add_comment_to_post'),
    path('<int:post_id>/like/', like_post, name='like_post'),
    # Adicione outras URLs relacionadas a posts aqui, se houver
]