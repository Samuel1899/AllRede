# posts/forms.py

from django import forms
from .models import Post, Comment # Certifique-se de que Comment está importado

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título (Opcional)'}),
            'content': forms.Textarea(attrs={'placeholder': 'O que está pensando?', 'rows': 4}),
        }

# ADICIONE ESTA CLASSE para o formulário de comentário
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Adicione um comentário...', 'rows': 2}),
        }