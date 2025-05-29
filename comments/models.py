# C:\Users\Meu computador\Desktop\AllRede\comments\models.py (EXEMPLO - APENAS SE EXISTIR)

from django.db import models
from django.conf import settings
from posts.models import Post # Importar Post do aplicativo 'posts'

class Comment(models.Model):
    # ATENÇÃO: related_name DIFERENTES dos usados em posts/models.py
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments_module_comments_on_post') # related_name único
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments_module_comments_by_user') # related_name único
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on Post ID {self.post.id} (from comments app)"