from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pedidos.selectors import obter_pedidos_recentes, obter_resumo_pedidos_mes


def _display_name(user):
    if user.get_full_name():
        return user.get_full_name()
    if user.first_name:
        return user.first_name
    return user.username.capitalize()


def _user_role(user):
    if user.is_superuser or user.is_staff:
        return 'Administração'
    return 'Operação'


def _dashboard_context(user):
    resumo_mes = obter_resumo_pedidos_mes()
    return {
        'display_name': _display_name(user),
        'user_role': _user_role(user),
        'active_nav': 'dashboard',
        'monthly_sales': None,
        'monthly_orders': {
            'value': resumo_mes['quantidade'],
            'subtitle': resumo_mes['valor_formatado'],
        },
        'monthly_budgets': None,
        'total_clients': None,
        'recent_orders': obter_pedidos_recentes(limite=5),
        'sales_chart_labels': [],
        'sales_chart_values': [],
        'financial_summary': None,
        'best_selling_products': [],
        'upcoming_deliveries': [],
    }


@login_required(login_url='login')
def dashboard_view(request):
    context = _dashboard_context(request.user)
    return render(request, 'dash/dashboard.html', context)
