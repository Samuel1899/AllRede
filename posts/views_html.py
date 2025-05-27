# posts/views_html.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post
from .forms import PostForm
from accounts.models import CustomUser # Importe CustomUser para as sugestões


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