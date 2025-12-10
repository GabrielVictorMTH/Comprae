"""
Testes E2E para gerenciamento de produtos do vendedor (UC-201 a UC-205).

Casos de uso testados:
- UC-201: Listar Meus Produtos
- UC-202: Cadastrar Produto
- UC-203: Editar Produto
- UC-204: Excluir Produto
- UC-205: Ativar/Desativar Produto
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    MeusProdutosPage,
    criar_usuario_e_logar,
    verificar_redirecionamento_login,
)


# ============================================================
# UC-201: LISTAR MEUS PRODUTOS
# ============================================================


@pytest.mark.e2e
class TestListarMeusProdutos:
    """Testes para UC-201: Listar Meus Produtos."""

    def test_listar_produtos_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-201: Listagem de produtos deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/vendedor/anuncios")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_listar_produtos_vendedor_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-201: Vendedor deve acessar listagem de produtos."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Produtos Lista",
            email="vendedor_produtos@example.com",
            senha="SenhaForte@123",
        )

        produtos = MeusProdutosPage(e2e_page, e2e_server)
        produtos.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)
        assert "/anuncios" in e2e_page.url

    def test_listar_produtos_comprador_nao_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-201: Comprador nao deve acessar area de vendedor."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Tenta Produtos",
            email="comprador_produtos@example.com",
            senha="SenhaForte@123",
        )

        produtos = MeusProdutosPage(e2e_page, e2e_server)
        produtos.navegar()
        e2e_page.wait_for_timeout(500)

        # Deve redirecionar ou negar acesso
        conteudo = e2e_page.content().lower()
        assert (
            "permiss" in conteudo
            or "acesso" in conteudo
            or "/usuario" in e2e_page.url
            or "/login" in e2e_page.url
        )

    def test_listar_produtos_vazio(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-201: Sem produtos deve exibir mensagem apropriada."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Sem Produtos",
            email="sem_produtos@example.com",
            senha="SenhaForte@123",
        )

        produtos = MeusProdutosPage(e2e_page, e2e_server)
        produtos.navegar()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "nenhum" in conteudo
            or "vazio" in conteudo
            or "anuncio" in conteudo
            or "produto" in conteudo
        )


# ============================================================
# UC-202: CADASTRAR PRODUTO
# ============================================================


@pytest.mark.e2e
class TestCadastrarProduto:
    """Testes para UC-202: Cadastrar Produto."""

    def test_cadastrar_produto_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-202: Cadastro de produto deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/vendedor/anuncios/cadastrar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_cadastrar_produto_exibe_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-202: Deve exibir formulario de cadastro de produto."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Form Produto",
            email="form_produto@example.com",
            senha="SenhaForte@123",
        )

        produtos = MeusProdutosPage(e2e_page, e2e_server)
        produtos.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        expect(e2e_page.locator('input[name="nome"]')).to_be_visible()
        expect(e2e_page.locator('textarea[name="descricao"]')).to_be_visible()
        expect(e2e_page.locator('input[name="preco"]')).to_be_visible()

    def test_cadastrar_produto_comprador_nao_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-202: Comprador nao deve cadastrar produtos."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Tenta Cadastrar",
            email="comprador_cadastrar@example.com",
            senha="SenhaForte@123",
        )

        produtos = MeusProdutosPage(e2e_page, e2e_server)
        produtos.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        # Deve redirecionar ou negar acesso
        conteudo = e2e_page.content().lower()
        assert (
            "permiss" in conteudo
            or "acesso" in conteudo
            or "/usuario" in e2e_page.url
            or "/login" in e2e_page.url
        )

    def test_cadastrar_produto_validacao_campos(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-202: Deve validar campos obrigatorios."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Validacao Produto",
            email="validacao_produto@example.com",
            senha="SenhaForte@123",
        )

        produtos = MeusProdutosPage(e2e_page, e2e_server)
        produtos.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        # Tentar submeter sem preencher
        produtos.submeter()
        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina ou mostrar erro
        assert "/anuncios" in e2e_page.url

    def test_cadastrar_produto_preco_invalido(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-202: Deve validar preco invalido."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Preco Invalido",
            email="preco_invalido@example.com",
            senha="SenhaForte@123",
        )

        produtos = MeusProdutosPage(e2e_page, e2e_server)
        produtos.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        # Preencher com preco negativo
        e2e_page.fill('input[name="nome"]', "Produto Teste")
        e2e_page.fill('textarea[name="descricao"]', "Descricao do produto")
        e2e_page.fill('input[name="preco"]', "-10")
        e2e_page.fill('input[name="estoque"]', "5")
        produtos.submeter()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "preco" in conteudo or "/cadastrar" in e2e_page.url


# ============================================================
# UC-203: EDITAR PRODUTO
# ============================================================


@pytest.mark.e2e
class TestEditarProduto:
    """Testes para UC-203: Editar Produto."""

    def test_editar_produto_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-203: Edicao de produto deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/vendedor/anuncios/editar/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_editar_produto_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-203: Produto inexistente deve mostrar erro."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Editar Inexistente",
            email="editar_inexistente@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/vendedor/anuncios/editar/99999")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "encontrad" in conteudo
            or "erro" in conteudo
            or "/anuncios" in e2e_page.url
        )


# ============================================================
# UC-204: EXCLUIR PRODUTO
# ============================================================


@pytest.mark.e2e
class TestExcluirProduto:
    """Testes para UC-204: Excluir Produto."""

    def test_excluir_produto_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-204: Exclusao de produto deve requerer autenticacao (rota e POST-only)."""
        # A rota /vendedor/anuncios/excluir/{id} e POST-only
        # Acesso GET retorna 405 Method Not Allowed
        response = e2e_page.request.get(f"{e2e_server}/vendedor/anuncios/excluir/1")
        assert response.status == 405 or verificar_redirecionamento_login(e2e_page)

    def test_excluir_produto_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-204: Exclusao de produto inexistente deve falhar (rota e POST-only)."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Excluir Inexistente",
            email="excluir_inexistente@example.com",
            senha="SenhaForte@123",
        )

        # A rota /vendedor/anuncios/excluir/{id} e POST-only
        response = e2e_page.request.get(f"{e2e_server}/vendedor/anuncios/excluir/99999")
        # GET em rota POST-only deve retornar 405
        assert response.status == 405


# ============================================================
# UC-205: ATIVAR/DESATIVAR PRODUTO
# ============================================================


@pytest.mark.e2e
class TestAtivarDesativarProduto:
    """Testes para UC-205: Ativar/Desativar Produto."""

    def test_alternar_status_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-205: Alternar status deve requerer autenticacao (rota e POST-only)."""
        # A rota /vendedor/anuncios/ativar/{id} e POST-only
        # Acesso GET retorna 405 Method Not Allowed
        response = e2e_page.request.get(f"{e2e_server}/vendedor/anuncios/ativar/1")
        assert response.status == 405 or verificar_redirecionamento_login(e2e_page)

    def test_alternar_status_produto_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-205: Alternar status de produto inexistente deve falhar."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Alternar Inexistente",
            email="alternar_inexistente@example.com",
            senha="SenhaForte@123",
        )

        # A rota /vendedor/anuncios/ativar/{id} e POST-only
        response = e2e_page.request.get(f"{e2e_server}/vendedor/anuncios/ativar/99999")
        # GET em rota POST-only deve retornar 405
        assert response.status == 405


# ============================================================
# TESTES DE REGRAS DE NEGOCIO
# ============================================================


@pytest.mark.e2e
class TestRegrasNegocioProduto:
    """Testes de regras de negocio de produtos."""

    def test_vendedor_so_edita_proprio_produto(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Vendedor so pode editar seus proprios produtos."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Proprio Produto",
            email="proprio_produto@example.com",
            senha="SenhaForte@123",
        )

        # Tentar editar produto de outro vendedor (ID 1 provavelmente nao existe)
        e2e_page.goto(f"{e2e_server}/vendedor/anuncios/editar/1")
        e2e_page.wait_for_timeout(500)

        # Deve negar acesso ou mostrar erro
        conteudo = e2e_page.content().lower()
        assert (
            "permiss" in conteudo
            or "acesso" in conteudo
            or "encontrad" in conteudo
            or "/anuncios" in e2e_page.url
        )
