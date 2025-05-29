# C:\Users\Meu computador\Desktop\AllRede\accounts\urls_html.py

from django.urls import path
from django.contrib.auth import views as auth_views
# Importe as views do seu accounts/views.py, incluindo SignUpView
from .views import SignUpView, user_profile_view, edit_profile_view, send_friend_request, accept_friend_request, decline_friend_request, remove_friend

urlpatterns = [
    # URLs de Autenticação (Django's built-in views)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'), # <--- Caminho do template corrigido
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # URL de Registro (usando sua SignUpView como uma classe)
    path('register/', SignUpView.as_view(), name='register'), # <--- Usando .as_view()

    # URLs de Perfil
    path('profile/<str:username>/', user_profile_view, name='user_profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'), # <--- Nome da URL

    # URLs de Amizade (visto que as views estão em accounts/views.py)
    path('send-friend-request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<int:request_id>/', decline_friend_request, name='decline_friend_request'),
    path('remove-friend/<int:user_id>/', remove_friend, name='remove_friend'),
]