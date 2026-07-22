from decimal import Decimal

from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    bling_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    class Status(models.TextChoices):
        NOVO = 'novo', 'Novo'
        EM_PREPARACAO = 'em_preparacao', 'Em preparação'
        EM_ENTREGA = 'em_entrega', 'Em entrega'
        ENTREGUE = 'entregue', 'Entregue'
        CANCELADO = 'cancelado', 'Cancelado'

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOVO)
    observacoes = models.TextField(blank=True)
    bling_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f'Pedido #{self.pk} - {self.cliente}'

    @property
    def valor_total(self):
        return sum((item.subtotal for item in self.itens.all()), Decimal('0'))


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    preco_padrao = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)
    bling_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(
        Produto, on_delete=models.SET_NULL, null=True, blank=True, related_name='itens_pedido'
    )
    descricao = models.CharField(max_length=255)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantidade}x {self.descricao}'

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario
