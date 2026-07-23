from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import Pedido


def formatar_moeda(value):
    value = value or Decimal('0.00')
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def obter_pedidos_recentes(limite=5):
    """Retorna os pedidos mais recentes (mesma fonte da aba Pedidos)."""
    return Pedido.objects.order_by('-data_criacao')[:limite]


def obter_resumo_pedidos_mes(referencia=None):
    """
    Quantidade e valor total dos pedidos criados no mês corrente
    (respeitando o fuso horário do Django).
    """
    hoje = referencia or timezone.localdate()
    agregados = Pedido.objects.filter(
        data_criacao__year=hoje.year,
        data_criacao__month=hoje.month,
    ).aggregate(
        quantidade=Count('id'),
        valor=Coalesce(Sum('valor_total'), Decimal('0.00')),
    )
    quantidade = agregados['quantidade'] or 0
    valor = agregados['valor'] or Decimal('0.00')
    return {
        'quantidade': quantidade,
        'valor': valor,
        'valor_formatado': formatar_moeda(valor),
    }
