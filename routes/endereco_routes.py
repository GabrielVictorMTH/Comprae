# =============================================================================
# Imports
# =============================================================================

# Standard library
from typing import Optional

# Third-party
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs
from dtos.endereco_dto import CriarEnderecoDTO, AlterarEnderecoDTO

# Models
from model.endereco_model import Endereco
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import endereco_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.template_util import criar_templates

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/usuario/endereco", tags=["Endereço do Usuário"])
templates_endereco = criar_templates()


# =============================================================================
# Rotas
# =============================================================================

@router.get("")
@requer_autenticacao()
async def get_endereco(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Visualizar endereço do usuário ou redirecionar para cadastro"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    endereco = endereco_repo.obter_endereco_usuario(usuario_logado.id)

    if endereco:
        return templates_endereco.TemplateResponse(
            "endereco/visualizar.html",
            {
                "request": request,
                "endereco": endereco,
                "usuario_logado": usuario_logado,
            },
        )
    else:
        # Usuário não tem endereço, redirecionar para cadastro
        return RedirectResponse(
            url="/usuario/endereco/cadastrar",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/cadastrar")
@requer_autenticacao()
async def get_cadastrar_endereco(
    request: Request, usuario_logado: Optional[UsuarioLogado] = None
):
    """Formulário para cadastrar endereço"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Verificar se o usuário já tem endereço
    if endereco_repo.usuario_tem_endereco(usuario_logado.id):
        informar_erro(request, "Você já possui um endereço cadastrado.")
        return RedirectResponse(
            url="/usuario/endereco",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return templates_endereco.TemplateResponse(
        "endereco/cadastrar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "dados": {},
        },
    )


@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar_endereco(
    request: Request,
    titulo: str = Form(),
    logradouro: str = Form(),
    numero: str = Form(),
    complemento: str = Form(""),
    bairro: str = Form(),
    cidade: str = Form(),
    uf: str = Form(),
    cep: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Processar cadastro de endereço"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Verificar se o usuário já tem endereço
    if endereco_repo.usuario_tem_endereco(usuario_logado.id):
        informar_erro(request, "Você já possui um endereço cadastrado.")
        return RedirectResponse(
            url="/usuario/endereco",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Armazenar dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "titulo": titulo,
        "logradouro": logradouro,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cidade": cidade,
        "uf": uf,
        "cep": cep,
    }

    try:
        # Validar com DTO
        dto = CriarEnderecoDTO(**dados_formulario)

        # Criar objeto Endereco
        endereco = Endereco(
            id=0,
            id_usuario=usuario_logado.id,
            titulo=dto.titulo,
            logradouro=dto.logradouro,
            numero=dto.numero,
            complemento=dto.complemento or "",
            bairro=dto.bairro,
            cidade=dto.cidade,
            uf=dto.uf,
            cep=dto.cep,
        )

        # Inserir no banco
        id_novo = endereco_repo.inserir(endereco)
        if id_novo:
            logger.info(f"Endereço cadastrado - Usuário ID: {usuario_logado.id}")
            informar_sucesso(request, "Endereço cadastrado com sucesso!")
            return RedirectResponse(
                url="/usuario/endereco",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao cadastrar endereço. Tente novamente.")
            return templates_endereco.TemplateResponse(
                "endereco/cadastrar.html",
                {
                    "request": request,
                    "dados": dados_formulario,
                    "usuario_logado": usuario_logado,
                },
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="endereco/cadastrar.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
            mensagem_flash="Há campos com erros de validação!",
        )


@router.get("/editar")
@requer_autenticacao()
async def get_editar_endereco(
    request: Request, usuario_logado: Optional[UsuarioLogado] = None
):
    """Formulário para editar endereço"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    endereco = endereco_repo.obter_endereco_usuario(usuario_logado.id)

    if not endereco:
        informar_erro(request, "Você não possui endereço cadastrado.")
        return RedirectResponse(
            url="/usuario/endereco/cadastrar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return templates_endereco.TemplateResponse(
        "endereco/editar.html",
        {
            "request": request,
            "dados": endereco.__dict__,
            "usuario_logado": usuario_logado,
        },
    )


@router.post("/editar")
@requer_autenticacao()
async def post_editar_endereco(
    request: Request,
    titulo: str = Form(),
    logradouro: str = Form(),
    numero: str = Form(),
    complemento: str = Form(""),
    bairro: str = Form(),
    cidade: str = Form(),
    uf: str = Form(),
    cep: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Processar edição de endereço"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    endereco = endereco_repo.obter_endereco_usuario(usuario_logado.id)

    if not endereco:
        informar_erro(request, "Endereço não encontrado.")
        return RedirectResponse(
            url="/usuario/endereco/cadastrar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar ownership
    if endereco.id_usuario != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para editar este endereço.")
        return RedirectResponse(
            url="/usuario/endereco",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Armazenar dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "id": endereco.id,
        "titulo": titulo,
        "logradouro": logradouro,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cidade": cidade,
        "uf": uf,
        "cep": cep,
    }

    try:
        # Validar com DTO
        dto = AlterarEnderecoDTO(**dados_formulario)

        # Atualizar objeto Endereco
        endereco.titulo = dto.titulo
        endereco.logradouro = dto.logradouro
        endereco.numero = dto.numero
        endereco.complemento = dto.complemento or ""
        endereco.bairro = dto.bairro
        endereco.cidade = dto.cidade
        endereco.uf = dto.uf
        endereco.cep = dto.cep

        # Salvar no banco
        if endereco_repo.alterar(endereco):
            logger.info(f"Endereço atualizado - Usuário ID: {usuario_logado.id}")
            informar_sucesso(request, "Endereço atualizado com sucesso!")
            return RedirectResponse(
                url="/usuario/endereco",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao atualizar endereço. Tente novamente.")
            return templates_endereco.TemplateResponse(
                "endereco/editar.html",
                {
                    "request": request,
                    "dados": dados_formulario,
                    "usuario_logado": usuario_logado,
                },
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="endereco/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
            mensagem_flash="Há campos com erros de validação!",
        )


@router.post("/excluir")
@requer_autenticacao()
async def post_excluir_endereco(
    request: Request,
    csrf_token: str = Form(default=""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Excluir endereço do usuário"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    endereco = endereco_repo.obter_endereco_usuario(usuario_logado.id)

    if not endereco:
        informar_erro(request, "Endereço não encontrado.")
        return RedirectResponse(
            url="/usuario/perfil/visualizar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar ownership
    if endereco.id_usuario != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para excluir este endereço.")
        return RedirectResponse(
            url="/usuario/endereco",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if endereco_repo.excluir(endereco.id):
        logger.info(f"Endereço excluído - Usuário ID: {usuario_logado.id}")
        informar_sucesso(request, "Endereço excluído com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir endereço. Tente novamente.")

    return RedirectResponse(
        url="/usuario/perfil/visualizar",
        status_code=status.HTTP_303_SEE_OTHER
    )
