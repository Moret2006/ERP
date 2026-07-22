from django.db import models
from django.utils import timezone


class BlingToken(models.Model):
    """
    Guarda o token OAuth2 atual da conexão com a Bling.
    Singleton simples: só deve existir uma linha (a mais recente é a válida).
    """

    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Token Bling (expira em {self.expires_at:%d/%m/%Y %H:%M})'

    @property
    def expirado(self):
        return timezone.now() >= self.expires_at
