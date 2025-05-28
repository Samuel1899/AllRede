# accounts/views.py

# Importações de Rest Framework (para API)
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

# Importações do Django (para Views HTML)
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404 # Adicionado get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden # Para controle de acesso em delete_post (se for movido para cá, mas está em posts/views_html.py)

# Importações dos seus apps
from .forms import CustomUserCreationForm, UserProfileForm # Importe ambos os formulários
from .models import CustomUser # Importe seu modelo CustomUser
from .serializers import RegisterSerializer # Para a API de registro
from posts.models import Post # Importe o modelo Post para buscar os posts do usuário

# =====================================================================
# Views da API (geralmente em accounts/views.py ou accounts/api_views.py)
# =====================================================================

@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

class CustomTokenLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'username': token.user.username
        })

# =====================================================================
# Views HTML (geralmente em accounts/views_html.py ou accounts/views.py)
# =====================================================================

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') # Redireciona para a página de login após o registro
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'

@login_required
def profile_view(request):
    """
    View para o perfil do USUÁRIO LOGADO.
    Permite editar o próprio perfil e exibe seus posts.
    """
    # Pega todos os posts do usuário logado, ordenados pelo mais recente
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')

    if request.method == 'POST':
        # O formulário precisa da instância do usuário para preencher os campos existentes
        # e do request.FILES para lidar com o upload de arquivos (avatar)
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile') # Redireciona para o próprio perfil após salvar
    else:
        form = UserProfileForm(instance=request.user) # Preenche o formulário com dados do usuário logado

    context = {
        'user_posts': user_posts,
        'user': request.user, # O objeto 'user' é o usuário logado
        'form': form, # O formulário para edição do próprio perfil
    }
    return render(request, 'profile.html', context)


@login_required
def user_profile_view(request, username):
    """
    View para o perfil de OUTROS USUÁRIOS.
    Exibe as informações do usuário e seus posts.
    Permite edição APENAS se o usuário logado for o dono do perfil.
    """
    # Tenta buscar o usuário pelo username ou retorna um 404 Not Found
    user_to_view = get_object_or_404(CustomUser, username=username)

    # Pega todos os posts do usuário cujo perfil estamos vendo
    user_to_view_posts = Post.objects.filter(author=user_to_view).order_by('-created_at')

    form = None # Inicializa o formulário como None
    # Se o usuário logado for o dono do perfil que está sendo visualizado, permite edição
    if request.user == user_to_view:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('profile') # Redireciona para o próprio perfil (sem o username na URL)
        else:
            form = UserProfileForm(instance=request.user)

    context = {
        'user_to_view': user_to_view, # O usuário cujo perfil estamos vendo
        'user_to_view_posts': user_to_view_posts, # Posts desse usuário
        'form': form, # O formulário (será None se não for o perfil do usuário logado)
        'is_own_profile': request.user == user_to_view # Variável para controle no template
    }
    return render(request, 'user_profile.html', context) # Renderiza o template para outros perfis

@login_required
def user_profile_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    user_posts = Post.objects.filter(author=profile_user).order_by('-created_at')

    friendship_status = get_friendship_status(request.user, profile_user)
    request_id = None

    if friendship_status == 'sent_request':
        req = FriendRequest.objects.filter(from_user=request.user, to_user=profile_user, is_active=True).first()
        if req:
            request_id = req.id
    elif friendship_status == 'received_request':
        req = FriendRequest.objects.filter(from_user=profile_user, to_user=request.user, is_active=True).first()
        if req:
            request_id = req.id

    context = {
        'profile_user': profile_user,
        'user_posts': user_posts,
        'friendship_status': friendship_status,
        'request_id': request_id, # Passa o ID da solicitação aqui
    }
    return render(request, 'accounts/user_profile.html', context)