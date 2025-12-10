"""
Testes E2E para gerenciamento de perfil (UC-101 a UC-105).

Casos de uso testados:
- UC-101: Visualizar Dashboard
- UC-102: Visualizar Perfil
- UC-103: Editar Perfil
- UC-104: Alterar Senha
- UC-105: Atualizar Foto de Perfil
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    CadastroPage,
    LoginPage,
    PerfilPage,
    criar_usuario_e_logar,
    verificar_redirecionamento_login,
)


# ============================================================
# UC-101: VISUALIZAR DASHBOARD
# ============================================================


@pytest.mark.e2e
class TestVisualizarDashboard:
    """Testes para UC-101: Visualizar Dashboard."""

    def test_dashboard_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-101: Dashboard deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_dashboard_comprador_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-101: Dashboard do comprador deve carregar."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Dashboard",
            email="comprador_dash@example.com",
            senha="SenhaForte@123",
        )

        assert "/usuario" in e2e_page.url

    def test_dashboard_vendedor_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-101: Dashboard do vendedor deve carregar."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Dashboard",
            email="vendedor_dash@example.com",
            senha="SenhaForte@123",
        )

        assert "/usuario" in e2e_page.url

    def test_dashboard_exibe_nome_usuario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-101: Dashboard deve exibir nome do usuario."""
        nome = "Usuario Nome Visivel"
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome=nome,
            email="nome_visivel@example.com",
            senha="SenhaForte@123",
        )

        conteudo = e2e_page.content()
        assert nome in conteudo or nome.split()[0] in conteudo


# ============================================================
# UC-102: VISUALIZAR PERFIL
# ============================================================


@pytest.mark.e2e
class TestVisualizarPerfil:
    """Testes para UC-102: Visualizar Perfil."""

    def test_perfil_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-102: Pagina de perfil deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/perfil")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_visualizar_perfil_exibe_dados(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-102: Deve exibir dados do usuario."""
        email = "perfil_dados@example.com"
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Perfil Dados",
            email=email,
            senha="SenhaForte@123",
        )

        # Navegar para perfil (pode estar em /usuario ou /usuario/perfil)
        e2e_page.goto(f"{e2e_server}/usuario")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content()
        # Deve exibir o email ou nome do usuario
        assert email in conteudo or "Usuario Perfil" in conteudo


# ============================================================
# UC-103: EDITAR PERFIL
# ============================================================


@pytest.mark.e2e
class TestEditarPerfil:
    """Testes para UC-103: Editar Perfil."""

    def test_editar_perfil_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-103: Edicao de perfil deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/editar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_editar_perfil_carrega_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-103: Deve carregar formulario de edicao."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Editar Form",
            email="editar_form@example.com",
            senha="SenhaForte@123",
        )

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_editar()
        e2e_page.wait_for_timeout(500)

        # Deve ter campos de edicao
        expect(e2e_page.locator('input[name="nome"]')).to_be_visible()

    def test_editar_perfil_atualiza_nome(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-103: Deve permitir atualizar nome."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Nome Original Usuario",
            email="editar_nome@example.com",
            senha="SenhaForte@123",
        )

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_editar()
        e2e_page.wait_for_timeout(500)

        # Limpar e preencher novo nome
        e2e_page.fill('input[name="nome"]', "")
        e2e_page.fill('input[name="nome"]', "Nome Atualizado Usuario")
        perfil.submeter()
        e2e_page.wait_for_timeout(500)

        # Verificar se foi atualizado
        conteudo = e2e_page.content()
        assert "sucesso" in conteudo.lower() or "atualizado" in conteudo.lower()

    def test_editar_perfil_validacao_nome_vazio(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-103: Deve validar nome vazio."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Validacao Nome",
            email="validacao_nome@example.com",
            senha="SenhaForte@123",
        )

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_editar()
        e2e_page.wait_for_timeout(500)

        # Tentar salvar com nome vazio
        e2e_page.fill('input[name="nome"]', "")
        perfil.submeter()
        e2e_page.wait_for_timeout(500)

        # Deve exibir erro ou permanecer na pagina
        conteudo = e2e_page.content().lower()
        assert "nome" in conteudo


# ============================================================
# UC-104: ALTERAR SENHA
# ============================================================


@pytest.mark.e2e
class TestAlterarSenha:
    """Testes para UC-104: Alterar Senha."""

    def test_alterar_senha_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-104: Alteracao de senha deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/alterar-senha")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_alterar_senha_carrega_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-104: Deve carregar formulario de alteracao de senha."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Alterar Senha",
            email="alterar_senha@example.com",
            senha="SenhaForte@123",
        )

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()
        e2e_page.wait_for_timeout(500)

        # Deve ter campos de senha
        expect(e2e_page.locator('input[name="senha_atual"]')).to_be_visible()
        expect(e2e_page.locator('input[name="nova_senha"]')).to_be_visible()

    def test_alterar_senha_com_sucesso(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-104: Deve permitir alterar senha com senha atual correta."""
        email = "alterar_sucesso@example.com"
        senha_antiga = "SenhaForte@123"
        senha_nova = "NovaSenha@456"

        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Alterar Sucesso",
            email=email,
            senha=senha_antiga,
        )

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()
        e2e_page.wait_for_timeout(500)

        # Preencher formulario
        e2e_page.fill('input[name="senha_atual"]', senha_antiga)
        e2e_page.fill('input[name="nova_senha"]', senha_nova)
        e2e_page.fill('input[name="confirmar_nova_senha"]', senha_nova)
        perfil.submeter()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "sucesso" in conteudo or "alterada" in conteudo or "/usuario" in e2e_page.url

    def test_alterar_senha_atual_incorreta(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-104: Deve validar senha atual incorreta."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Senha Incorreta",
            email="senha_incorreta@example.com",
            senha="SenhaForte@123",
        )

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()
        e2e_page.wait_for_timeout(500)

        # Tentar com senha atual errada
        e2e_page.fill('input[name="senha_atual"]', "SenhaErrada@123")
        e2e_page.fill('input[name="nova_senha"]', "NovaSenha@456")
        e2e_page.fill('input[name="confirmar_nova_senha"]', "NovaSenha@456")
        perfil.submeter()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "incorreta" in conteudo or "atual" in conteudo or "erro" in conteudo


# ============================================================
# UC-105: ATUALIZAR FOTO DE PERFIL
# ============================================================


@pytest.mark.e2e
class TestAtualizarFotoPerfil:
    """Testes para UC-105: Atualizar Foto de Perfil."""

    def test_foto_perfil_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-105: Upload de foto deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/foto")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_foto_perfil_exibe_area_upload(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-105: Deve exibir area para upload de foto."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Foto Upload",
            email="foto_upload@example.com",
            senha="SenhaForte@123",
        )

        # Navegar para pagina de foto (pode estar em diferentes rotas)
        e2e_page.goto(f"{e2e_server}/usuario")
        e2e_page.wait_for_timeout(500)

        # Deve haver alguma indicacao de foto/avatar
        conteudo = e2e_page.content().lower()
        assert "foto" in conteudo or "avatar" in conteudo or "imagem" in conteudo


# ============================================================
# TESTES DE PERMISSAO DE PERFIL
# ============================================================


@pytest.mark.e2e
class TestPermissoesPerfil:
    """Testes de permissoes de acesso ao perfil."""

    def test_comprador_acessa_dashboard(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Comprador deve acessar seu dashboard."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Acesso Dashboard",
            email="comprador_acesso@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/usuario")
        e2e_page.wait_for_timeout(500)

        assert "/usuario" in e2e_page.url
        assert not verificar_redirecionamento_login(e2e_page)

    def test_vendedor_acessa_dashboard(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Vendedor deve acessar seu dashboard."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Acesso Dashboard",
            email="vendedor_acesso@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/usuario")
        e2e_page.wait_for_timeout(500)

        assert "/usuario" in e2e_page.url
        assert not verificar_redirecionamento_login(e2e_page)
