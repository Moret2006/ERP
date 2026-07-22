"""
Cliente HTTP fino para a API v3 da Bling.

Host e paths confirmados contra a API real: as chamadas de dados vão por
`api.bling.com.br` (não `www.bling.com.br`, que serve só o fluxo OAuth) —
usar o host errado dá 403 "Acesso não permitido". `/contatos`, `/produtos` e
`/pedidos/vendas` respondem 200 com envelope `{"data": [...]}`.

Campos confirmados criando registros de teste reais na API:
- contato: id, nome, telefone, celular (sem email/endereço na listagem).
- produto: id, nome, preco, estoque.saldoVirtualTotal (estoque é objeto, não número).
- pedido (listagem): id, contato.id, contato.nome, situacao.id — SEM itens.
- pedido (detalhe, `GET /pedidos/vendas/{id}`): traz `itens[]` com
  descricao, quantidade, valor, produto.id.
"""
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from .models import BlingToken

AUTHORIZE_URL = 'https://www.bling.com.br/Api/v3/oauth/authorize'
TOKEN_URL = 'https://www.bling.com.br/Api/v3/oauth/token'
API_BASE_URL = 'https://api.bling.com.br/Api/v3'


class BlingConfigError(Exception):
    """BLING_CLIENT_ID/BLING_CLIENT_SECRET não configurados."""


class BlingNotConnectedError(Exception):
    """Ainda não existe um BlingToken salvo (fluxo OAuth não foi concluído)."""


def build_authorize_url(state):
    if not settings.BLING_CLIENT_ID or not settings.BLING_REDIRECT_URI:
        raise BlingConfigError('BLING_CLIENT_ID/BLING_REDIRECT_URI não configurados.')

    params = {
        'response_type': 'code',
        'client_id': settings.BLING_CLIENT_ID,
        'redirect_uri': settings.BLING_REDIRECT_URI,
        'state': state,
    }
    query = '&'.join(f'{key}={value}' for key, value in params.items())
    return f'{AUTHORIZE_URL}?{query}'


def exchange_code_for_token(code):
    if not settings.BLING_CLIENT_ID or not settings.BLING_CLIENT_SECRET:
        raise BlingConfigError('BLING_CLIENT_ID/BLING_CLIENT_SECRET não configurados.')

    response = requests.post(
        TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.BLING_REDIRECT_URI,
        },
        auth=(settings.BLING_CLIENT_ID, settings.BLING_CLIENT_SECRET),
        timeout=15,
    )
    response.raise_for_status()
    return _save_token(response.json())


def _save_token(payload):
    expires_at = timezone.now() + timedelta(seconds=payload['expires_in'])
    BlingToken.objects.all().delete()
    return BlingToken.objects.create(
        access_token=payload['access_token'],
        refresh_token=payload['refresh_token'],
        expires_at=expires_at,
    )


def _refresh_token(token):
    response = requests.post(
        TOKEN_URL,
        data={
            'grant_type': 'refresh_token',
            'refresh_token': token.refresh_token,
        },
        auth=(settings.BLING_CLIENT_ID, settings.BLING_CLIENT_SECRET),
        timeout=15,
    )
    response.raise_for_status()
    return _save_token(response.json())


class BlingClient:
    """
    Uso: BlingClient().listar_pedidos()
    Renova o token automaticamente via refresh_token quando expirado.
    """

    def __init__(self):
        token = BlingToken.objects.first()
        if token is None:
            raise BlingNotConnectedError(
                'Nenhum token salvo — conecte em /integracoes/bling/ primeiro.'
            )
        if token.expirado:
            token = _refresh_token(token)
        self._token = token

    def _get(self, path, params=None):
        response = requests.get(
            f'{API_BASE_URL}{path}',
            headers={'Authorization': f'Bearer {self._token.access_token}'},
            params=params or {},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def listar_pedidos(self):
        return self._get('/pedidos/vendas')

    def detalhar_pedido(self, pedido_id):
        # A listagem de /pedidos/vendas não traz `itens` — só o detalhe traz.
        return self._get(f'/pedidos/vendas/{pedido_id}')

    def listar_produtos(self):
        return self._get('/produtos')

    def listar_contatos(self):
        return self._get('/contatos')
