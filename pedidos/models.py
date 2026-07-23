from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class StatusPedido(models.TextChoices):
    AGUARDANDO = 'aguardando', 'Aguardando'
    EM_ANDAMENTO = 'em_andamento', 'Em andamento'
    CONCLUIDO = 'concluido', 'Concluído'
    CANCELADO = 'cancelado', 'Cancelado'


class Pedido(models.Model):
    numero = models.CharField('Número', max_length=20, unique=True, editable=False)
    cliente = models.CharField('Cliente', max_length=200)
    descricao = models.CharField('Descrição', max_length=255)
    status = models.CharField(
        'Status',
        max_length=20,
        choices=StatusPedido.choices,
        default=StatusPedido.AGUARDANDO,
        db_index=True,
    )
    valor_total = models.DecimalField(
        'Valor total',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    data_criacao = models.DateTimeField('Data de criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de atualização', auto_now=True)
    data_entrega = models.DateField('Data de entrega', null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_criados',
        verbose_name='Criado por',
    )

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'{self.numero} — {self.cliente}'

    @property
    def status_badge_class(self):
        return {
            StatusPedido.AGUARDANDO: 'orange',
            StatusPedido.EM_ANDAMENTO: 'blue',
            StatusPedido.CONCLUIDO: 'green',
            StatusPedido.CANCELADO: 'pink',
        }.get(self.status, 'orange')

    @property
    def valor_formatado(self):
        value = self.valor_total or Decimal('0.00')
        return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    @classmethod
    def gerar_numero(cls):
        """Gera número único no formato PED-YYYYMMDD-XXXX."""
        prefixo = f'PED-{timezone.localdate().strftime("%Y%m%d")}-'
        with transaction.atomic():
            ultimo = (
                cls.objects.select_for_update()
                .filter(numero__startswith=prefixo)
                .order_by('-numero')
                .values_list('numero', flat=True)
                .first()
            )
            sequencia = 1
            if ultimo:
                try:
                    sequencia = int(ultimo.rsplit('-', 1)[-1]) + 1
                except ValueError:
                    sequencia = 1
            return f'{prefixo}{sequencia:04d}'

    def recalcular_valor_total(self, save=True):
        total = self.itens.aggregate(total=models.Sum('subtotal'))['total'] or Decimal('0.00')
        self.valor_total = total
        if save:
            self.save(update_fields=['valor_total', 'data_atualizacao'])
        return total


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Pedido',
    )
    produto = models.CharField('Produto', max_length=200, blank=True)
    descricao = models.CharField('Descrição', max_length=255)
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    valor_unitario = models.DecimalField('Valor unitário', max_digits=12, decimal_places=2)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, editable=False)

    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'

    def __str__(self):
        return f'{self.descricao} ({self.quantidade}x)'

    def save(self, *args, **kwargs):
        self.subtotal = (self.valor_unitario or Decimal('0.00')) * self.quantidade
        super().save(*args, **kwargs)
