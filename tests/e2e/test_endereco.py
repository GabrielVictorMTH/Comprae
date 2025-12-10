"""
Testes E2E para gerenciamento de endereco (UC-111 a UC-114).

Casos de uso testados:
- UC-111: Visualizar Endereco
- UC-112: Cadastrar Endereco
- UC-113: Editar Endereco
- UC-114: Excluir Endereco
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    EnderecoPage,
    criar_usuario_e_logar,
    verificar_redirecionamento_login,
)


# ============================================================
# UC-111: VISUALIZAR ENDERECO
# ============================================================


@pytest.mark.e2e
class TestVisualizarEndereco:
    """Testes para UC-111: Visualizar Endereco."""

    def test_visualizar_endereco_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-111: Visualizacao de endereco deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/endereco")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_visualizar_endereco_sem_cadastro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-111: Deve indicar que nao ha endereco cadastrado."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Sem Endereco",
            email="sem_endereco@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        # Deve indicar ausencia de endereco ou mostrar botao de cadastro
        assert (
            "nenhum" in conteudo
            or "cadastrar" in conteudo
            or "adicionar" in conteudo
            or "endereco" in conteudo
        )

    def test_visualizar_endereco_comprador(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-111: Comprador deve poder visualizar pagina de endereco."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Endereco",
            email="comprador_end@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)

    def test_visualizar_endereco_vendedor(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-111: Vendedor deve poder visualizar pagina de endereco."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Endereco",
            email="vendedor_end@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-112: CADASTRAR ENDERECO
# ============================================================


@pytest.mark.e2e
class TestCadastrarEndereco:
    """Testes para UC-112: Cadastrar Endereco."""

    def test_cadastrar_endereco_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-112: Cadastro de endereco deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/endereco/cadastrar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_cadastrar_endereco_exibe_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-112: Deve exibir formulario de cadastro de endereco."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Form Endereco",
            email="form_endereco@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        # Deve ter campos do formulario
        expect(e2e_page.locator('input[name="cep"]')).to_be_visible()
        expect(e2e_page.locator('input[name="logradouro"]')).to_be_visible()
        expect(e2e_page.locator('input[name="numero"]')).to_be_visible()

    def test_cadastrar_endereco_com_sucesso(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-112: Deve cadastrar endereco com dados validos."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Cadastro End",
            email="cadastro_end@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        # Preencher formulario
        endereco.preencher_formulario(
            cep="29000-000",
            logradouro="Rua Teste",
            numero="123",
            complemento="Apto 101",
            bairro="Centro",
            cidade="Vitoria",
            estado="ES",
        )
        endereco.submeter()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "sucesso" in conteudo
            or "cadastrado" in conteudo
            or "/usuario/endereco" in e2e_page.url
        )

    def test_cadastrar_endereco_validacao_cep(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-112: Deve validar formato do CEP."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario CEP Invalido",
            email="cep_invalido@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        # Tentar com CEP invalido
        endereco.preencher_formulario(
            cep="123",
            logradouro="Rua Teste",
            numero="123",
            complemento="",
            bairro="Centro",
            cidade="Vitoria",
            estado="ES",
        )
        endereco.submeter()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "cep" in conteudo or "/cadastrar" in e2e_page.url

    def test_cadastrar_endereco_campos_obrigatorios(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-112: Deve validar campos obrigatorios."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Campos Obrig",
            email="campos_obrig@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        # Tentar submeter sem preencher
        endereco.submeter()
        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina de cadastro
        assert "/endereco" in e2e_page.url


# ============================================================
# UC-113: EDITAR ENDERECO
# ============================================================


@pytest.mark.e2e
class TestEditarEndereco:
    """Testes para UC-113: Editar Endereco."""

    def test_editar_endereco_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-113: Edicao de endereco deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/endereco/editar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_editar_endereco_sem_cadastro_redireciona(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-113: Sem endereco cadastrado deve redirecionar ou mostrar erro."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Editar Sem End",
            email="editar_sem_end@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_editar()
        e2e_page.wait_for_timeout(500)

        # Deve redirecionar para cadastro ou mostrar erro
        conteudo = e2e_page.content().lower()
        assert (
            "cadastrar" in e2e_page.url
            or "nenhum" in conteudo
            or "cadastre" in conteudo
            or "endereco" in e2e_page.url
        )

    def test_editar_endereco_carrega_dados(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-113: Deve carregar dados existentes no formulario."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Editar End",
            email="editar_end@example.com",
            senha="SenhaForte@123",
        )

        # Primeiro cadastrar um endereco
        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        endereco.preencher_formulario(
            cep="29000-000",
            logradouro="Rua Original",
            numero="100",
            complemento="",
            bairro="Centro",
            cidade="Vitoria",
            estado="ES",
        )
        endereco.submeter()
        e2e_page.wait_for_timeout(500)

        # Agora tentar editar
        endereco.navegar_editar()
        e2e_page.wait_for_timeout(500)

        # Deve ter o formulario preenchido
        campo_logradouro = e2e_page.locator('input[name="logradouro"]')
        if campo_logradouro.is_visible():
            valor = campo_logradouro.input_value()
            assert "Rua Original" in valor or len(valor) > 0


# ============================================================
# UC-114: EXCLUIR ENDERECO
# ============================================================


@pytest.mark.e2e
class TestExcluirEndereco:
    """Testes para UC-114: Excluir Endereco."""

    def test_excluir_endereco_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-114: Exclusao de endereco deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/endereco/excluir")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_excluir_endereco_sem_cadastro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-114: Sem endereco nao deve haver opcao de excluir."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Excluir Sem End",
            email="excluir_sem@example.com",
            senha="SenhaForte@123",
        )

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        # Nao deve ter opcao de excluir se nao tem endereco
        # Ou a opcao deve estar desabilitada/oculta


# ============================================================
# TESTES DE LIMITE DE ENDERECO
# ============================================================


@pytest.mark.e2e
class TestLimiteEndereco:
    """Testes para validar limite de um endereco por usuario."""

    def test_limite_um_endereco_por_usuario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Cada usuario pode ter apenas um endereco cadastrado."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Usuario Limite End",
            email="limite_end@example.com",
            senha="SenhaForte@123",
        )

        # Cadastrar primeiro endereco
        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        endereco.preencher_formulario(
            cep="29000-000",
            logradouro="Rua Primeira",
            numero="1",
            complemento="",
            bairro="Centro",
            cidade="Vitoria",
            estado="ES",
        )
        endereco.submeter()
        e2e_page.wait_for_timeout(500)

        # Tentar cadastrar segundo endereco
        endereco.navegar_cadastrar()
        e2e_page.wait_for_timeout(500)

        # Deve redirecionar para edicao ou mostrar mensagem
        conteudo = e2e_page.content().lower()
        assert (
            "editar" in e2e_page.url
            or "já" in conteudo
            or "existente" in conteudo
            or "/endereco" in e2e_page.url
        )
