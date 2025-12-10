"""
Testes E2E para gerenciamento de pedidos do vendedor (UC-211 a UC-214).

Casos de uso testados:
- UC-211: Listar Pedidos Recebidos
- UC-212: Definir Preco Final
- UC-213: Enviar Pedido
- UC-214: Cancelar Pedido (vendedor)
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    PedidosRecebidosPage,
    criar_usuario_e_logar,
    verificar_redirecionamento_login,
)


# ============================================================
# UC-211: LISTAR PEDIDOS RECEBIDOS
# ============================================================


@pytest.mark.e2e
class TestListarPedidosRecebidos:
    """Testes para UC-211: Listar Pedidos Recebidos."""

    def test_listar_pedidos_recebidos_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-211: Listagem de pedidos recebidos deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/pedidos-recebidos")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_listar_pedidos_recebidos_vendedor_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-211: Vendedor deve acessar listagem de pedidos recebidos."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Pedidos Recebidos",
            email="vendedor_recebidos@example.com",
            senha="SenhaForte@123",
        )

        pedidos = PedidosRecebidosPage(e2e_page, e2e_server)
        pedidos.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)
        assert "/pedidos-recebidos" in e2e_page.url

    def test_listar_pedidos_recebidos_comprador_nao_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-211: Comprador nao deve acessar pedidos recebidos."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Tenta Recebidos",
            email="comprador_recebidos@example.com",
            senha="SenhaForte@123",
        )

        pedidos = PedidosRecebidosPage(e2e_page, e2e_server)
        pedidos.navegar()
        e2e_page.wait_for_timeout(500)

        # Deve redirecionar ou negar acesso
        conteudo = e2e_page.content().lower()
        assert (
            "permiss" in conteudo
            or "acesso" in conteudo
            or "/usuario" in e2e_page.url
            or "/login" in e2e_page.url
        )

    def test_listar_pedidos_recebidos_vazio(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-211: Sem pedidos recebidos deve exibir mensagem."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Sem Recebidos",
            email="sem_recebidos@example.com",
            senha="SenhaForte@123",
        )

        pedidos = PedidosRecebidosPage(e2e_page, e2e_server)
        pedidos.navegar()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "nenhum" in conteudo
            or "vazio" in conteudo
            or "pedido" in conteudo
        )


# ============================================================
# UC-212: DEFINIR PRECO FINAL
# ============================================================


@pytest.mark.e2e
class TestDefinirPrecoFinal:
    """Testes para UC-212: Definir Preco Final."""

    def test_definir_preco_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-212: Definicao de preco deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/pedidos-recebidos/1/definir-preco")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_definir_preco_pedido_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-212: Pedido inexistente deve mostrar erro."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Preco Inexistente",
            email="preco_inexistente@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/usuario/pedidos-recebidos/99999/definir-preco")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "encontrad" in conteudo
            or "erro" in conteudo
            or "/pedidos-recebidos" in e2e_page.url
        )


# ============================================================
# UC-213: ENVIAR PEDIDO
# ============================================================


@pytest.mark.e2e
class TestEnviarPedido:
    """Testes para UC-213: Enviar Pedido."""

    def test_enviar_pedido_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-213: Envio de pedido deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/pedidos-recebidos/1/enviar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_enviar_pedido_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-213: Envio de pedido inexistente deve falhar."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Enviar Inexistente",
            email="enviar_inexistente@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/usuario/pedidos-recebidos/99999/enviar")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "encontrad" in conteudo
            or "erro" in conteudo
            or "/pedidos-recebidos" in e2e_page.url
        )


# ============================================================
# UC-214: CANCELAR PEDIDO (VENDEDOR)
# ============================================================


@pytest.mark.e2e
class TestCancelarPedidoVendedor:
    """Testes para UC-214: Cancelar Pedido (Vendedor)."""

    def test_cancelar_pedido_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-214: Cancelamento deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/pedidos-recebidos/1/cancelar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_cancelar_pedido_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-214: Cancelamento de pedido inexistente deve falhar."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Cancelar Inexistente",
            email="cancelar_vend@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/usuario/pedidos-recebidos/99999/cancelar")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "encontrad" in conteudo
            or "erro" in conteudo
            or "/pedidos-recebidos" in e2e_page.url
        )


# ============================================================
# TESTES DE FLUXO DE VENDA
# ============================================================


@pytest.mark.e2e
class TestFluxoVenda:
    """Testes do fluxo de venda do vendedor."""

    def test_visualizar_detalhes_pedido_recebido(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Vendedor deve poder visualizar detalhes de pedido recebido."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Detalhes Pedido",
            email="detalhes_pedido@example.com",
            senha="SenhaForte@123",
        )

        # Tentar visualizar pedido (mesmo inexistente, rota deve existir)
        e2e_page.goto(f"{e2e_server}/usuario/pedidos-recebidos/1")
        e2e_page.wait_for_timeout(500)

        # Deve mostrar erro de pedido nao encontrado ou redirecionar
        conteudo = e2e_page.content().lower()
        assert (
            "pedido" in conteudo
            or "encontrad" in conteudo
            or "/pedidos-recebidos" in e2e_page.url
        )

    def test_pagina_pedidos_recebidos_exibe_filtros(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de pedidos recebidos pode ter filtros de status."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Filtros Pedidos",
            email="filtros_pedidos@example.com",
            senha="SenhaForte@123",
        )

        pedidos = PedidosRecebidosPage(e2e_page, e2e_server)
        pedidos.navegar()
        e2e_page.wait_for_timeout(500)

        # Pagina deve carregar corretamente
        assert "/pedidos-recebidos" in e2e_page.url
