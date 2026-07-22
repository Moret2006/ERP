from django.contrib import admin

from .models import Cliente, ItemPedido, Pedido, Produto


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone', 'criado_em']
    search_fields = ['nome', 'email']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco_padrao', 'estoque', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'status', 'valor_total', 'criado_em']
    list_filter = ['status']
    search_fields = ['cliente__nome']
    inlines = [ItemPedidoInline]
