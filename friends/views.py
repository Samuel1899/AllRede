# friends/views.py

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import FriendRequest, Friendship # Importe seus modelos de amizade

@login_required
def send_friend_request(request, user_id):
    CustomUser = get_user_model()
    to_user = get_object_or_404(CustomUser, id=user_id)

    if request.user == to_user:
        messages.error(request, "Você não pode enviar um pedido de amizade para si mesmo.")
        return redirect('user_profile', username=to_user.username)

    # Verificar se já são amigos
    are_friends = Friendship.objects.filter(
        Q(user=request.user, friend=to_user) | Q(user=to_user, friend=request.user)
    ).exists()
    if are_friends:
        messages.info(request, f"Você já é amigo(a) de {to_user.username}.")
        return redirect('user_profile', username=to_user.username)

    # Verificar se já existe um pedido pendente
    existing_request = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=to_user, is_active=True) |
        Q(from_user=to_user, to_user=request.user, is_active=True)
    ).exists()

    if existing_request:
        messages.info(request, "Já existe um pedido de amizade pendente entre vocês.")
        return redirect('user_profile', username=to_user.username)

    # Criar o pedido de amizade
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, f"Pedido de amizade enviado para {to_user.username}.")
    return redirect('user_profile', username=to_user.username)


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user, is_active=True)
    
    if friend_request.accept():
        messages.success(request, f"Você aceitou o pedido de amizade de {friend_request.from_user.username}.")
    else:
        messages.error(request, "Não foi possível aceitar o pedido de amizade.")
    
    return redirect('home') # Ou para uma página de notificações/pedidos


@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user, is_active=True)
    
    if friend_request.decline():
        messages.info(request, f"Você recusou o pedido de amizade de {friend_request.from_user.username}.")
    else:
        messages.error(request, "Não foi possível recusar o pedido de amizade.")
    
    return redirect('home') # Ou para uma página de notificações/pedidos


@login_required
def cancel_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, from_user=request.user, is_active=True)
    
    if friend_request.cancel():
        messages.info(request, f"Você cancelou o pedido de amizade enviado para {friend_request.to_user.username}.")
    else:
        messages.error(request, "Não foi possível cancelar o pedido de amizade.")
    
    return redirect('home') # Ou para uma página de notificações/pedidos

@login_required
def remove_friend(request, user_id):
    CustomUser = get_user_model()
    friend_to_remove = get_object_or_404(CustomUser, id=user_id)

    # Remover a amizade bidirecional
    Friendship.objects.filter(
        Q(user=request.user, friend=friend_to_remove) | Q(user=friend_to_remove, friend=request.user)
    ).delete()

    messages.success(request, f"Você removeu {friend_to_remove.username} dos seus amigos.")
    return redirect('user_profile', username=friend_to_remove.username)