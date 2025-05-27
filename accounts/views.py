# accounts/views.py (ou accounts/views_html.py)

from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .forms import CustomUserCreationForm
from .models import CustomUser
from .serializers import RegisterSerializer
from posts.models import Post # IMPORTANTE: Esta importação é necessária para a profile_view

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm # Importe o formulário que você acabou de criar

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

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'

@login_required
def profile_view(request):
    # Pega todos os posts do usuário logado, ordenados pelo mais recente
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    context = {
        'user_posts': user_posts,
        'user': request.user # O objeto 'user' já está disponível no template por padrão, mas passá-lo explicitamente não faz mal
    }
    return render(request, 'profile.html', context)
@login_required
def register_view(request):
    # ... (sua view de registro existente) ...
    pass # Deixe o conteúdo original aqui

@login_required
def profile_view(request):
    if request.method == 'POST':
        # O formulário precisa da instância do usuário para preencher os campos existentes
        # e do request.FILES para lidar com o upload de arquivos
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile') # Redireciona para o próprio perfil após salvar
    else:
        form = UserProfileForm(instance=request.user) # Preenche o formulário com dados do usuário logado

    context = {
        'form': form,
    }
    return render(request, 'profile.html', context)