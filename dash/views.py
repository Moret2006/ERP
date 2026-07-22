from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from pedidos.models import ItemPedido, Pedido

STATUS_BADGE_CLASS = {
    Pedido.Status.NOVO: 'blue',
    Pedido.Status.EM_PREPARACAO: 'yellow',
    Pedido.Status.EM_ENTREGA: 'blue',
    Pedido.Status.ENTREGUE: 'green',
    Pedido.Status.CANCELADO: 'gray',
}


def _order_row(pedido):
    return {
        'number': f'#{pedido.id}',
        'client': str(pedido.cliente),
        'description': ', '.join(item.descricao for item in pedido.itens.all()) or '—',
        'status_class': STATUS_BADGE_CLASS.get(pedido.status, 'gray'),
        'status_label': pedido.get_status_display(),
        'value': f'R$ {pedido.valor_total}',
        'date': timezone.localtime(pedido.criado_em).strftime('%d/%m/%Y'),
    }


def _dashboard_context():
    """
    Contexto do dashboard preparado para integração com o backend.
    Enquanto os módulos não existirem, listas ficam vazias e métricas como None
    para exibir skeletons no template.
    """
    recent_orders_qs = (
        Pedido.objects.select_related('cliente').prefetch_related('itens').order_by('-criado_em')[:5]
    )
    now = timezone.localtime()
    monthly_orders_count = Pedido.objects.filter(
        criado_em__year=now.year, criado_em__month=now.month
    ).count()

    best_selling_products = (
        ItemPedido.objects.filter(produto__isnull=False)
        .values('produto__nome')
        .annotate(total_quantidade=Sum('quantidade'))
        .order_by('-total_quantidade')[:5]
    )

    return {
        'active_nav': 'dashboard',
        # Métricas superiores — substituir quando houver models/serviços
        'monthly_sales': None,
        'monthly_orders': {'value': monthly_orders_count, 'subtitle': 'neste mês'} if monthly_orders_count else None,
        'monthly_budgets': None,
        'total_clients': None,
        # Listas e gráficos
        'recent_orders': [_order_row(pedido) for pedido in recent_orders_qs],
        'sales_chart_labels': [],
        'sales_chart_values': [],
        'financial_summary': None,
        'best_selling_products': [
            {'name': row['produto__nome'], 'quantity': row['total_quantidade']}
            for row in best_selling_products
        ],
        'upcoming_deliveries': [],
    }


@login_required(login_url='login')
def dashboard_view(request):
    context = _dashboard_context()
    return render(request, 'dash/dashboard.html', context)
