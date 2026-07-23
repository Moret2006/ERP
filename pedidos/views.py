from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from dash.views import _display_name, _user_role

from .forms import AlterarStatusForm, ItemPedidoFormSet, PedidoForm
from .models import Pedido, StatusPedido
from .selectors import formatar_moeda, obter_pedidos_recentes

RECENTES_LIMIT = 10


def _layout_context(user, active_nav='pedidos'):
    return {
        'display_name': _display_name(user),
        'user_role': _user_role(user),
        'active_nav': active_nav,
    }


def _format_currency(value):
    return formatar_moeda(value)


def _percent(part, total):
    if not total:
        return 0.0
    return round((part / total) * 100, 1)


def _build_resumo(hoje):
    agregados = Pedido.objects.aggregate(
        pedidos_do_dia_qtd=Count('id', filter=Q(data_criacao__date=hoje)),
        pedidos_do_dia_valor=Coalesce(
            Sum('valor_total', filter=Q(data_criacao__date=hoje)),
            Decimal('0.00'),
        ),
        em_andamento_qtd=Count('id', filter=Q(status=StatusPedido.EM_ANDAMENTO)),
        em_andamento_valor=Coalesce(
            Sum('valor_total', filter=Q(status=StatusPedido.EM_ANDAMENTO)),
            Decimal('0.00'),
        ),
        concluidos_qtd=Count('id', filter=Q(status=StatusPedido.CONCLUIDO)),
        concluidos_valor=Coalesce(
            Sum('valor_total', filter=Q(status=StatusPedido.CONCLUIDO)),
            Decimal('0.00'),
        ),
        cancelados_qtd=Count('id', filter=Q(status=StatusPedido.CANCELADO)),
        cancelados_valor=Coalesce(
            Sum('valor_total', filter=Q(status=StatusPedido.CANCELADO)),
            Decimal('0.00'),
        ),
    )

    return {
        'pedidos_do_dia': {
            'quantidade': agregados['pedidos_do_dia_qtd'],
            'valor': agregados['pedidos_do_dia_valor'],
            'valor_formatado': _format_currency(agregados['pedidos_do_dia_valor']),
        },
        'em_andamento': {
            'quantidade': agregados['em_andamento_qtd'],
            'valor': agregados['em_andamento_valor'],
            'valor_formatado': _format_currency(agregados['em_andamento_valor']),
        },
        'concluidos': {
            'quantidade': agregados['concluidos_qtd'],
            'valor': agregados['concluidos_valor'],
            'valor_formatado': _format_currency(agregados['concluidos_valor']),
        },
        'cancelados': {
            'quantidade': agregados['cancelados_qtd'],
            'valor': agregados['cancelados_valor'],
            'valor_formatado': _format_currency(agregados['cancelados_valor']),
        },
    }


def _build_status_context():
    totais = Pedido.objects.aggregate(
        total=Count('id'),
        concluido=Count('id', filter=Q(status=StatusPedido.CONCLUIDO)),
        em_andamento=Count('id', filter=Q(status=StatusPedido.EM_ANDAMENTO)),
        cancelado=Count('id', filter=Q(status=StatusPedido.CANCELADO)),
        aguardando=Count('id', filter=Q(status=StatusPedido.AGUARDANDO)),
    )

    total = totais['total'] or 0
    status_pedidos = {
        'concluidos': {
            'quantidade': totais['concluido'],
            'percentual': _percent(totais['concluido'], total),
        },
        'em_andamento': {
            'quantidade': totais['em_andamento'],
            'percentual': _percent(totais['em_andamento'], total),
        },
        'cancelados': {
            'quantidade': totais['cancelado'],
            'percentual': _percent(totais['cancelado'], total),
        },
        'aguardando': {
            'quantidade': totais['aguardando'],
            'percentual': _percent(totais['aguardando'], total),
        },
    }

    taxa_conclusao = _percent(totais['concluido'], total)
    status_chart_data = {
        'labels': ['Concluídos', 'Em andamento', 'Cancelados', 'Aguardando'],
        'values': [
            status_pedidos['concluidos']['quantidade'],
            status_pedidos['em_andamento']['quantidade'],
            status_pedidos['cancelados']['quantidade'],
            status_pedidos['aguardando']['quantidade'],
        ],
        'colors': ['#2e9e6a', '#0099d6', '#ff2f78', '#e67e22'],
        'total': total,
    }

    return {
        'status_pedidos': status_pedidos,
        'total_pedidos': total,
        'taxa_conclusao': taxa_conclusao,
        'status_chart_data': status_chart_data,
    }


@login_required(login_url='login')
def dashboard_pedidos(request):
    hoje = timezone.localdate()
    context = {
        **_layout_context(request.user),
        'pedidos_recentes': obter_pedidos_recentes(limite=RECENTES_LIMIT),
        'resumo': _build_resumo(hoje),
        **_build_status_context(),
    }
    return render(request, 'pedidos/dashboard_pedidos.html', context)


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def criar_pedido(request):
    pedido = Pedido()
    form = PedidoForm(request.POST or None)
    formset = ItemPedidoFormSet(request.POST or None, instance=pedido, prefix='itens')

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            pedido = form.save(commit=False)
            pedido.numero = Pedido.gerar_numero()
            pedido.criado_por = request.user
            pedido.save()
            formset.instance = pedido
            formset.save()
            pedido.recalcular_valor_total()

        messages.success(request, f'Pedido {pedido.numero} cadastrado com sucesso.')
        return redirect('pedidos:dashboard')

    context = {
        **_layout_context(request.user),
        'form': form,
        'formset': formset,
        'page_title': 'Adicionar Pedido',
        'submit_label': 'Salvar pedido',
        'cancel_url': reverse('pedidos:dashboard'),
    }
    return render(request, 'pedidos/formulario_pedido.html', context)


@login_required(login_url='login')
def detalhar_pedido(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('itens'),
        pk=pk,
    )
    context = {
        **_layout_context(request.user),
        'pedido': pedido,
        'status_form': AlterarStatusForm(initial={'status': pedido.status}),
    }
    return render(request, 'pedidos/detalhe_pedido.html', context)


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoForm(request.POST or None, instance=pedido)
    formset = ItemPedidoFormSet(request.POST or None, instance=pedido, prefix='itens')

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            form.save()
            formset.save()
            pedido.recalcular_valor_total()

        messages.success(request, f'Pedido {pedido.numero} atualizado com sucesso.')
        return redirect('pedidos:detalhar', pk=pedido.pk)

    context = {
        **_layout_context(request.user),
        'form': form,
        'formset': formset,
        'pedido': pedido,
        'page_title': f'Editar Pedido {pedido.numero}',
        'submit_label': 'Salvar alterações',
        'cancel_url': reverse('pedidos:detalhar', kwargs={'pk': pedido.pk}),
    }
    return render(request, 'pedidos/formulario_pedido.html', context)


@login_required(login_url='login')
@require_POST
def alterar_status_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = AlterarStatusForm(request.POST)
    if form.is_valid():
        pedido.status = form.cleaned_data['status']
        pedido.save(update_fields=['status', 'data_atualizacao'])
        messages.success(request, f'Status do pedido {pedido.numero} atualizado.')
    else:
        messages.error(request, 'Não foi possível alterar o status do pedido.')
    return redirect(request.POST.get('next') or reverse('pedidos:detalhar', kwargs={'pk': pk}))


@login_required(login_url='login')
@require_POST
def cancelar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.status != StatusPedido.CANCELADO:
        pedido.status = StatusPedido.CANCELADO
        pedido.save(update_fields=['status', 'data_atualizacao'])
        messages.success(request, f'Pedido {pedido.numero} cancelado.')
    return redirect(request.POST.get('next') or reverse('pedidos:dashboard'))


@login_required(login_url='login')
@require_POST
def excluir_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    numero = pedido.numero
    pedido.delete()
    messages.success(request, f'Pedido {numero} excluído.')
    return redirect('pedidos:dashboard')
