from django.core.management.base import BaseCommand

from bling.api import BlingClient, BlingNotConnectedError
from pedidos.models import Cliente, ItemPedido, Pedido, Produto


class Command(BaseCommand):
    help = 'Importa contatos, produtos e pedidos da Bling para o ERP local (upsert por bling_id).'

    def handle(self, *args, **options):
        try:
            client = BlingClient()
        except BlingNotConnectedError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        self._importar_contatos(client)
        self._importar_produtos(client)
        self._importar_pedidos(client)

    def _importar_contatos(self, client):
        # Formato confirmado em produção: {"data": [{id, nome, codigo, situacao,
        # numeroDocumento, telefone, celular}]}. O endpoint de listagem não traz
        # email/endereço — isso só vem no detalhe (GET /contatos/{id}), que não
        # buscamos aqui pra não multiplicar as chamadas em contas grandes.
        contatos = client.listar_contatos().get('data', [])
        criados = atualizados = 0
        for contato in contatos:
            bling_id = str(contato.get('id'))
            _, created = Cliente.objects.update_or_create(
                bling_id=bling_id,
                defaults={
                    'nome': contato.get('nome', ''),
                    'telefone': contato.get('telefone') or contato.get('celular') or '',
                },
            )
            criados += created
            atualizados += not created
        self.stdout.write(f'Contatos: {criados} criados, {atualizados} atualizados.')

    def _importar_produtos(self, client):
        # Formato confirmado em produção: {"data": [{id, nome, preco,
        # estoque: {saldoVirtualTotal}, tipo, situacao, formato, ...}]}.
        produtos = client.listar_produtos().get('data', [])
        criados = atualizados = 0
        for produto in produtos:
            bling_id = str(produto.get('id'))
            estoque = produto.get('estoque') or {}
            _, created = Produto.objects.update_or_create(
                bling_id=bling_id,
                defaults={
                    'nome': produto.get('nome', ''),
                    'preco_padrao': produto.get('preco', 0),
                    'estoque': estoque.get('saldoVirtualTotal', 0),
                },
            )
            criados += created
            atualizados += not created
        self.stdout.write(f'Produtos: {criados} criados, {atualizados} atualizados.')

    def _importar_pedidos(self, client):
        # A listagem de /pedidos/vendas não traz `itens` — só o detalhe
        # (GET /pedidos/vendas/{id}) traz. Formato confirmado em produção:
        # detalhe.itens = [{descricao, quantidade, valor, produto: {id}}].
        pedidos = client.listar_pedidos().get('data', [])
        criados = atualizados = 0
        for pedido_resumo in pedidos:
            bling_id = str(pedido_resumo.get('id'))
            contato_id = str(pedido_resumo.get('contato', {}).get('id', ''))
            cliente = Cliente.objects.filter(bling_id=contato_id).first()
            if cliente is None:
                continue

            pedido, created = Pedido.objects.update_or_create(
                bling_id=bling_id,
                defaults={'cliente': cliente},
            )
            criados += created
            atualizados += not created

            pedido_bling = client.detalhar_pedido(bling_id).get('data', {})
            for item in pedido_bling.get('itens', []):
                produto_id = str(item.get('produto', {}).get('id', ''))
                produto = Produto.objects.filter(bling_id=produto_id).first()
                ItemPedido.objects.update_or_create(
                    pedido=pedido,
                    produto=produto,
                    defaults={
                        'descricao': item.get('descricao', ''),
                        'quantidade': item.get('quantidade', 1),
                        'preco_unitario': item.get('valor', 0),
                    },
                )
        self.stdout.write(f'Pedidos: {criados} criados, {atualizados} atualizados.')
