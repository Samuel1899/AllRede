# posts/views_html.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post
from .forms import PostForm
from accounts.models import CustomUser # Importe CustomUser para as sugestões

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm # Se você tiver um PostForm para criar posts
from comments.forms import CommentForm # <-- Importe o CommentForm
from comments.models import Comment # <-- Importe o modelo Comment


@login_required
def post_list_create_view(request):
    posts = Post.objects.all().order_by('-created_at')

    # Lógica de sugestão de amigos: Pegando 5 usuários aleatórios que não sejam o logado.
    # Isso é para simular. Em um projeto real, você teria lógica de amizade/seguidores.
    suggested_friends = CustomUser.objects.exclude(id=request.user.id).order_by('?')[:5]


    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('home')
    else:
        form = PostForm()

    context = {
        'posts': posts,
        'form': form,
        'suggested_friends': suggested_friends, # Passando a lista de sugestões para o template
    }
    return render(request, 'home.html', context)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("Você não tem permissão para deletar este post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home') # Redireciona para a home após deletar

    return redirect('home')

# A view que já lista e permite criar posts (home_view, se for a sua)
# Adaptei para passar o CommentForm para cada post se quiser exibir em home.html
def post_list_create_view(request):
    if request.method == 'POST':
        # Assumindo que este formulário é para criar um NOVO POST
        form = PostForm(request.POST, request.FILES) # Adapte se o seu form tem uploads
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home') # Redireciona para a página inicial
    else:
        form = PostForm()

    posts = Post.objects.all().order_by('-created_at')

    # Para cada post, instancie um CommentForm
    # Isso permite que cada post na página inicial tenha seu próprio formulário de comentário
    posts_with_comments_forms = []
    for post in posts:
        # Acessa os comentários relacionados ao post usando o related_name 'comments'
        post_comments = post.comments.all()
        posts_with_comments_forms.append({
            'post': post,
            'comments': post_comments, # Adiciona os comentários existentes do post
            'comment_form': CommentForm(), # Cada post terá seu próprio formulário de comentário
        })

    context = {
        'form': form, # Formulário para criar novos posts
        'posts_data': posts_with_comments_forms, # Lista de posts com seus comentários e formulários
    }
    return render(request, 'home.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author: # Garante que apenas o autor pode deletar
        post.delete()
    return redirect('home') # Redireciona para o feed após a exclusão

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
            return redirect('home') # Ou redireciona para a página do post específico se houver
    # Se não for um POST válido, redireciona de volta para a home
    return redirect('home')