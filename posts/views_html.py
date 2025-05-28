# posts/views_html.py

# Importações necessárias
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden # Para a view delete_post

# Importações dos modelos e formulários dos seus apps
from .models import Post, Like # Importe Post e Like
from .forms import PostForm # Importe o PostForm
from comments.forms import CommentForm # Importe o CommentForm
from comments.models import Comment # Importe o modelo Comment
from accounts.models import CustomUser # Importe CustomUser para sugestões de amigos

# =====================================================================
# Views HTML
# =====================================================================

@login_required
def post_list_create_view(request):
    """
    View para listar todos os posts e permitir a criação de novos posts.
    Também prepara dados para comentários e likes.
    """
    # Lógica para criar um novo post (se o request for POST)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('home') # Redireciona para a página inicial após criar o post
    else:
        form = PostForm() # Instancia um formulário vazio para GET requests

    # Otimização: pré-carrega os autores dos posts, os autores dos comentários e os usuários dos likes.
    # Isso reduz o número de consultas ao banco de dados (evita N+1 queries).
    posts = Post.objects.select_related('author').prefetch_related('comments__author', 'likes__user').all().order_by('-created_at')

    posts_data_for_template = []
    for post in posts:
        post_comments = post.comments.all() # Acessa os comentários relacionados ao post

        # Verifica se o usuário logado já curtiu este post
        user_has_liked = False
        if request.user.is_authenticated:
            # 'post.likes.all()' agora é eficiente devido ao prefetch_related
            user_has_liked = any(like.user == request.user for like in post.likes.all())

        posts_data_for_template.append({
            'post': post,
            'comments': post_comments,
            'comment_form': CommentForm(), # Cada post terá seu próprio formulário de comentário
            'user_has_liked': user_has_liked, # Informa se o usuário logado curtiu este post
        })

    # Lógica de sugestão de amigos: Pegando 5 usuários aleatórios que não sejam o logado.
    # Para que a lista de amigos/sugestões apareça vazia por padrão, defina como []
    # Se você tiver uma lógica real de amizade, substitua por ela.
    friends_online = [] # Lista vazia para "Amigos Online"
    suggested_friends = CustomUser.objects.exclude(id=request.user.id).order_by('?')[:5] # Exemplo de sugestões reais de 5 usuários

    context = {
        'form': form, # Formulário para criar novos posts (no topo da página)
        'posts_data': posts_data_for_template, # Lista de posts com seus comentários, formulários e status de like
        'friends_online': friends_online,       # Passando lista de amigos online (vazia ou com dados reais)
        'suggested_friends': suggested_friends, # Passando lista de sugestões de amigos
    }
    return render(request, 'home.html', context)


@login_required
def delete_post(request, post_id):
    """
    View para deletar um post. Apenas o autor do post pode deletá-lo.
    """
    post = get_object_or_404(Post, id=post_id)

    # Garante que apenas o autor do post pode deletá-lo
    if post.author != request.user:
        return HttpResponseForbidden("Você não tem permissão para deletar este post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home') # Redireciona para a home após deletar

    # Se a requisição não for POST, apenas redireciona para a home
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
            # Redireciona de volta para a página anterior (feed) ou para a home
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    # Se não for um POST válido, ou se o método não for POST, redireciona de volta para a home
    return redirect('home')


@login_required
def like_post(request, post_id):
    """
    Adiciona ou remove um like de um post.
    """
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # Verifica se o usuário já curtiu este post
    like_exists = Like.objects.filter(user=user, post=post).exists()

    if like_exists:
        # Se já curtiu, descurte (remove o like)
        Like.objects.filter(user=user, post=post).delete()
    else:
        # Se não curtiu, curta (adiciona o like)
        Like.objects.create(user=user, post=post)

    # Redireciona de volta para a página anterior ou para a home
    # Usar request.META.get('HTTP_REFERER') é útil para voltar de onde veio
    return redirect(request.META.get('HTTP_REFERER', 'home'))