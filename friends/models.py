# friends/models.py

from django.db import models
from django.conf import settings # Para referenciar o modelo de usuário padrão (CustomUser)

class FriendRequest(models.Model):
    """
    Modelo para representar uma solicitação de amizade.
    """
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) # Para indicar se a solicitação ainda está pendente

    class Meta:
        # Garante que um usuário não possa enviar uma solicitação de amizade duplicada para o mesmo usuário
        # E que não possa enviar para si mesmo (embora a view também trate isso)
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"De {self.from_user.username} para {self.to_user.username}"

    def accept(self):
        """
        Aceita a solicitação de amizade e cria o relacionamento de amizade bidirecional.
        """
        Friendship.objects.create(user=self.from_user, friend=self.to_user)
        Friendship.objects.create(user=self.to_user, friend=self.from_user)
        self.is_active = False # Marca a solicitação como inativa/resolvida
        self.save()
        return True

    def decline(self):
        """
        Recusa a solicitação de amizade.
        """
        self.is_active = False
        self.save()
        return False

    def cancel(self):
        """
        Cancela a solicitação de amizade enviada (pelo remetente).
        """
        self.is_active = False
        self.save()
        return False


class Friendship(models.Model):
    """
    Modelo para representar um relacionamento de amizade bidirecional.
    (A -> B e B -> A). Usamos dois objetos Friendship para facilitar consultas.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships', on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='_friend_of', on_delete=models.CASCADE) # _friend_of para evitar conflito com 'friendships'

    class Meta:
        # Garante que não haja duplicatas (user, friend)
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} é amigo de {self.friend.username}"