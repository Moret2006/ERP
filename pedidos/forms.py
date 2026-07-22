from django.forms import inlineformset_factory
from django import forms

from .models import Cliente, ItemPedido, Pedido, Produto


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'endereco']


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'preco_padrao', 'estoque', 'ativo']


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'status', 'observacoes']


class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'descricao', 'quantidade', 'preco_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produto'].queryset = Produto.objects.filter(ativo=True)
        self.fields['produto'].required = False
        self.fields['produto'].widget.attrs['class'] = 'item-produto-select'
        # Evita que a linha extra vazia seja tratada como "alterada" só por
        # comparação com o default do model (quantidade=1) quando o usuário
        # não preencheu nada nela.
        self.fields['quantidade'].initial = None


ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    form=ItemPedidoForm,
    extra=1,
    can_delete=True,
)
