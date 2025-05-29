# C:\Users\Meu computador\Desktop\AllRede\accounts\forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'avatar', 'bio',) # Adicione campos personalizados

class CustomUserChangeForm(UserChangeForm):
    password = None # Não permitir mudança de senha aqui, usar view separada para isso se necessário

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'avatar', 'bio') # Campos que podem ser editados no perfil