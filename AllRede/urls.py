# AllRede/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importe suas views diretamente se precisar delas para URLs específicas,
# ou use include para apps inteiros.
from posts.views_html import post_list_create_view, delete_post, add_comment_to_post, like_post, user_profile_view
# Certifique-se de que a importação para views de accounts e friends estão corretas se você tiver

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', post_list_create_view, name='home'),
    path('register/', include('accounts.urls_html')), # Assumindo que você tem um accounts/urls.py
    path('posts/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('posts/<int:post_id>/comment/', add_comment_to_post, name='add_comment_to_post'),
    path('posts/<int:post_id>/like/', like_post, name='like_post'),
    path('profile/<str:username>/', user_profile_view, name='user_profile'),
    
    # URLs para o app de amigos
    path('friends/', include('friends.urls')), # Inclua as URLs do seu app 'friends'
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)