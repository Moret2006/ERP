from django.contrib.auth.decorators import login_required
from django.shortcuts import render


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
    """
    Contexto do dashboard preparado para integração com o backend.
    Enquanto os módulos não existirem, listas ficam vazias e métricas como None
    para exibir skeletons no template.
    """
    return {
        'display_name': _display_name(user),
        'user_role': _user_role(user),
        'active_nav': 'dashboard',
        # Métricas superiores — substituir quando houver models/serviços
        'monthly_sales': None,
        'monthly_orders': None,
        'monthly_budgets': None,
        'total_clients': None,
        # Listas e gráficos
        'recent_orders': [],
        'sales_chart_labels': [],
        'sales_chart_values': [],
        'financial_summary': None,
        'best_selling_products': [],
        'upcoming_deliveries': [],
        # Rotas futuras — descomentar quando os apps existirem
        # 'url_new_order': reverse('pedidos:create'),
        # 'url_new_budget': reverse('orcamentos:create'),
        # 'url_orders_list': reverse('pedidos:list'),
    }


@login_required(login_url='login')
def dashboard_view(request):
    context = _dashboard_context(request.user)
    return render(request, 'dash/dashboard.html', context)
