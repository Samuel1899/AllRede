# AllRede/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importe suas views dos apps correspondentes
from accounts.views import profile_view # Assumindo que profile_view está em accounts.views
from posts.views_html import (
    post_list_create_view,
    delete_post,
    add_comment_to_post,
    like_post,
    user_profile_view # <-- Importe user_profile_view daqui, se ela estiver em posts.views_html
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls_html')), # Inclua as URLs do seu app accounts
    path('comments/', include('comments.urls')), # Se você tiver URLs para comments
    path('friends/', include('friends.urls')),   # <-- Adicione as URLs do app friends

    # URLs do seu app posts (ajuste conforme a organização real das suas views)
    path('', post_list_create_view, name='home'),
    path('posts/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('posts/<int:post_id>/comment/', add_comment_to_post, name='add_comment_to_post'),
    path('posts/<int:post_id>/like/', like_post, name='like_post'),

    # URL para perfil de outros usuários (usando o username)
    path('profile/<str:username>/', user_profile_view, name='user_profile'),

    # Sua URL de perfil existente para o usuário logado (geralmente sem username no path)
    path('profile/', profile_view, name='profile'),
]

# Configuração para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)