# C:\Users\Meu computador\Desktop\AllRede\posts\views_html.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import get_user_model 

from .forms import PostForm, CommentForm
from .models import Post, Comment
from accounts.models import CustomUser 
from friends.models import Friendship, FriendRequest 


@login_required
def post_list_create_view(request):
    form = PostForm()
    comment_form = CommentForm() 

    if request.method == 'POST':
        if 'content' in request.POST or 'image' in request.FILES:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                messages.success(request, "Publicação criada com sucesso!")
                return redirect('home')
            else:
                messages.error(request, "Erro ao criar a publicação. Verifique os campos.")

    # Lógica para buscar posts:
    user_friends_ids = []
    if request.user.is_authenticated:
        # Obter IDs dos amigos do usuário logado com status 'accepted'
        # Corrigido o filtro para incluir 'status'
        friends_as_user = Friendship.objects.filter(user=request.user, status='accepted').values_list('friend__id', flat=True)
        friends_as_friend = Friendship.objects.filter(friend=request.user, status='accepted').values_list('user__id', flat=True)
        user_friends_ids = list(set(list(friends_as_user) + list(friends_as_friend)))
    
    # Incluir os próprios posts do usuário e posts de amigos
    author_ids = user_friends_ids + [request.user.id] if request.user.is_authenticated else []
    
    # Buscar posts dos autores relevantes (usuário e amigos)
    all_posts = Post.objects.filter(author__id__in=author_ids).order_by('-created_at')

    posts_data = []
    for post in all_posts:
        comments = Comment.objects.filter(post=post).order_by('created_at')
        
        user_has_liked = False
        if request.user.is_authenticated:
            # Acessar a lista de likes corretamente
            user_has_liked = post.likes.filter(id=request.user.id).exists()

        posts_data.append({
            'post': post,
            'comments': comments,
            'comment_form': CommentForm(), # Nova instância para cada post no template
            'user_has_liked': user_has_liked,
        })

    # Paginação
    paginator = Paginator(posts_data, 10)
    page_number = request.GET.get('page')
    try:
        posts_page = paginator.page(page_number)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)

    # Lógica para a barra lateral (Amigos Online, Sugestões de Amizade)
    current_user_profile = request.user 

    online_friends = CustomUser.objects.filter(id__in=user_friends_ids).order_by('username')

    all_related_users_ids = set(user_friends_ids)
    if request.user.is_authenticated:
        all_related_users_ids.add(request.user.id)

        pending_sent_requests = FriendRequest.objects.filter(from_user=request.user, is_active=True).values_list('to_user__id', flat=True)
        pending_received_requests = FriendRequest.objects.filter(to_user=request.user, is_active=True).values_list('from_user__id', flat=True)

        all_related_users_ids.update(pending_sent_requests)
        all_related_users_ids.update(pending_received_requests)

    suggested_friends = CustomUser.objects.exclude(id__in=list(all_related_users_ids)).order_by('?')[:5]

    context = {
        'form': form,
        'comment_form': comment_form, # Este é o formulário geral, mas o de cada post é passado em posts_data
        'posts_data': posts_page,
        'posts_page': posts_page,
        'current_user_profile': current_user_profile,
        'online_friends': online_friends,
        'suggested_friends': suggested_friends,
    }
    return render(request, 'home.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
        messages.success(request, "Publicação excluída com sucesso!")
    else:
        messages.error(request, "Você não tem permissão para excluir esta publicação.")
    return redirect('home')

@login_required
def add_comment_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comentário adicionado!")
        else:
            messages.error(request, "Erro ao adicionar comentário.")
    return redirect('home') # Ou redirect('post_detail', post_id=post.id) se tiver

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        messages.info(request, "Você descurtiu a publicação.")
    else:
        post.likes.add(request.user)
        messages.success(request, "Você curtiu a publicação!")
    return redirect('home') # Ou redirect('post_detail', post_id=post.id) se tiver