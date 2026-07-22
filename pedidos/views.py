from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm, ItemPedidoFormSet, PedidoForm, ProdutoForm
from .models import Cliente, Pedido, Produto


@login_required(login_url='login')
def pedidos_list_view(request):
    pedidos = Pedido.objects.select_related('cliente').prefetch_related('itens')
    paginator = Paginator(pedidos, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'active_nav': 'pedidos',
        'page_obj': page_obj,
    }
    return render(request, 'pedidos/list.html', context)


@login_required(login_url='login')
def pedido_form_view(request, pk=None):
    pedido = get_object_or_404(Pedido, pk=pk) if pk else None

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        formset = ItemPedidoFormSet(request.POST, instance=pedido or Pedido())

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                pedido = form.save()
                formset.instance = pedido
                formset.save()
            messages.success(request, 'Pedido salvo com sucesso.')
            return redirect('pedidos:list')
    else:
        form = PedidoForm(instance=pedido)
        formset = ItemPedidoFormSet(instance=pedido)

    context = {
        'active_nav': 'pedidos',
        'form': form,
        'formset': formset,
        'pedido': pedido,
    }
    return render(request, 'pedidos/pedido_form.html', context)


@login_required(login_url='login')
def clientes_list_view(request):
    clientes = Cliente.objects.all()
    paginator = Paginator(clientes, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'active_nav': 'clientes',
        'page_obj': page_obj,
    }
    return render(request, 'pedidos/clientes_list.html', context)


@login_required(login_url='login')
def cliente_form_view(request, pk=None):
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente salvo com sucesso.')
            return redirect('pedidos:clientes_list')
    else:
        form = ClienteForm(instance=cliente)

    context = {
        'active_nav': 'clientes',
        'form': form,
        'cliente': cliente,
    }
    return render(request, 'pedidos/cliente_form.html', context)


@login_required(login_url='login')
def produtos_list_view(request):
    produtos = Produto.objects.all()
    paginator = Paginator(produtos, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'active_nav': 'produtos',
        'page_obj': page_obj,
    }
    return render(request, 'pedidos/produtos_list.html', context)


@login_required(login_url='login')
def produto_form_view(request, pk=None):
    produto = get_object_or_404(Produto, pk=pk) if pk else None

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto salvo com sucesso.')
            return redirect('pedidos:produtos_list')
    else:
        form = ProdutoForm(instance=produto)

    context = {
        'active_nav': 'produtos',
        'form': form,
        'produto': produto,
    }
    return render(request, 'pedidos/produto_form.html', context)


@login_required(login_url='login')
def produtos_json_view(request):
    produtos = Produto.objects.filter(ativo=True).values('id', 'nome', 'preco_padrao')
    return JsonResponse(list(produtos), safe=False)
