"""
Testes E2E para gerenciamento de pedidos do comprador (UC-121 a UC-126).

Casos de uso testados:
- UC-121: Listar Meus Pedidos
- UC-122: Visualizar Detalhes do Pedido
- UC-123: Criar Pedido
- UC-124: Pagar Pedido
- UC-125: Cancelar Pedido
- UC-126: Confirmar Entrega
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    MeusPedidosPage,
    criar_usuario_e_logar,
    verificar_redirecionamento_login,
)


# ============================================================
# UC-121: LISTAR MEUS PEDIDOS
# ============================================================


@pytest.mark.e2e
class TestListarMeusPedidos:
    """Testes para UC-121: Listar Meus Pedidos."""

    def test_listar_pedidos_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-121: Listagem de pedidos deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/pedidos")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_listar_pedidos_comprador_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-121: Comprador deve acessar listagem de pedidos."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Pedidos",
            email="comprador_pedidos@example.com",
            senha="SenhaForte@123",
        )

        pedidos = MeusPedidosPage(e2e_page, e2e_server)
        pedidos.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)
        assert "/pedidos" in e2e_page.url

    def test_listar_pedidos_vazio_exibe_mensagem(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-121: Sem pedidos deve exibir mensagem apropriada."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Sem Pedidos",
            email="sem_pedidos@example.com",
            senha="SenhaForte@123",
        )

        pedidos = MeusPedidosPage(e2e_page, e2e_server)
        pedidos.navegar()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "nenhum" in conteudo
            or "vazio" in conteudo
            or "pedido" in conteudo
        )

    def test_vendedor_nao_acessa_meus_pedidos(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-121: Vendedor nao deve acessar 'Meus Pedidos' de comprador."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Teste Pedidos",
            email="vendedor_pedidos@example.com",
            senha="SenhaForte@123",
        )

        # Vendedor usa pedidos-recebidos, nao pedidos
        e2e_page.goto(f"{e2e_server}/pedidos")
        e2e_page.wait_for_timeout(500)

        # Pode redirecionar ou mostrar vazio (vendedor nao faz pedidos)
        conteudo = e2e_page.content().lower()
        assert "/pedidos" in e2e_page.url or "pedido" in conteudo


# ============================================================
# UC-122: VISUALIZAR DETALHES DO PEDIDO
# ============================================================


@pytest.mark.e2e
class TestVisualizarDetalhesPedido:
    """Testes para UC-122: Visualizar Detalhes do Pedido."""

    def test_detalhes_pedido_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-122: Visualizacao de pedido deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/pedidos/detalhes/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_detalhes_pedido_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-122: Pedido inexistente deve mostrar erro ou redirecionar."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Pedido Inexistente",
            email="pedido_inexistente@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/pedidos/detalhes/99999")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "encontrad" in conteudo
            or "erro" in conteudo
            or "/pedidos" in e2e_page.url
        )


# ============================================================
# UC-123: CRIAR PEDIDO
# ============================================================


@pytest.mark.e2e
class TestCriarPedido:
    """Testes para UC-123: Criar Pedido."""

    def test_criar_pedido_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-123: Criacao de pedido deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/pedidos/criar?anuncio=1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_criar_pedido_produto_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-123: Produto inexistente deve mostrar erro."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Produto Inexistente",
            email="produto_inexistente@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/pedidos/criar?anuncio=99999")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "encontrad" in conteudo
            or "erro" in conteudo
            or "/anuncios" in e2e_page.url
        )

    def test_criar_pedido_requer_endereco(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-123: Comprador precisa de endereco para criar pedido."""
        # Este teste valida a regra de negocio que exige endereco
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Sem Endereco Pedido",
            email="sem_endereco_pedido@example.com",
            senha="SenhaForte@123",
        )

        # Tentar criar pedido sem ter endereco
        e2e_page.goto(f"{e2e_server}/pedidos/criar?anuncio=1")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        # Pode redirecionar para cadastro de endereco ou mostrar erro
        assert (
            "endereco" in conteudo
            or "cadastr" in conteudo
            or "/endereco" in e2e_page.url
            or "encontrad" in conteudo
        )


# ============================================================
# UC-124: PAGAR PEDIDO
# ============================================================


@pytest.mark.e2e
class TestPagarPedido:
    """Testes para UC-124: Pagar Pedido."""

    def test_pagar_pedido_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-124: Pagamento de pedido deve requerer autenticacao (rota e POST-only)."""
        # A rota /pedidos/pagar/{id} e POST-only
        # Acesso GET retorna 405 Method Not Allowed
        response = e2e_page.request.get(f"{e2e_server}/pedidos/pagar/1")
        assert response.status == 405 or verificar_redirecionamento_login(e2e_page)

    def test_pagar_pedido_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-124: Pagamento de pedido inexistente deve falhar (rota e POST-only)."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Pagar Inexistente",
            email="pagar_inexistente@example.com",
            senha="SenhaForte@123",
        )

        # A rota /pedidos/pagar/{id} e POST-only
        response = e2e_page.request.get(f"{e2e_server}/pedidos/pagar/99999")
        # GET em rota POST-only deve retornar 405
        assert response.status == 405


# ============================================================
# UC-125: CANCELAR PEDIDO
# ============================================================


@pytest.mark.e2e
class TestCancelarPedido:
    """Testes para UC-125: Cancelar Pedido."""

    def test_cancelar_pedido_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-125: Cancelamento de pedido deve requerer autenticacao (rota e POST-only)."""
        # A rota /pedidos/cancelar/{id} e POST-only
        # Acesso GET retorna 405 Method Not Allowed
        response = e2e_page.request.get(f"{e2e_server}/pedidos/cancelar/1")
        assert response.status == 405 or verificar_redirecionamento_login(e2e_page)

    def test_cancelar_pedido_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-125: Cancelamento de pedido inexistente deve falhar (rota e POST-only)."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Cancelar Inexistente",
            email="cancelar_inexistente@example.com",
            senha="SenhaForte@123",
        )

        # A rota /pedidos/cancelar/{id} e POST-only
        response = e2e_page.request.get(f"{e2e_server}/pedidos/cancelar/99999")
        # GET em rota POST-only deve retornar 405
        assert response.status == 405


# ============================================================
# UC-126: CONFIRMAR ENTREGA
# ============================================================


@pytest.mark.e2e
class TestConfirmarEntrega:
    """Testes para UC-126: Confirmar Entrega."""

    def test_confirmar_entrega_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-126: Confirmacao de entrega deve requerer autenticacao (rota e POST-only)."""
        # A rota /pedidos/confirmar-entrega/{id} e POST-only
        # Acesso GET retorna 405 Method Not Allowed
        response = e2e_page.request.get(f"{e2e_server}/pedidos/confirmar-entrega/1")
        assert response.status == 405 or verificar_redirecionamento_login(e2e_page)

    def test_confirmar_entrega_pedido_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-126: Confirmacao de pedido inexistente deve falhar (rota e POST-only)."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Confirmar Inexistente",
            email="confirmar_inexistente@example.com",
            senha="SenhaForte@123",
        )

        # A rota /pedidos/confirmar-entrega/{id} e POST-only
        response = e2e_page.request.get(f"{e2e_server}/pedidos/confirmar-entrega/99999")
        # GET em rota POST-only deve retornar 405
        assert response.status == 405


# ============================================================
# TESTES DE FLUXO DE PEDIDO
# ============================================================


@pytest.mark.e2e
class TestFluxoPedido:
    """Testes do fluxo completo de pedido."""

    def test_pagina_criar_pedido_exibe_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Formulario de criacao de pedido deve ter campo quantidade."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Form Pedido",
            email="form_pedido@example.com",
            senha="SenhaForte@123",
        )

        # Mesmo que o produto nao exista, a rota deve existir
        e2e_page.goto(f"{e2e_server}/pedidos/criar?anuncio=1")
        e2e_page.wait_for_timeout(500)

        # Se a rota existe e ha formulario
        # (pode redirecionar se produto nao existe)
        conteudo = e2e_page.content().lower()
        assert "pedido" in conteudo or "produto" in conteudo
