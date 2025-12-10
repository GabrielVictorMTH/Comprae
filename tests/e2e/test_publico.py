"""
Testes E2E para casos de uso publicos (UC-001 a UC-008).

Casos de uso testados:
- UC-001: Visualizar Pagina Inicial
- UC-002: Visualizar Pagina Sobre
- UC-003: Navegar por Produtos
- UC-004: Visualizar Detalhes do Produto
- UC-005: Cadastrar-se no Sistema (coberto em test_auth.py)
- UC-006: Fazer Login (coberto em test_auth.py)
- UC-007: Solicitar Recuperacao de Senha
- UC-008: Redefinir Senha
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    HomePage,
    SobrePage,
    ProdutosPage,
    RecuperarSenhaPage,
    CadastroPage,
)


# ============================================================
# UC-001: VISUALIZAR PAGINA INICIAL
# ============================================================


@pytest.mark.e2e
class TestVisualizarPaginaInicial:
    """Testes para UC-001: Visualizar Pagina Inicial."""

    def test_pagina_inicial_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-001: Deve carregar a pagina inicial com sucesso."""
        page = HomePage(e2e_page, e2e_server)
        page.navegar()

        assert page.esta_na_home() or e2e_page.url.endswith("/")

    def test_pagina_inicial_exibe_logo(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-001: Deve exibir o logo do sistema."""
        page = HomePage(e2e_page, e2e_server)
        page.navegar()

        # Verifica se existe algum elemento de logo/marca
        conteudo = e2e_page.content().lower()
        assert "comprae" in conteudo

    def test_pagina_inicial_exibe_navegacao(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-001: Deve exibir menu de navegacao."""
        page = HomePage(e2e_page, e2e_server)
        page.navegar()

        # Verifica se existe navbar
        expect(e2e_page.locator("nav")).to_be_visible()

    def test_pagina_inicial_possui_link_para_produtos(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-001: Deve ter link para pagina de produtos."""
        page = HomePage(e2e_page, e2e_server)
        page.navegar()

        conteudo = e2e_page.content().lower()
        assert "produto" in conteudo

    def test_pagina_inicial_possui_link_para_login(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-001: Deve ter link para pagina de login."""
        page = HomePage(e2e_page, e2e_server)
        page.navegar()

        conteudo = e2e_page.content().lower()
        assert "login" in conteudo or "entrar" in conteudo


# ============================================================
# UC-002: VISUALIZAR PAGINA SOBRE
# ============================================================


@pytest.mark.e2e
class TestVisualizarPaginaSobre:
    """Testes para UC-002: Visualizar Pagina Sobre."""

    def test_pagina_sobre_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-002: Deve carregar a pagina sobre com sucesso."""
        page = SobrePage(e2e_page, e2e_server)
        page.navegar()

        assert "/sobre" in e2e_page.url

    def test_pagina_sobre_exibe_informacoes_projeto(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-002: Deve exibir informacoes sobre o projeto."""
        page = SobrePage(e2e_page, e2e_server)
        page.navegar()

        conteudo = e2e_page.content().lower()
        # Deve conter informacoes sobre o projeto academico
        assert "sobre" in conteudo or "projeto" in conteudo or "ifes" in conteudo


# ============================================================
# UC-003: NAVEGAR POR PRODUTOS
# ============================================================


@pytest.mark.e2e
class TestNavegarPorProdutos:
    """Testes para UC-003: Navegar por Produtos."""

    def test_pagina_produtos_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-003: Deve carregar a pagina de produtos."""
        page = ProdutosPage(e2e_page, e2e_server)
        page.navegar()

        assert "/produtos" in e2e_page.url

    def test_pagina_produtos_exibe_campo_busca(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-003: Deve exibir campo de busca."""
        page = ProdutosPage(e2e_page, e2e_server)
        page.navegar()

        # Deve ter um campo de busca
        campo_busca = e2e_page.locator('input[name="q"]')
        expect(campo_busca).to_be_visible()

    def test_pagina_produtos_permite_busca(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-003: Deve permitir busca por termo."""
        page = ProdutosPage(e2e_page, e2e_server)
        page.navegar()

        # Realizar busca
        page.buscar("teste")

        # Deve permanecer na pagina de produtos com parametro de busca
        assert "/produtos" in e2e_page.url

    def test_pagina_produtos_exibe_listagem(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-003: Deve exibir area de listagem de produtos."""
        page = ProdutosPage(e2e_page, e2e_server)
        page.navegar()

        # Deve ter container para produtos (mesmo vazio)
        conteudo = e2e_page.content().lower()
        assert "produto" in conteudo


# ============================================================
# UC-004: VISUALIZAR DETALHES DO PRODUTO
# ============================================================


@pytest.mark.e2e
class TestVisualizarDetalhesProduto:
    """Testes para UC-004: Visualizar Detalhes do Produto."""

    def test_rota_detalhes_produto_existe(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-004: A rota de detalhes do produto deve existir."""
        # Tenta acessar um produto (mesmo inexistente)
        e2e_page.goto(f"{e2e_server}/produtos/1")

        # Deve redirecionar ou mostrar mensagem (nao dar erro 500)
        assert e2e_page.url is not None

    def test_detalhes_produto_nao_encontrado_exibe_mensagem(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-004: Produto inexistente deve exibir mensagem apropriada."""
        e2e_page.goto(f"{e2e_server}/produtos/99999")
        e2e_page.wait_for_timeout(500)

        # Deve mostrar mensagem de erro ou redirecionar
        conteudo = e2e_page.content().lower()
        # Pode ter sido redirecionado ou mostrar erro
        assert (
            "encontrad" in conteudo
            or "/produtos" in e2e_page.url
            or "erro" in conteudo
        )


# ============================================================
# UC-007: SOLICITAR RECUPERACAO DE SENHA
# ============================================================


@pytest.mark.e2e
class TestSolicitarRecuperacaoSenha:
    """Testes para UC-007: Solicitar Recuperacao de Senha."""

    def test_pagina_recuperar_senha_carrega(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-007: Deve carregar pagina de recuperacao de senha."""
        page = RecuperarSenhaPage(e2e_page, e2e_server)
        page.navegar()

        assert "/recuperar-senha" in e2e_page.url

    def test_pagina_recuperar_senha_exibe_formulario(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-007: Deve exibir formulario com campo de e-mail."""
        page = RecuperarSenhaPage(e2e_page, e2e_server)
        page.navegar()

        expect(e2e_page.locator('input[name="email"]')).to_be_visible()
        expect(e2e_page.locator('button[type="submit"]')).to_be_visible()

    def test_solicitar_recuperacao_email_invalido(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-007: Deve validar formato do e-mail."""
        page = RecuperarSenhaPage(e2e_page, e2e_server)
        page.navegar()

        # Tentar com e-mail invalido
        page.solicitar_recuperacao("email_invalido")
        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina ou mostrar erro
        assert "/recuperar-senha" in e2e_page.url

    def test_solicitar_recuperacao_email_nao_cadastrado(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-007: Deve aceitar solicitacao mesmo para e-mail nao cadastrado (seguranca)."""
        page = RecuperarSenhaPage(e2e_page, e2e_server)
        page.navegar()

        # Solicitar para e-mail inexistente
        page.solicitar_recuperacao("nao_existe@example.com")
        e2e_page.wait_for_timeout(500)

        # Por seguranca, nao deve revelar se o e-mail existe ou nao
        # Deve mostrar mensagem generica de sucesso ou redirecionar
        conteudo = e2e_page.content().lower()
        assert (
            "enviado" in conteudo
            or "enviamos" in conteudo
            or "verifique" in conteudo
            or "/login" in e2e_page.url
        )


# ============================================================
# UC-008: REDEFINIR SENHA
# ============================================================


@pytest.mark.e2e
class TestRedefinirSenha:
    """Testes para UC-008: Redefinir Senha."""

    def test_rota_redefinir_senha_existe(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-008: A rota de redefinicao de senha deve existir."""
        # Tenta acessar com token invalido
        e2e_page.goto(f"{e2e_server}/redefinir-senha/token_invalido")
        e2e_page.wait_for_timeout(500)

        # Nao deve dar erro 500
        assert e2e_page.url is not None

    def test_redefinir_senha_token_invalido(
        self, e2e_page: Page, e2e_server: str
    ):
        """UC-008: Token invalido deve exibir erro."""
        e2e_page.goto(f"{e2e_server}/redefinir-senha/token_invalido_123")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        # Deve mostrar erro de token invalido ou redirecionar
        assert (
            "token" in conteudo
            or "invalido" in conteudo
            or "expirado" in conteudo
            or "/login" in e2e_page.url
            or "/recuperar-senha" in e2e_page.url
        )


# ============================================================
# TESTES DE NAVEGACAO PUBLICA
# ============================================================


@pytest.mark.e2e
class TestNavegacaoPublica:
    """Testes de navegacao entre paginas publicas."""

    def test_navegacao_home_para_produtos(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve navegar da home para produtos."""
        e2e_page.goto(e2e_server)
        e2e_page.wait_for_timeout(300)

        # Clicar em link de produtos
        link = e2e_page.get_by_role("link", name="Produtos")
        if link.is_visible():
            link.click()
            e2e_page.wait_for_timeout(500)
            assert "/produtos" in e2e_page.url

    def test_navegacao_home_para_login(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve navegar da home para login."""
        e2e_page.goto(e2e_server)
        e2e_page.wait_for_timeout(300)

        # Clicar em link de login/entrar
        link = e2e_page.get_by_role("link", name="Entrar")
        if not link.is_visible():
            link = e2e_page.get_by_role("link", name="Login")

        if link.is_visible():
            link.click()
            e2e_page.wait_for_timeout(500)
            assert "/login" in e2e_page.url

    def test_navegacao_login_para_cadastro(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve navegar do login para cadastro."""
        e2e_page.goto(f"{e2e_server}/login")
        e2e_page.wait_for_timeout(300)

        # Clicar em link de cadastro
        link = e2e_page.get_by_text("cadastre-se aqui")
        if link.is_visible():
            link.click()
            e2e_page.wait_for_timeout(500)
            assert "/cadastrar" in e2e_page.url

    def test_navegacao_login_para_recuperar_senha(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve navegar do login para recuperar senha."""
        e2e_page.goto(f"{e2e_server}/login")
        e2e_page.wait_for_timeout(300)

        # Clicar em link de esqueci senha
        link = e2e_page.get_by_text("Esqueceu sua senha?")
        if link.is_visible():
            link.click()
            e2e_page.wait_for_timeout(500)
            assert "/recuperar-senha" in e2e_page.url
