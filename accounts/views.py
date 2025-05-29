# C:\Users\Meu computador\Desktop\AllRede\accounts\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model() # Garante que User está sempre definido para uso global no módulo
from django.contrib import messages
from django.views.generic import CreateView
from django.db.models import Q

from .forms import CustomUserCreationForm, CustomUserChangeForm
from posts.models import Post
from friends.models import Friendship, FriendRequest

# View para registro de usuário (SignUp)
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = '/accounts/login/' # Redirecionar para a página de login após o registro (URL completa)
    template_name = 'registration/register.html' # Ajustado para 'registration/register.html' (assumindo que você moveu 'register.html' para a pasta 'registration' dentro de 'templates')

@login_required
def user_profile_view(request, username):
    # Usar a variável 'User' já definida globalmente, sem chamar get_user_model() novamente
    user_profile = get_object_or_404(User, username=username)

    # Lógica para saber se o usuário logado é amigo ou tem pedido pendente
    is_friend = False
    friend_request_sent = False
    friend_request_received = False

    if request.user.is_authenticated and request.user != user_profile:
        # Verifica se já são amigos (bidirecional)
        if Friendship.objects.filter(
            Q(user=request.user, friend=user_profile, status='accepted') |
            Q(user=user_profile, friend=request.user, status='accepted')
        ).exists():
            is_friend = True

        # Verifica se o usuário logado já enviou um pedido para este perfil
        if FriendRequest.objects.filter(from_user=request.user, to_user=user_profile, is_active=True).exists():
            friend_request_sent = True

        # Verifica se este perfil enviou um pedido para o usuário logado
        if FriendRequest.objects.filter(from_user=user_profile, to_user=request.user, is_active=True).exists():
            friend_request_received = True

    # Obter os posts deste usuário
    user_posts = Post.objects.filter(author=user_profile).order_by('-created_at')

    context = {
        'user_profile': user_profile,
        'user_posts': user_posts,
        'is_friend': is_friend,
        'friend_request_sent': friend_request_sent,
        'friend_request_received': friend_request_received,
    }
    return render(request, 'accounts/profile_detail.html', context)


@login_required
def edit_profile_view(request):
    # Usar a variável 'User' já definida globalmente, sem chamar get_user_model() novamente
    if request.method == 'POST':
        # Instancie o formulário com os dados POST, arquivos (se houver) e a instância do usuário atual
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            # Redirecione para a página de perfil do usuário, usando o username atualizado
            return redirect('accounts:user_profile', username=request.user.username) # Usar namespace 'accounts:'
        else:
            messages.error(request, "Erro ao atualizar o perfil. Verifique os campos.")
    else:
        # Se for um GET, instancie o formulário com os dados atuais do usuário
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# Views para Amizade (Friendship)
@login_required
def send_friend_request(request, user_id):
    # Usar a variável 'User' já definida globalmente
    to_user = get_object_or_404(User, id=user_id)
    if request.user == to_user:
        messages.error(request, "Você não pode enviar uma solicitação de amizade para si mesmo.")
    elif FriendRequest.objects.filter(from_user=request.user, to_user=to_user, is_active=True).exists():
        messages.info(request, "Você já enviou uma solicitação de amizade para este usuário.")
    elif FriendRequest.objects.filter(from_user=to_user, to_user=request.user, is_active=True).exists():
        messages.info(request, "Este usuário já enviou uma solicitação de amizade para você. Aceite-a na sua página de amizades.")
    elif Friendship.objects.filter(Q(user=request.user, friend=to_user, status='accepted') | Q(user=to_user, friend=request.user, status='accepted')).exists():
        messages.info(request, "Vocês já são amigos.")
    else:
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
        messages.success(request, f"Solicitação de amizade enviada para {to_user.username}!")
    return redirect('accounts:user_profile', username=to_user.username) # Usar namespace 'accounts:'


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if request.user == friend_request.to_user and friend_request.is_active:
        friend_request.accept() # Isso vai criar a Friendship e desativar a requisição
        messages.success(request, f"Você aceitou a solicitação de amizade de {friend_request.from_user.username}.")
    else:
        messages.error(request, "Você não tem permissão para aceitar esta solicitação ou ela não está ativa.")
    return redirect('home') # Ou para a página de amizades


@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if request.user == friend_request.to_user and friend_request.is_active:
        friend_request.decline()
        messages.success(request, f"Você recusou a solicitação de amizade de {friend_request.from_user.username}.")
    else:
        messages.error(request, "Você não tem permissão para recusar esta solicitação ou ela não está ativa.")
    return redirect('home') # Ou para a página de amizades

@login_required
def remove_friend(request, user_id):
    # Usar a variável 'User' já definida globalmente
    friend_to_remove = get_object_or_404(User, id=user_id)
    # Tenta remover a amizade em ambas as direções
    friendship1 = Friendship.objects.filter(user=request.user, friend=friend_to_remove, status='accepted')
    friendship2 = Friendship.objects.filter(user=friend_to_remove, friend=request.user, status='accepted')

    if friendship1.exists() or friendship2.exists():
        friendship1.delete()
        friendship2.delete()
        messages.success(request, f"Você removeu {friend_to_remove.username} da sua lista de amigos.")
    else:
        messages.error(request, "Vocês não são amigos.")
    return redirect('accounts:user_profile', username=friend_to_remove.username) # Usar namespace 'accounts:'