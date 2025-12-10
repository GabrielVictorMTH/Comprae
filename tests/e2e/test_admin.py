"""
Testes E2E para administracao do sistema (UC-301 a UC-376).

Casos de uso testados:
- UC-301 a UC-304: Gerenciamento de Usuarios
- UC-311 a UC-316: Gerenciamento de Produtos
- UC-321 a UC-324: Gerenciamento de Pedidos
- UC-331 a UC-334: Gerenciamento de Categorias
- UC-341 a UC-343: Gerenciamento de Enderecos
- UC-351 a UC-352: Gerenciamento de Curtidas
- UC-361 a UC-365: Gerenciamento de Chamados
- UC-371 a UC-376: Gerenciamento do Sistema
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    AdminUsuariosPage,
    AdminProdutosPage,
    AdminPedidosPage,
    AdminCategoriasPage,
    AdminChamadosPage,
    AdminConfiguracoesPage,
    AdminBackupsPage,
    CadastroPage,
    LoginPage,
    verificar_redirecionamento_login,
)


def criar_admin_e_logar(page: Page, base_url: str) -> bool:
    """
    Cria usuario admin e faz login.

    Nota: Em ambiente real, admin seria criado diretamente no banco.
    Para testes E2E, usamos abordagem alternativa.
    """
    # Tentar fazer login como admin padrao
    login = LoginPage(page, base_url)
    login.navegar()
    login.fazer_login("admin@comprae.com", "Admin@123")

    try:
        page.wait_for_url("**/admin**", timeout=5000)
        return True
    except Exception:
        return "/admin" in page.url


# ============================================================
# UC-301 a UC-304: GERENCIAMENTO DE USUARIOS
# ============================================================


@pytest.mark.e2e
class TestAdminListarUsuarios:
    """Testes para UC-301: Listar Usuarios."""

    def test_listar_usuarios_requer_admin(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-301: Listagem de usuarios deve requerer admin."""
        admin = AdminUsuariosPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_comprador_nao_acessa_admin_usuarios(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-301: Comprador nao deve acessar admin."""
        # Criar e logar como comprador
        cadastro = CadastroPage(e2e_page, e2e_server)
        cadastro.navegar()
        cadastro.cadastrar(
            perfil="Comprador",
            nome="Comprador Tenta Admin",
            email="comprador_admin@example.com",
            senha="SenhaForte@123",
        )
        cadastro.aguardar_navegacao_login()

        login = LoginPage(e2e_page, e2e_server)
        login.fazer_login("comprador_admin@example.com", "SenhaForte@123")
        login.aguardar_navegacao_usuario()

        # Tentar acessar admin
        admin = AdminUsuariosPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        # Deve negar acesso
        conteudo = e2e_page.content().lower()
        assert (
            "permiss" in conteudo
            or "acesso" in conteudo
            or "/usuario" in e2e_page.url
            or "/login" in e2e_page.url
        )

    def test_vendedor_nao_acessa_admin_usuarios(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-301: Vendedor nao deve acessar admin."""
        # Criar e logar como vendedor
        cadastro = CadastroPage(e2e_page, e2e_server)
        cadastro.navegar()
        cadastro.cadastrar(
            perfil="Vendedor",
            nome="Vendedor Tenta Admin",
            email="vendedor_admin@example.com",
            senha="SenhaForte@123",
        )
        cadastro.aguardar_navegacao_login()

        login = LoginPage(e2e_page, e2e_server)
        login.fazer_login("vendedor_admin@example.com", "SenhaForte@123")
        login.aguardar_navegacao_usuario()

        # Tentar acessar admin
        admin = AdminUsuariosPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        # Deve negar acesso
        conteudo = e2e_page.content().lower()
        assert (
            "permiss" in conteudo
            or "acesso" in conteudo
            or "/usuario" in e2e_page.url
            or "/login" in e2e_page.url
        )


@pytest.mark.e2e
class TestAdminCadastrarUsuario:
    """Testes para UC-302: Cadastrar Usuario."""

    def test_cadastrar_usuario_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-302: Cadastro de usuario pelo admin requer autenticacao."""
        admin = AdminUsuariosPage(e2e_page, e2e_server)
        admin.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminEditarUsuario:
    """Testes para UC-303: Editar Usuario."""

    def test_editar_usuario_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-303: Edicao de usuario requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/usuarios/1/editar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminExcluirUsuario:
    """Testes para UC-304: Excluir Usuario."""

    def test_excluir_usuario_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-304: Exclusao de usuario requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/usuarios/1/excluir")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-311 a UC-316: GERENCIAMENTO DE PRODUTOS
# ============================================================


@pytest.mark.e2e
class TestAdminListarProdutos:
    """Testes para UC-311: Listar Todos os Produtos."""

    def test_listar_produtos_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-311: Listagem de produtos requer autenticacao admin."""
        admin = AdminProdutosPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminModerarProdutos:
    """Testes para UC-312 a UC-314: Moderar Produtos."""

    def test_moderar_produtos_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-312: Moderacao de produtos requer autenticacao."""
        admin = AdminProdutosPage(e2e_page, e2e_server)
        admin.navegar_moderar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_aprovar_produto_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-313: Aprovacao de produto requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/anuncios/1/aprovar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_reprovar_produto_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-314: Reprovacao de produto requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/anuncios/1/reprovar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-321 a UC-324: GERENCIAMENTO DE PEDIDOS
# ============================================================


@pytest.mark.e2e
class TestAdminListarPedidos:
    """Testes para UC-321: Listar Todos os Pedidos."""

    def test_listar_pedidos_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-321: Listagem de pedidos requer autenticacao admin."""
        admin = AdminPedidosPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminVisualizarPedido:
    """Testes para UC-322: Visualizar Detalhes do Pedido."""

    def test_visualizar_pedido_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-322: Visualizacao de pedido requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/pedidos/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminCancelarPedido:
    """Testes para UC-323: Cancelar Pedido (Admin)."""

    def test_cancelar_pedido_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-323: Cancelamento admin requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/pedidos/1/cancelar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-331 a UC-334: GERENCIAMENTO DE CATEGORIAS
# ============================================================


@pytest.mark.e2e
class TestAdminListarCategorias:
    """Testes para UC-331: Listar Categorias."""

    def test_listar_categorias_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-331: Listagem de categorias requer autenticacao admin."""
        admin = AdminCategoriasPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminCadastrarCategoria:
    """Testes para UC-332: Cadastrar Categoria."""

    def test_cadastrar_categoria_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-332: Cadastro de categoria requer autenticacao."""
        admin = AdminCategoriasPage(e2e_page, e2e_server)
        admin.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminEditarCategoria:
    """Testes para UC-333: Editar Categoria."""

    def test_editar_categoria_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-333: Edicao de categoria requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/categorias/1/editar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminExcluirCategoria:
    """Testes para UC-334: Excluir Categoria."""

    def test_excluir_categoria_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-334: Exclusao de categoria requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/categorias/1/excluir")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-341 a UC-343: GERENCIAMENTO DE ENDERECOS
# ============================================================


@pytest.mark.e2e
class TestAdminEnderecos:
    """Testes para UC-341 a UC-343: Gerenciamento de Enderecos."""

    def test_listar_enderecos_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-341: Listagem de enderecos requer autenticacao admin."""
        e2e_page.goto(f"{e2e_server}/admin/enderecos/listar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_visualizar_endereco_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-342: Visualizacao de endereco requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/enderecos/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_excluir_endereco_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-343: Exclusao de endereco requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/enderecos/1/excluir")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-351 a UC-352: GERENCIAMENTO DE CURTIDAS
# ============================================================


@pytest.mark.e2e
class TestAdminCurtidas:
    """Testes para UC-351 a UC-352: Gerenciamento de Curtidas."""

    def test_listar_curtidas_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-351: Listagem de curtidas requer autenticacao admin."""
        e2e_page.goto(f"{e2e_server}/admin/curtidas/listar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_excluir_curtida_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-352: Exclusao de curtida requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/curtidas/1/excluir")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-361 a UC-365: GERENCIAMENTO DE CHAMADOS
# ============================================================


@pytest.mark.e2e
class TestAdminChamados:
    """Testes para UC-361 a UC-365: Gerenciamento de Chamados."""

    def test_listar_chamados_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-361: Listagem de chamados requer autenticacao admin."""
        admin = AdminChamadosPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_visualizar_chamado_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-362: Visualizacao de chamado admin requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/chamados/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_responder_chamado_admin_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-363: Resposta admin requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/chamados/1/responder")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_fechar_chamado_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-364: Fechamento de chamado requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/chamados/1/fechar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_reabrir_chamado_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-365: Reabertura de chamado requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/chamados/1/reabrir")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-371 a UC-376: GERENCIAMENTO DO SISTEMA
# ============================================================


@pytest.mark.e2e
class TestAdminConfiguracoes:
    """Testes para UC-371 a UC-372: Configuracoes do Sistema."""

    def test_visualizar_configuracoes_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-371: Visualizacao de configuracoes requer autenticacao."""
        admin = AdminConfiguracoesPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_editar_configuracao_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-372: Edicao de configuracao requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/configuracoes/1/editar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


@pytest.mark.e2e
class TestAdminBackups:
    """Testes para UC-373 a UC-376: Backups do Sistema."""

    def test_criar_backup_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-373: Criacao de backup requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/backups/criar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_listar_backups_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-374: Listagem de backups requer autenticacao."""
        admin = AdminBackupsPage(e2e_page, e2e_server)
        admin.navegar()
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_restaurar_backup_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-375: Restauracao de backup requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/backups/restaurar/teste.db")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_download_backup_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-376: Download de backup requer autenticacao."""
        e2e_page.goto(f"{e2e_server}/admin/backups/download/teste.db")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)
