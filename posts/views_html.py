# posts/views_html.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages # Para mensagens de feedback

from .models import Post, Like
from .forms import PostForm
from comments.forms import CommentForm
from comments.models import Comment
from accounts.models import CustomUser

# Importe a função auxiliar de amizade do seu novo app 'friends'
from friends.models import Friendship, FriendRequest # Importe os modelos de amizade
from friends.views import get_friendship_status # Importe a função que calcula o status

@login_required
def post_list_create_view(request):
    """
    View para listar todos os posts no feed e permitir a criação de novos posts.
    Inclui lógica para status de likes, amigos online e sugestões de amizade.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            messages.success(request, "Seu post foi publicado com sucesso!")
            return redirect('home')
        else:
            messages.error(request, "Erro ao publicar o post. Verifique os campos.")
    else:
        form = PostForm()

    # Otimização: pré-carrega os autores dos posts, comentários e likes.
    posts = Post.objects.select_related('author').prefetch_related('comments__author', 'likes__user').all().order_by('-created_at')

    posts_data_for_template = []
    for post in posts:
        post_comments = post.comments.all()

        user_has_liked = False
        if request.user.is_authenticated:
            user_has_liked = any(like.user == request.user for like in post.likes.all())

        posts_data_for_template.append({
            'post': post,
            'comments': post_comments,
            'comment_form': CommentForm(),
            'user_has_liked': user_has_liked,
        })

    # Lógica para "Amigos Online" (placeholder por enquanto)
    # Em um sistema real, isso exigiria rastreamento de atividade do usuário.
    friends_online = [] # Substitua por uma lógica real de "online" no futuro

    # Lógica para "Pessoas que você talvez conheça"
    # Excluir o próprio usuário e usuários que já são amigos
    # E usuários para os quais já existe uma solicitação pendente (enviada ou recebida)
    current_friends_ids = Friendship.objects.filter(user=request.user).values_list('friend__id', flat=True)
    pending_requests_ids = FriendRequest.objects.filter(
        Q(from_user=request.user, is_active=True) | Q(to_user=request.user, is_active=True)
    ).values_list('from_user__id', flat=True) | FriendRequest.objects.filter(
        Q(from_user=request.user, is_active=True) | Q(to_user=request.user, is_active=True)
    ).values_list('to_user__id', flat=True)


    suggested_users_raw = CustomUser.objects.exclude(id=request.user.id).exclude(
        id__in=list(current_friends_ids) + list(pending_requests_ids)
    ).order_by('?')[:5] # Pega 5 sugestões aleatórias

    suggested_friends_with_status = []
    for su_user in suggested_users_raw:
        status = get_friendship_status(request.user, su_user)
        request_id = None # Inicializa com None

        # Apenas pega o ID da solicitação se houver uma pendente
        if status == 'sent_request':
            req = FriendRequest.objects.filter(from_user=request.user, to_user=su_user, is_active=True).first()
            if req:
                request_id = req.id
        elif status == 'received_request':
            req = FriendRequest.objects.filter(from_user=su_user, to_user=request.user, is_active=True).first()
            if req:
                request_id = req.id

        suggested_friends_with_status.append({
            'user': su_user,
            'status': status,
            'request_id': request_id # Passa o ID da solicitação aqui
        })


    context = {
        'form': form,
        'posts_data': posts_data_for_template,
        'friends_online': friends_online,
        'suggested_friends': suggested_friends_with_status,
    }
    return render(request, 'home.html', context)

@login_required
def delete_post(request, post_id):
    """
    View para deletar um post. Apenas o autor do post pode deletá-lo.
    """
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "Você não tem permissão para deletar este post.")
        return HttpResponseForbidden("Você não tem permissão para deletar este post.")

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deletado com sucesso!")
        return redirect('home')

    messages.error(request, "Método de requisição inválido para deletar o post.")
    return redirect('home')

@login_required
def add_comment_to_post(request, post_id):
    """
    View para adicionar um comentário a um post específico.
    """
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comentário adicionado com sucesso!")
            # Redireciona de volta para a página anterior (feed ou perfil do post)
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            messages.error(request, "Erro ao adicionar o comentário. Verifique o conteúdo.")
    messages.error(request, "Método de requisição inválido para adicionar comentário.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def like_post(request, post_id):
    """
    Adiciona ou remove um like de um post.
    """
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if request.method == 'POST':
        like_exists = Like.objects.filter(user=user, post=post).exists()

        if like_exists:
            Like.objects.filter(user=user, post=post).delete()
            messages.info(request, "Like removido.")
        else:
            Like.objects.create(user=user, post=post)
            messages.success(request, "Post curtido!")
    else:
        messages.error(request, "Método de requisição inválido para curtir o post.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def user_profile_view(request, username):
    """
    View para exibir o perfil de outro usuário.
    """
    profile_user = get_object_or_404(CustomUser, username=username)

    # Obtenha os posts deste usuário
    user_posts = Post.objects.filter(author=profile_user).order_by('-created_at')

    # Obtenha o status da amizade entre o usuário logado e o usuário do perfil
    friendship_status = get_friendship_status(request.user, profile_user)
    request_id = None # Inicializa com None

    # Se houver uma solicitação pendente, pegue o ID dela para os botões de ação
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
        'friendship_status': friendship_status, # 'friends', 'sent_request', 'received_request', 'not_friends', 'self'
        'request_id': request_id, # ID da solicitação de amizade pendente (se houver)
    }
    return render(request, 'accounts/user_profile.html', context) # Renderiza o template de perfil de usuário