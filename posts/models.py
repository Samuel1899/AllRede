# posts/models.py
from django.db import models
from django.conf import settings # Para referenciar o modelo de usuário personalizado

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='posts_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} by {self.author.username}'

# NOVO MODELO: Like
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garante que um usuário só possa dar um like por post
        unique_together = ('user', 'post')
        ordering = ['-created_at'] # Likes mais recentes primeiro (opcional)

    def __str__(self):
        return f'{self.user.username} liked {self.post.title}'