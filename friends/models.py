# C:\Users\Meu computador\Desktop\AllRede\friends\models.py

from django.db import models
from django.conf import settings

class Friendship(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships_as_user')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships_as_friend')
    # Adicione o campo status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending') # Campo 'status' adicionado
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend') # Garante que não haja amizades duplicadas

    def __str__(self):
        return f"{self.user.username} is {self.status} with {self.friend.username}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_friend_requests')
    is_active = models.BooleanField(default=True) # Para controlar se a requisição ainda está pendente
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.from_user.username} to {self.to_user.username}"

    # Métodos para aceitar e recusar (opcional, pode ser feito na view)
    def accept(self):
        # Cria a amizade com status 'accepted' em ambas as direções
        # Verifica se a amizade já existe antes de criar
        if not Friendship.objects.filter(user=self.from_user, friend=self.to_user, status='accepted').exists():
            Friendship.objects.create(user=self.from_user, friend=self.to_user, status='accepted')
        if not Friendship.objects.filter(user=self.to_user, friend=self.from_user, status='accepted').exists():
            Friendship.objects.create(user=self.to_user, friend=self.from_user, status='accepted')
        self.is_active = False # Desativa a requisição
        self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()