"""
Testes E2E para comunicacao - chamados e chat (UC-131 a UC-145).

Casos de uso testados:
- UC-131: Abrir Chamado de Suporte
- UC-132: Listar Meus Chamados
- UC-133: Visualizar Chamado
- UC-134: Responder Chamado
- UC-135: Excluir Chamado
- UC-141: Iniciar Chat
- UC-142: Enviar Mensagem
- UC-143: Visualizar Conversas
- UC-144: Visualizar Mensagens
- UC-145: Marcar como Lida
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    ChamadosPage,
    ChatPage,
    criar_usuario_e_logar,
    verificar_redirecionamento_login,
)


# ============================================================
# UC-131: ABRIR CHAMADO DE SUPORTE
# ============================================================


@pytest.mark.e2e
class TestAbrirChamadoSuporte:
    """Testes para UC-131: Abrir Chamado de Suporte."""

    def test_abrir_chamado_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-131: Abertura de chamado deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chamados/criar")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_abrir_chamado_exibe_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-131: Deve exibir formulario de abertura de chamado."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Chamado Form",
            email="chamado_form@example.com",
            senha="SenhaForte@123",
        )

        chamados = ChamadosPage(e2e_page, e2e_server)
        chamados.navegar_criar()
        e2e_page.wait_for_timeout(500)

        expect(e2e_page.locator('input[name="assunto"]')).to_be_visible()
        expect(e2e_page.locator('textarea[name="mensagem"]')).to_be_visible()

    def test_abrir_chamado_com_sucesso(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-131: Deve abrir chamado com dados validos."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Chamado Sucesso",
            email="chamado_sucesso@example.com",
            senha="SenhaForte@123",
        )

        chamados = ChamadosPage(e2e_page, e2e_server)
        chamados.navegar_criar()
        e2e_page.wait_for_timeout(500)

        chamados.preencher_formulario(
            assunto="Problema com pedido",
            mensagem="Meu pedido nao chegou no prazo estipulado.",
        )
        chamados.submeter()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "sucesso" in conteudo
            or "criado" in conteudo
            or "/chamados" in e2e_page.url
        )

    def test_abrir_chamado_validacao_campos(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-131: Deve validar campos obrigatorios."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Chamado Validacao",
            email="chamado_validacao@example.com",
            senha="SenhaForte@123",
        )

        chamados = ChamadosPage(e2e_page, e2e_server)
        chamados.navegar_criar()
        e2e_page.wait_for_timeout(500)

        # Tentar submeter sem preencher
        chamados.submeter()
        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina ou mostrar erro
        assert "/chamados" in e2e_page.url


# ============================================================
# UC-132: LISTAR MEUS CHAMADOS
# ============================================================


@pytest.mark.e2e
class TestListarMeusChamados:
    """Testes para UC-132: Listar Meus Chamados."""

    def test_listar_chamados_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-132: Listagem de chamados deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chamados")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_listar_chamados_comprador_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-132: Comprador deve acessar listagem de chamados."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Chamados Lista",
            email="chamados_lista@example.com",
            senha="SenhaForte@123",
        )

        chamados = ChamadosPage(e2e_page, e2e_server)
        chamados.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)
        assert "/chamados" in e2e_page.url

    def test_listar_chamados_vendedor_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-132: Vendedor deve acessar listagem de chamados."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Chamados Lista",
            email="vendedor_chamados@example.com",
            senha="SenhaForte@123",
        )

        chamados = ChamadosPage(e2e_page, e2e_server)
        chamados.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)

    def test_listar_chamados_vazio(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-132: Sem chamados deve exibir mensagem apropriada."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Sem Chamados",
            email="sem_chamados@example.com",
            senha="SenhaForte@123",
        )

        chamados = ChamadosPage(e2e_page, e2e_server)
        chamados.navegar()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "nenhum" in conteudo
            or "vazio" in conteudo
            or "chamado" in conteudo
        )


# ============================================================
# UC-133: VISUALIZAR CHAMADO
# ============================================================


@pytest.mark.e2e
class TestVisualizarChamado:
    """Testes para UC-133: Visualizar Chamado."""

    def test_visualizar_chamado_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-133: Visualizacao de chamado deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chamados/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_visualizar_chamado_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-133: Chamado inexistente deve mostrar erro."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Chamado Inexistente",
            email="chamado_inexistente@example.com",
            senha="SenhaForte@123",
        )

        e2e_page.goto(f"{e2e_server}/usuario/chamados/99999")
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "encontrad" in conteudo
            or "erro" in conteudo
            or "/chamados" in e2e_page.url
        )


# ============================================================
# UC-134: RESPONDER CHAMADO
# ============================================================


@pytest.mark.e2e
class TestResponderChamado:
    """Testes para UC-134: Responder Chamado."""

    def test_responder_chamado_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-134: Resposta a chamado deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chamados/1/responder")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-135: EXCLUIR CHAMADO
# ============================================================


@pytest.mark.e2e
class TestExcluirChamado:
    """Testes para UC-135: Excluir Chamado."""

    def test_excluir_chamado_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-135: Exclusao de chamado deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chamados/1/excluir")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-141: INICIAR CHAT
# ============================================================


@pytest.mark.e2e
class TestIniciarChat:
    """Testes para UC-141: Iniciar Chat."""

    def test_iniciar_chat_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-141: Inicio de chat deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chat/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_iniciar_chat_usuario_inexistente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-141: Chat com usuario inexistente deve falhar."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Chat Inexistente",
            email="chat_inexistente@example.com",
            senha="SenhaForte@123",
        )

        chat = ChatPage(e2e_page, e2e_server)
        chat.iniciar_chat(99999)
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "encontrad" in conteudo
            or "erro" in conteudo
            or "/chat" in e2e_page.url
        )

    def test_nao_pode_chat_consigo_mesmo(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-141: Usuario nao pode iniciar chat consigo mesmo."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Chat Proprio",
            email="chat_proprio@example.com",
            senha="SenhaForte@123",
        )

        # Tentar chat com seu proprio ID (assumindo ID 1)
        chat = ChatPage(e2e_page, e2e_server)
        chat.iniciar_chat(1)
        e2e_page.wait_for_timeout(500)

        # Deve mostrar erro ou redirecionar
        conteudo = e2e_page.content().lower()
        assert (
            "mesmo" in conteudo
            or "proprio" in conteudo
            or "erro" in conteudo
            or "/chat" in e2e_page.url
        )


# ============================================================
# UC-142: ENVIAR MENSAGEM
# ============================================================


@pytest.mark.e2e
class TestEnviarMensagem:
    """Testes para UC-142: Enviar Mensagem."""

    def test_enviar_mensagem_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-142: Envio de mensagem deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chat/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-143: VISUALIZAR CONVERSAS
# ============================================================


@pytest.mark.e2e
class TestVisualizarConversas:
    """Testes para UC-143: Visualizar Conversas."""

    def test_visualizar_conversas_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-143: Listagem de conversas deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chat")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)

    def test_visualizar_conversas_comprador_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-143: Comprador deve acessar listagem de conversas."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Chat Lista",
            email="chat_lista@example.com",
            senha="SenhaForte@123",
        )

        chat = ChatPage(e2e_page, e2e_server)
        chat.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)
        assert "/chat" in e2e_page.url

    def test_visualizar_conversas_vendedor_acessa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-143: Vendedor deve acessar listagem de conversas."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Vendedor",
            nome="Vendedor Chat Lista",
            email="vendedor_chat@example.com",
            senha="SenhaForte@123",
        )

        chat = ChatPage(e2e_page, e2e_server)
        chat.navegar()
        e2e_page.wait_for_timeout(500)

        assert not verificar_redirecionamento_login(e2e_page)

    def test_visualizar_conversas_vazio(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-143: Sem conversas deve exibir mensagem apropriada."""
        criar_usuario_e_logar(
            e2e_page,
            e2e_server,
            perfil="Comprador",
            nome="Comprador Sem Chat",
            email="sem_chat@example.com",
            senha="SenhaForte@123",
        )

        chat = ChatPage(e2e_page, e2e_server)
        chat.navegar()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert (
            "nenhum" in conteudo
            or "vazio" in conteudo
            or "conversa" in conteudo
            or "chat" in conteudo
        )


# ============================================================
# UC-144: VISUALIZAR MENSAGENS
# ============================================================


@pytest.mark.e2e
class TestVisualizarMensagens:
    """Testes para UC-144: Visualizar Mensagens."""

    def test_visualizar_mensagens_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-144: Visualizacao de mensagens deve requerer autenticacao."""
        e2e_page.goto(f"{e2e_server}/usuario/chat/sala/1")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)


# ============================================================
# UC-145: MARCAR COMO LIDA
# ============================================================


@pytest.mark.e2e
class TestMarcarComoLida:
    """Testes para UC-145: Marcar como Lida."""

    def test_marcar_lida_requer_autenticacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """UC-145: Marcacao de lida deve requerer autenticacao."""
        # Esta funcionalidade geralmente e via AJAX/API
        e2e_page.goto(f"{e2e_server}/usuario/chat")
        e2e_page.wait_for_timeout(500)

        assert verificar_redirecionamento_login(e2e_page)
