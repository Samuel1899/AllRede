# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',) # Adicione email, ou outros campos que desejar no registro

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar', 'bio'] # Campos que o usuário poderá editar no perfil