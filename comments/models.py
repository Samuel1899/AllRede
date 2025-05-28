# comments/models.py
from django.db import models
from django.conf import settings # Para referenciar o modelo de usuário personalizado
from posts.models import Post # Para vincular o comentário a um post

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Comentários mais antigos primeiro

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title[:30]}...'