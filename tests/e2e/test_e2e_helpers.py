"""
Funcoes auxiliares e Page Objects para testes E2E.

Fornece helpers para interacoes comuns com a UI.
"""

from typing import Optional

from playwright.sync_api import Page, expect


class CadastroPage:
    """Page Object para a pagina de cadastro."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/cadastrar"

    def navegar(self) -> None:
        """Navega para a pagina de cadastro."""
        self.page.goto(self.url)

    def preencher_formulario(
        self,
        perfil: str,
        nome: str,
        email: str,
        senha: str,
        confirmar_senha: Optional[str] = None,
    ) -> None:
        """
        Preenche o formulario de cadastro.

        Args:
            perfil: "Comprador" ou "Vendedor"
            nome: Nome completo
            email: E-mail
            senha: Senha
            confirmar_senha: Confirmacao de senha (usa senha se nao informado)
        """
        if confirmar_senha is None:
            confirmar_senha = senha

        # Selecionar perfil (radio button com estilo de botao Bootstrap)
        # Precisamos clicar no label pois o input esta escondido
        self.page.locator(f'label[for="perfil_{perfil}"]').click()

        # Preencher campos
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="senha"]', senha)
        self.page.fill('input[name="confirmar_senha"]', confirmar_senha)

    def submeter(self) -> None:
        """Submete o formulario."""
        self.page.get_by_role("button", name="Criar Conta").click()

    def cadastrar(
        self,
        perfil: str,
        nome: str,
        email: str,
        senha: str,
        confirmar_senha: Optional[str] = None,
    ) -> None:
        """
        Realiza cadastro completo: preenche e submete.
        """
        self.preencher_formulario(perfil, nome, email, senha, confirmar_senha)
        self.submeter()

    def obter_mensagem_erro_campo(self, campo: str) -> Optional[str]:
        """
        Obtem mensagem de erro de um campo especifico.

        Args:
            campo: Nome do campo (nome, email, senha, confirmar_senha)

        Returns:
            Texto da mensagem de erro ou None
        """
        seletor = f'input[name="{campo}"] ~ .invalid-feedback'
        elemento = self.page.locator(seletor).first

        if elemento.is_visible():
            return elemento.text_content()
        return None

    def obter_mensagem_flash(self) -> Optional[str]:
        """
        Obtem mensagem flash (toast ou alert).

        Returns:
            Texto da mensagem ou None
        """
        toast = self.page.locator(".toast-body").first
        if toast.is_visible():
            return toast.text_content()

        alert = self.page.locator(".alert").first
        if alert.is_visible():
            return alert.text_content()

        return None

    def aguardar_navegacao_login(self, timeout: int = 5000) -> bool:
        """
        Aguarda redirecionamento para pagina de login.

        Args:
            timeout: Tempo maximo em ms

        Returns:
            True se redirecionou, False caso contrario
        """
        try:
            self.page.wait_for_url("**/login**", timeout=timeout)
            return True
        except Exception:
            return False


class LoginPage:
    """Page Object para a pagina de login."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/login"

    def navegar(self) -> None:
        """Navega para a pagina de login."""
        self.page.goto(self.url)

    def preencher_formulario(self, email: str, senha: str) -> None:
        """Preenche o formulario de login sem submeter."""
        self.page.wait_for_selector('input[name="email"]')
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="senha"]', senha)

    def submeter(self) -> None:
        """Submete o formulario de login."""
        self.page.locator('form button[type="submit"]').first.click()

    def fazer_login(self, email: str, senha: str) -> None:
        """Preenche e submete formulario de login."""
        self.preencher_formulario(email, senha)
        self.submeter()

    def esta_na_pagina_login(self) -> bool:
        """Verifica se esta na pagina de login."""
        return "/login" in self.page.url

    def aguardar_navegacao_usuario(self, timeout: int = 10000) -> bool:
        """
        Aguarda redirecionamento para area do usuario.

        Args:
            timeout: Tempo maximo em ms

        Returns:
            True se redirecionou, False caso contrario
        """
        try:
            self.page.wait_for_url("**/usuario**", timeout=timeout)
            return True
        except Exception:
            # Pode ter ido para /home
            return "/usuario" in self.page.url or "/home" in self.page.url

    def obter_mensagem_flash(self) -> Optional[str]:
        """
        Obtem mensagem flash (toast ou alert).

        Returns:
            Texto da mensagem ou None
        """
        toast = self.page.locator(".toast-body").first
        if toast.is_visible():
            return toast.text_content()

        alert = self.page.locator(".alert").first
        if alert.is_visible():
            return alert.text_content()

        return None


class HomePage:
    """Page Object para a pagina inicial."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/"

    def navegar(self) -> None:
        """Navega para a pagina inicial."""
        self.page.goto(self.url)

    def esta_na_home(self) -> bool:
        """Verifica se esta na pagina inicial."""
        url = self.page.url.rstrip("/")
        base = self.base_url.rstrip("/")
        return url == base or "/index" in self.page.url


class SobrePage:
    """Page Object para a pagina sobre."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/sobre"

    def navegar(self) -> None:
        """Navega para a pagina sobre."""
        self.page.goto(self.url)


class ProdutosPage:
    """Page Object para a pagina de produtos (anuncios)."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/anuncios"

    def navegar(self) -> None:
        """Navega para a pagina de produtos."""
        self.page.goto(self.url)

    def buscar(self, termo: str) -> None:
        """Realiza busca por termo."""
        self.page.fill('input[name="busca"]', termo)
        self.page.locator('button[type="submit"]').first.click()

    def visualizar_produto(self, indice: int = 0) -> None:
        """Clica no produto pelo indice."""
        self.page.locator(".card").nth(indice).click()


class PerfilPage:
    """Page Object para a pagina de perfil do usuario."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/usuario"

    def navegar(self) -> None:
        """Navega para a pagina de perfil."""
        self.page.goto(self.url)

    def navegar_visualizar(self) -> None:
        """Navega para visualizacao do perfil."""
        self.page.goto(f"{self.base_url}/usuario/perfil/visualizar")

    def navegar_editar(self) -> None:
        """Navega para edicao de perfil."""
        self.page.goto(f"{self.base_url}/usuario/perfil/editar")

    def navegar_alterar_senha(self) -> None:
        """Navega para alteracao de senha."""
        self.page.goto(f"{self.base_url}/usuario/perfil/alterar-senha")

    def preencher_edicao(self, nome: str, email: str) -> None:
        """Preenche formulario de edicao."""
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('input[name="email"]', email)

    def submeter(self) -> None:
        """Submete o formulario."""
        self.page.locator('button[type="submit"]').first.click()


class EnderecoPage:
    """Page Object para gerenciamento de endereco."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/usuario/endereco"

    def navegar(self) -> None:
        """Navega para a pagina de endereco."""
        self.page.goto(self.url)

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de endereco."""
        self.page.goto(f"{self.base_url}/usuario/endereco/cadastrar")

    def navegar_editar(self) -> None:
        """Navega para edicao de endereco."""
        self.page.goto(f"{self.base_url}/usuario/endereco/editar")

    def preencher_formulario(
        self,
        cep: str,
        logradouro: str,
        numero: str,
        complemento: str,
        bairro: str,
        cidade: str,
        uf: str,
        titulo: str = "Casa",
    ) -> None:
        """Preenche formulario de endereco."""
        self.page.fill('input[name="titulo"]', titulo)
        self.page.fill('input[name="logradouro"]', logradouro)
        self.page.fill('input[name="numero"]', numero)
        self.page.fill('input[name="complemento"]', complemento)
        self.page.fill('input[name="bairro"]', bairro)
        self.page.fill('input[name="cidade"]', cidade)
        self.page.select_option('select[name="uf"]', uf)
        self.page.fill('input[name="cep"]', cep)

    def submeter(self) -> None:
        """Submete o formulario."""
        self.page.locator('button[type="submit"]').first.click()


class MeusPedidosPage:
    """Page Object para listagem de pedidos do comprador."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/usuario/pedidos"

    def navegar(self) -> None:
        """Navega para a pagina de pedidos."""
        self.page.goto(self.url)

    def visualizar_pedido(self, indice: int = 0) -> None:
        """Clica no pedido pelo indice."""
        self.page.locator("table tbody tr").nth(indice).locator("a").first.click()


class CriarPedidoPage:
    """Page Object para criacao de pedido."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def criar_pedido(self, anuncio_id: int, quantidade: int = 1) -> None:
        """Navega para criacao de pedido."""
        self.page.goto(f"{self.base_url}/usuario/pedidos/criar/{anuncio_id}")
        self.page.fill('input[name="quantidade"]', str(quantidade))
        self.page.locator('button[type="submit"]').first.click()


class ChamadosPage:
    """Page Object para gerenciamento de chamados."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/usuario/chamados"

    def navegar(self) -> None:
        """Navega para listagem de chamados."""
        self.page.goto(self.url)

    def navegar_criar(self) -> None:
        """Navega para criacao de chamado."""
        self.page.goto(f"{self.base_url}/usuario/chamados/criar")

    def preencher_formulario(self, assunto: str, mensagem: str) -> None:
        """Preenche formulario de chamado."""
        self.page.fill('input[name="assunto"]', assunto)
        self.page.fill('textarea[name="mensagem"]', mensagem)

    def submeter(self) -> None:
        """Submete o formulario."""
        self.page.locator('button[type="submit"]').first.click()

    def visualizar_chamado(self, indice: int = 0) -> None:
        """Clica no chamado pelo indice."""
        self.page.locator("table tbody tr").nth(indice).locator("a").first.click()

    def responder(self, mensagem: str) -> None:
        """Responde ao chamado."""
        self.page.fill('textarea[name="mensagem"]', mensagem)
        self.page.locator('button[type="submit"]').first.click()


class ChatPage:
    """Page Object para o chat."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/usuario/chat"

    def navegar(self) -> None:
        """Navega para listagem de conversas."""
        self.page.goto(self.url)

    def iniciar_chat(self, usuario_id: int) -> None:
        """Inicia chat com um usuario."""
        self.page.goto(f"{self.base_url}/usuario/chat/{usuario_id}")

    def enviar_mensagem(self, mensagem: str) -> None:
        """Envia mensagem no chat."""
        self.page.fill('input[name="mensagem"]', mensagem)
        self.page.locator('button[type="submit"]').first.click()


class MeusProdutosPage:
    """Page Object para listagem de produtos do vendedor."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/usuario/anuncios"

    def navegar(self) -> None:
        """Navega para listagem de produtos."""
        self.page.goto(self.url)

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de produto."""
        self.page.goto(f"{self.base_url}/usuario/anuncios/cadastrar")

    def preencher_formulario(
        self,
        titulo: str,
        descricao: str,
        preco: str,
        estoque: str,
        categoria_id: int = 1,
    ) -> None:
        """Preenche formulario de produto."""
        self.page.fill('input[name="titulo"]', titulo)
        self.page.fill('textarea[name="descricao"]', descricao)
        self.page.fill('input[name="preco"]', preco)
        self.page.fill('input[name="estoque"]', estoque)
        self.page.select_option('select[name="categoria_id"]', str(categoria_id))

    def submeter(self) -> None:
        """Submete o formulario."""
        self.page.locator('button[type="submit"]').first.click()


class PedidosRecebidosPage:
    """Page Object para pedidos recebidos do vendedor."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/usuario/pedidos-recebidos"

    def navegar(self) -> None:
        """Navega para listagem de pedidos recebidos."""
        self.page.goto(self.url)

    def visualizar_pedido(self, indice: int = 0) -> None:
        """Clica no pedido pelo indice."""
        self.page.locator("table tbody tr").nth(indice).locator("a").first.click()


class AdminUsuariosPage:
    """Page Object para administracao de usuarios."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/admin/usuarios/listar"

    def navegar(self) -> None:
        """Navega para listagem de usuarios."""
        self.page.goto(self.url)

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de usuario."""
        self.page.goto(f"{self.base_url}/admin/usuarios/cadastrar")


class AdminProdutosPage:
    """Page Object para administracao de produtos."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/admin/anuncios/listar"

    def navegar(self) -> None:
        """Navega para listagem de produtos."""
        self.page.goto(self.url)

    def navegar_moderar(self) -> None:
        """Navega para moderacao de produtos."""
        self.page.goto(f"{self.base_url}/admin/anuncios/moderar")


class AdminPedidosPage:
    """Page Object para administracao de pedidos."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/admin/pedidos/listar"

    def navegar(self) -> None:
        """Navega para listagem de pedidos."""
        self.page.goto(self.url)


class AdminCategoriasPage:
    """Page Object para administracao de categorias."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/admin/categorias/listar"

    def navegar(self) -> None:
        """Navega para listagem de categorias."""
        self.page.goto(self.url)

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de categoria."""
        self.page.goto(f"{self.base_url}/admin/categorias/cadastrar")

    def preencher_formulario(self, nome: str) -> None:
        """Preenche formulario de categoria."""
        self.page.fill('input[name="nome"]', nome)

    def submeter(self) -> None:
        """Submete o formulario."""
        self.page.locator('button[type="submit"]').first.click()


class AdminChamadosPage:
    """Page Object para administracao de chamados."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/admin/chamados/listar"

    def navegar(self) -> None:
        """Navega para listagem de chamados."""
        self.page.goto(self.url)


class AdminConfiguracoesPage:
    """Page Object para configuracoes do sistema."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/admin/configuracoes"

    def navegar(self) -> None:
        """Navega para configuracoes."""
        self.page.goto(self.url)


class AdminBackupsPage:
    """Page Object para backups do sistema."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/admin/backups/listar"

    def navegar(self) -> None:
        """Navega para listagem de backups."""
        self.page.goto(self.url)


class RecuperarSenhaPage:
    """Page Object para recuperacao de senha."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/esqueci-senha"

    def navegar(self) -> None:
        """Navega para pagina de recuperacao."""
        self.page.goto(self.url)

    def solicitar_recuperacao(self, email: str) -> None:
        """Solicita recuperacao de senha."""
        self.page.fill('input[name="email"]', email)
        self.page.locator('button[type="submit"]').first.click()


# ============================================================
# FUNCOES AUXILIARES
# ============================================================


def verificar_mensagem_sucesso_cadastro(page: Page) -> bool:
    """
    Verifica se a mensagem de sucesso do cadastro foi exibida.

    A mensagem esperada e: "Cadastro realizado com sucesso!"
    """
    try:
        toast = page.locator(".toast-body")
        if toast.is_visible():
            texto = toast.text_content() or ""
            return "cadastro realizado com sucesso" in texto.lower()

        alert = page.locator(".alert-success")
        if alert.is_visible():
            texto = alert.text_content() or ""
            return "cadastro realizado com sucesso" in texto.lower()
    except Exception:
        pass

    return False


def verificar_erro_email_duplicado(page: Page) -> bool:
    """
    Verifica se apareceu erro de e-mail duplicado.

    A mensagem esperada contem: "e-mail ja esta cadastrado"
    """
    try:
        conteudo = page.content().lower()
        return "e-mail" in conteudo and "cadastrado" in conteudo
    except Exception:
        return False


def verificar_erro_senhas_diferentes(page: Page) -> bool:
    """
    Verifica se apareceu erro de senhas nao coincidentes.

    A mensagem esperada: "As senhas nao coincidem."
    """
    try:
        conteudo = page.content().lower()
        return "senhas" in conteudo and "coincidem" in conteudo
    except Exception:
        return False


def criar_usuario_e_logar(
    page: Page,
    base_url: str,
    perfil: str,
    nome: str,
    email: str,
    senha: str,
) -> bool:
    """
    Helper para criar usuario e fazer login.

    Returns:
        True se login foi bem sucedido
    """
    cadastro = CadastroPage(page, base_url)
    cadastro.navegar()
    cadastro.cadastrar(perfil=perfil, nome=nome, email=email, senha=senha)
    cadastro.aguardar_navegacao_login()

    login = LoginPage(page, base_url)
    login.fazer_login(email, senha)
    return login.aguardar_navegacao_usuario()


def verificar_redirecionamento_login(page: Page) -> bool:
    """Verifica se foi redirecionado para login (acesso negado)."""
    return "/login" in page.url


def verificar_pagina_carregou(page: Page, texto_esperado: str) -> bool:
    """Verifica se a pagina carregou verificando texto no conteudo."""
    try:
        conteudo = page.content().lower()
        return texto_esperado.lower() in conteudo
    except Exception:
        return False
