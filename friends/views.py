# friends/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Para enviar mensagens de feedback ao usuário
from django.db.models import Q # Para consultas complexas
from .models import FriendRequest, Friendship
from accounts.models import CustomUser # Seu modelo de usuário

@login_required
def send_friend_request(request, user_id):
    """
    Envia uma solicitação de amizade para um usuário.
    """
    to_user = get_object_or_404(CustomUser, id=user_id)
    from_user = request.user

    if request.method == 'POST': # Garantir que a requisição é POST
        # Não enviar solicitação para si mesmo
        if from_user == to_user:
            messages.error(request, "Você não pode enviar uma solicitação de amizade para si mesmo.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # Verificar se já são amigos
        if Friendship.objects.filter(user=from_user, friend=to_user).exists():
            messages.info(request, f"Você já é amigo de {to_user.username}.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # Verificar se já existe uma solicitação pendente (do from_user para o to_user)
        existing_request_sent = FriendRequest.objects.filter(
            from_user=from_user, to_user=to_user, is_active=True
        ).exists()

        if existing_request_sent:
            messages.info(request, f"Você já enviou uma solicitação de amizade para {to_user.username}.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # Verificar se já existe uma solicitação pendente (do to_user para o from_user)
        # Se sim, significa que o outro usuário já enviou para você.
        # Neste caso, ao invés de enviar uma nova, o remetente deveria aceitar a existente.
        existing_request_received = FriendRequest.objects.filter(
            from_user=to_user, to_user=from_user, is_active=True
        ).exists()

        if existing_request_received:
            messages.info(request, f"{to_user.username} já te enviou uma solicitação de amizade. Você pode aceitá-la.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))


        # Se nenhuma das condições acima for verdadeira, cria a solicitação
        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        messages.success(request, f"Solicitação de amizade enviada para {to_user.username}.")
    else:
        messages.error(request, "Método de requisição inválido.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def accept_friend_request(request, request_id):
    """
    Aceita uma solicitação de amizade.
    """
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if request.method == 'POST': # Garantir que a requisição é POST
        # Verifica se a solicitação é realmente para o usuário logado e se está ativa
        if friend_request.to_user != request.user or not friend_request.is_active:
            messages.error(request, "Solicitação de amizade inválida ou já processada.")
            return redirect('home')

        friend_request.accept()
        messages.success(request, f"Você e {friend_request.from_user.username} agora são amigos!")
    else:
        messages.error(request, "Método de requisição inválido.")

    return redirect('home') # Redireciona para a home ou para a página de perfil do remetente


@login_required
def decline_friend_request(request, request_id):
    """
    Recusa uma solicitação de amizade.
    """
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if request.method == 'POST': # Garantir que a requisição é POST
        # Verifica se a solicitação é realmente para o usuário logado e se está ativa
        if friend_request.to_user != request.user or not friend_request.is_active:
            messages.error(request, "Solicitação de amizade inválida ou já processada.")
            return redirect('home')

        friend_request.decline()
        messages.info(request, f"Você recusou a solicitação de amizade de {friend_request.from_user.username}.")
    else:
        messages.error(request, "Método de requisição inválido.")

    return redirect('home')


@login_required
def cancel_friend_request(request, request_id):
    """
    Cancela uma solicitação de amizade enviada pelo usuário logado.
    """
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if request.method == 'POST': # Garantir que a requisição é POST
        # Verifica se a solicitação foi enviada pelo usuário logado e se está ativa
        if friend_request.from_user != request.user or not friend_request.is_active:
            messages.error(request, "Solicitação de amizade inválida ou já processada.")
            return redirect('home')

        friend_request.cancel()
        messages.info(request, f"Você cancelou a solicitação de amizade para {friend_request.to_user.username}.")
    else:
        messages.error(request, "Método de requisição inválido.")

    return redirect('home')


@login_required
def friend_list_view(request):
    """
    Exibe a lista de amigos do usuário logado, bem como solicitações enviadas e recebidas.
    """
    # Amizades onde o request.user é 'user'
    # Use select_related para buscar os dados do amigo de forma eficiente
    my_friendships = Friendship.objects.filter(user=request.user).select_related('friend')
    friends = [f.friend for f in my_friendships]

    # Solicitações de amizade recebidas pelo usuário logado
    received_requests = FriendRequest.objects.filter(to_user=request.user, is_active=True).select_related('from_user')

    # Solicitações de amizade enviadas pelo usuário logado
    sent_requests = FriendRequest.objects.filter(from_user=request.user, is_active=True).select_related('to_user')

    context = {
        'friends': friends,
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    }
    return render(request, 'friends/friend_list.html', context) # Você vai criar este template


# Função auxiliar para verificar o status da amizade entre DOIS usuários
def get_friendship_status(from_user, to_user):
    """
    Determina o status da amizade entre dois usuários (from_user e to_user).
    Retorna:
    - 'self' se from_user e to_user são o mesmo usuário.
    - 'friends' se já são amigos.
    - 'sent_request' se from_user enviou solicitação para to_user.
    - 'received_request' se to_user enviou solicitação para from_user.
    - 'not_friends' se não há relacionamento.
    """
    if from_user == to_user:
        return 'self' # É o próprio usuário

    # Verificar se já são amigos (bidirecionalmente)
    if Friendship.objects.filter(user=from_user, friend=to_user).exists():
        return 'friends'

    # Verificar se from_user enviou solicitação para to_user
    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, is_active=True).exists():
        return 'sent_request'

    # Verificar se to_user enviou solicitação para from_user
    if FriendRequest.objects.filter(from_user=to_user, to_user=from_user, is_active=True).exists():
        return 'received_request'

    return 'not_friends'