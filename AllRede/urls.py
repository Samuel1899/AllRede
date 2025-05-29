# C:\Users\Meu computador\Desktop\AllRede\AllRede\urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('posts.urls_html')), # Inclua as URLs do app 'posts'

    path('accounts/', include('accounts.urls_html')), # Inclua as URLs do app 'accounts'

    # DECISÃO IMPORTANTE: Se você tem um 'friends/urls.py' COM VIEWS LÁ DENTRO, mantenha.
    # CASO CONTRÁRIO (se as views de amizade estão em accounts/views.py), COMENTE OU REMOVA A LINHA ABAIXO.
    # path('friends/', include('friends.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)