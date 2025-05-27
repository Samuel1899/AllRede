# AllRede/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from posts.views_html import post_list_create_view as home_view

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importe settings
from django.conf.urls.static import static # Importe static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home_view, name='home'),

    path('accounts/', include('accounts.urls_html')),

    # Inclui as URLs HTML de posts (onde está o delete_post)
    path('posts/', include('posts.urls_html')),

    path('api/accounts/', include('accounts.urls_api')),

    path('api/posts/', include('posts.urls_api')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls_html')), # Suas URLs de autenticação
    path('', include('posts.urls_html')), # Suas URLs de posts
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
