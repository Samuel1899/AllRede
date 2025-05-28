# posts/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image'] # Adapte os campos conforme seu modelo Post
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título do seu post'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'O que você quer compartilhar?'}),
        }