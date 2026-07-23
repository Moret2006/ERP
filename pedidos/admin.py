from django.contrib import admin

from .models import ItemPedido, Pedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'cliente',
        'status',
        'valor_total',
        'data_criacao',
        'data_entrega',
        'criado_por',
    )
    list_filter = ('status', 'data_criacao')
    search_fields = ('numero', 'cliente', 'descricao')
    readonly_fields = ('numero', 'valor_total', 'data_criacao', 'data_atualizacao')
    inlines = [ItemPedidoInline]
