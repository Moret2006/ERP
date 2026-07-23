from decimal import Decimal, InvalidOperation

from django import forms
from django.forms import inlineformset_factory

from .models import ItemPedido, Pedido, StatusPedido


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'descricao', 'status', 'data_entrega', 'observacoes']
        widgets = {
            'cliente': forms.TextInput(attrs={
                'class': 'form-field__input',
                'placeholder': 'Nome do cliente',
                'autocomplete': 'name',
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-field__input',
                'placeholder': 'Resumo do pedido',
            }),
            'status': forms.Select(attrs={'class': 'form-field__input'}),
            'data_entrega': forms.DateInput(attrs={
                'class': 'form-field__input',
                'type': 'date',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-field__input form-field__textarea',
                'rows': 3,
                'placeholder': 'Observações adicionais (opcional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = StatusPedido.choices
        self.fields['data_entrega'].required = False
        self.fields['observacoes'].required = False


class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'descricao', 'quantidade', 'valor_unitario']
        widgets = {
            'produto': forms.TextInput(attrs={
                'class': 'form-field__input',
                'placeholder': 'Produto (opcional)',
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-field__input',
                'placeholder': 'Descrição do item',
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-field__input',
                'min': 1,
                'value': 1,
            }),
            'valor_unitario': forms.NumberInput(attrs={
                'class': 'form-field__input',
                'min': '0',
                'step': '0.01',
                'placeholder': '0,00',
            }),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is None or quantidade < 1:
            raise forms.ValidationError('Informe uma quantidade válida.')
        return quantidade

    def clean_valor_unitario(self):
        valor = self.cleaned_data.get('valor_unitario')
        if valor is None:
            raise forms.ValidationError('Informe o valor unitário.')
        try:
            valor = Decimal(valor)
        except (InvalidOperation, TypeError):
            raise forms.ValidationError('Valor unitário inválido.')
        if valor < 0:
            raise forms.ValidationError('O valor unitário não pode ser negativo.')
        return valor


ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    form=ItemPedidoForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class AlterarStatusForm(forms.Form):
    status = forms.ChoiceField(choices=StatusPedido.choices)
