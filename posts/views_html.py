# posts/views_html.py

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q # <--- ESSA IMPORTAÇÃO É NECESSÁRIA PARA USAR Q
from .models import Post, Like
from comments.models import Comment
from django.contrib.auth import get_user_model
from friends.models import Friendship, FriendRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def post_list_create_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        if not content and not image:
            messages.error(request, "A publicação não pode estar vazia.")
            return redirect('home')

        Post.objects.create(author=request.user, title=title, content=content, image=image)
        messages.success(request, "Publicação criada com sucesso!")
        return redirect('home')

    CustomUser = get_user_model()

    friends_as_user = Friendship.objects.filter(user=request.user).values_list('friend__id', flat=True)
    friends_as_friend = Friendship.objects.filter(friend=request.user).values_list('user__id', flat=True)
    user_friends_ids = list(set(list(friends_as_user) + list(friends_as_friend)))
    
    posts = Post.objects.filter(
        Q(author=request.user) | Q(author__id__in=user_friends_ids)
    ).order_by('-created_at')

    paginator = Paginator(posts, 10)
    page = request.GET.get('page')

    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)

    posts_data = []
    for post in posts_page:
        user_has_liked = post.likes.filter(user=request.user).exists()
        comments = Comment.objects.filter(post=post).order_by('created_at')
        posts_data.append({
            'post': post,
            'user_has_liked': user_has_liked,
            'comments': comments
        })

    current_user_profile = request.user

    online_friends = CustomUser.objects.filter(id__in=user_friends_ids).order_by('username')

    all_related_users_ids = set(user_friends_ids)
    all_related_users_ids.add(request.user.id)

    pending_sent_requests = FriendRequest.objects.filter(from_user=request.user, is_active=True).values_list('to_user__id', flat=True)
    pending_received_requests = FriendRequest.objects.filter(to_user=request.user, is_active=True).values_list('from_user__id', flat=True)

    all_related_users_ids.update(pending_sent_requests)
    all_related_users_ids.update(pending_received_requests)

    suggested_friends = CustomUser.objects.exclude(id__in=list(all_related_users_ids)).order_by('?')[:5]

    context = {
        'posts_data': posts_data,
        'current_user_profile': current_user_profile,
        'online_friends': online_friends,
        'suggested_friends': suggested_friends,
    }
    return render(request, 'home.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Publicação excluída com sucesso!")
    return redirect('home')

@login_required
def add_comment_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
            messages.success(request, "Comentário adicionado com sucesso!")
        else:
            messages.error(request, "O comentário não pode estar vazio.")
    return redirect('home')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        messages.info(request, "Você descurtiu a publicação.")
    else:
        messages.success(request, "Você curtiu a publicação!")
    return redirect('home')

def user_profile_view(request, username):
    CustomUser = get_user_model()
    user_to_view = get_object_or_404(CustomUser, username=username)
    user_posts = Post.objects.filter(author=user_to_view).order_by('-created_at')

    friend_status = None
    if request.user.is_authenticated and request.user != user_to_view:
        are_friends = Friendship.objects.filter(
            Q(user=request.user, friend=user_to_view) | Q(user=user_to_view, friend=request.user)
        ).exists()
        
        if are_friends:
            friend_status = 'friends'
        else:
            sent_request = FriendRequest.objects.filter(
                from_user=request.user, to_user=user_to_view, is_active=True
            ).exists()
            received_request = FriendRequest.objects.filter(
                from_user=user_to_view, to_user=request.user, is_active=True
            ).exists()

            if sent_request:
                friend_status = 'request_sent'
            elif received_request:
                friend_status = 'request_received'
            else:
                friend_status = 'not_friends'

    context = {
        'user_to_view': user_to_view,
        'user_posts': user_posts,
        'friend_status': friend_status,
    }
    return render(request, 'profile.html', context)