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
from dtos.anuncio_dto import CriarAnuncioDTO, AlterarAnuncioDTO

# Models
from model.anuncio_model import Anuncio
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import anuncio_repo, categoria_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.foto_anuncio_util import salvar_foto_anuncio, excluir_foto_anuncio
from util.logger_config import logger
from util.perfis import Perfil
from util.template_util import criar_templates

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/vendedor/anuncios", tags=["Anúncios do Vendedor"])
templates_anuncio = criar_templates()


# =============================================================================
# Rotas
# =============================================================================

@router.get("")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def listar_anuncios(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista os anúncios do vendedor logado"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    anuncios = anuncio_repo.obter_por_vendedor(usuario_logado.id)

    return templates_anuncio.TemplateResponse(
        "vendedor/anuncios/listar.html",
        {
            "request": request,
            "anuncios": anuncios,
            "usuario_logado": usuario_logado,
        },
    )


@router.get("/cadastrar")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def get_cadastrar_anuncio(
    request: Request, usuario_logado: Optional[UsuarioLogado] = None
):
    """Formulário para cadastrar anúncio"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    categorias = categoria_repo.obter_todos()

    return templates_anuncio.TemplateResponse(
        "vendedor/anuncios/cadastrar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categorias": categorias,
            "dados": {},
        },
    )


@router.post("/cadastrar")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def post_cadastrar_anuncio(
    request: Request,
    nome: str = Form(),
    descricao: str = Form(),
    id_categoria: int = Form(),
    peso: float = Form(),
    preco: float = Form(),
    estoque: int = Form(),
    foto_base64: str = Form(""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Processar cadastro de anúncio"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    categorias = categoria_repo.obter_todos()

    # Armazenar dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "nome": nome,
        "descricao": descricao,
        "id_categoria": id_categoria,
        "peso": peso,
        "preco": preco,
        "estoque": estoque,
    }

    try:
        # Validar com DTO
        dto = CriarAnuncioDTO(**dados_formulario)

        # Criar objeto Anuncio
        anuncio = Anuncio(
            id=0,
            id_vendedor=usuario_logado.id,
            id_categoria=dto.id_categoria,
            nome=dto.nome,
            descricao=dto.descricao,
            peso=dto.peso,
            preco=dto.preco,
            estoque=dto.estoque,
            data_cadastro=None,
            ativo=True,
        )

        # Inserir no banco
        anuncio_inserido = anuncio_repo.inserir(anuncio)
        if anuncio_inserido:
            # Salvar foto se foi enviada
            if foto_base64 and len(foto_base64) > 100:
                salvar_foto_anuncio(anuncio_inserido.id, foto_base64)

            logger.info(f"Anúncio cadastrado ID: {anuncio_inserido.id} - Vendedor: {usuario_logado.id}")
            informar_sucesso(request, "Anúncio cadastrado com sucesso!")
            return RedirectResponse(
                url="/vendedor/anuncios",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao cadastrar anúncio. Tente novamente.")
            return templates_anuncio.TemplateResponse(
                "vendedor/anuncios/cadastrar.html",
                {
                    "request": request,
                    "dados": dados_formulario,
                    "categorias": categorias,
                    "usuario_logado": usuario_logado,
                },
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="vendedor/anuncios/cadastrar.html",
            dados_formulario={**dados_formulario, "categorias": categorias},
            campo_padrao="nome",
            mensagem_flash="Há campos com erros de validação!",
        )


@router.get("/editar/{id}")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def get_editar_anuncio(
    request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None
):
    """Formulário para editar anúncio"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Anúncio não encontrado.")
        return RedirectResponse(
            url="/vendedor/anuncios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar ownership
    if anuncio.id_vendedor != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para editar este anúncio.")
        return RedirectResponse(
            url="/vendedor/anuncios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    categorias = categoria_repo.obter_todos()

    return templates_anuncio.TemplateResponse(
        "vendedor/anuncios/editar.html",
        {
            "request": request,
            "dados": anuncio.__dict__,
            "anuncio": anuncio,
            "categorias": categorias,
            "usuario_logado": usuario_logado,
        },
    )


@router.post("/editar/{id}")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def post_editar_anuncio(
    request: Request,
    id: int,
    nome: str = Form(),
    descricao: str = Form(),
    id_categoria: int = Form(),
    peso: float = Form(),
    preco: float = Form(),
    estoque: int = Form(),
    ativo: bool = Form(False),
    foto_base64: str = Form(""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Processar edição de anúncio"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Anúncio não encontrado.")
        return RedirectResponse(
            url="/vendedor/anuncios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar ownership
    if anuncio.id_vendedor != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para editar este anúncio.")
        return RedirectResponse(
            url="/vendedor/anuncios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    categorias = categoria_repo.obter_todos()

    # Armazenar dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "id": id,
        "nome": nome,
        "descricao": descricao,
        "id_categoria": id_categoria,
        "peso": peso,
        "preco": preco,
        "estoque": estoque,
        "ativo": ativo,
    }

    try:
        # Validar com DTO
        dto = AlterarAnuncioDTO(**dados_formulario)

        # Atualizar objeto Anuncio
        anuncio.id_categoria = dto.id_categoria
        anuncio.nome = dto.nome
        anuncio.descricao = dto.descricao
        anuncio.peso = dto.peso
        anuncio.preco = dto.preco
        anuncio.estoque = dto.estoque
        anuncio.ativo = dto.ativo

        # Salvar no banco
        if anuncio_repo.alterar(anuncio):
            # Salvar foto se foi enviada nova
            if foto_base64 and len(foto_base64) > 100:
                salvar_foto_anuncio(anuncio.id, foto_base64)

            logger.info(f"Anúncio atualizado ID: {anuncio.id} - Vendedor: {usuario_logado.id}")
            informar_sucesso(request, "Anúncio atualizado com sucesso!")
            return RedirectResponse(
                url="/vendedor/anuncios",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao atualizar anúncio. Tente novamente.")
            return templates_anuncio.TemplateResponse(
                "vendedor/anuncios/editar.html",
                {
                    "request": request,
                    "dados": dados_formulario,
                    "anuncio": anuncio,
                    "categorias": categorias,
                    "usuario_logado": usuario_logado,
                },
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="vendedor/anuncios/editar.html",
            dados_formulario={**dados_formulario, "categorias": categorias, "anuncio": anuncio},
            campo_padrao="nome",
            mensagem_flash="Há campos com erros de validação!",
        )


@router.post("/excluir/{id}")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def post_excluir_anuncio(
    request: Request,
    id: int,
    csrf_token: str = Form(default=""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Excluir anúncio"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Anúncio não encontrado.")
        return RedirectResponse(
            url="/vendedor/anuncios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar ownership
    if anuncio.id_vendedor != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para excluir este anúncio.")
        return RedirectResponse(
            url="/vendedor/anuncios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if anuncio_repo.excluir(id):
        # Excluir foto do anúncio
        excluir_foto_anuncio(id)
        logger.info(f"Anúncio excluído ID: {id} - Vendedor: {usuario_logado.id}")
        informar_sucesso(request, "Anúncio excluído com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir anúncio. Pode haver pedidos vinculados.")

    return RedirectResponse(
        url="/vendedor/anuncios",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/ativar/{id}")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def post_toggle_ativo(
    request: Request,
    id: int,
    csrf_token: str = Form(default=""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Toggle ativo/inativo do anúncio"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Anúncio não encontrado.")
        return RedirectResponse(
            url="/vendedor/anuncios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar ownership
    if anuncio.id_vendedor != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para modificar este anúncio.")
        return RedirectResponse(
            url="/vendedor/anuncios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Toggle status
    anuncio.ativo = not anuncio.ativo

    if anuncio_repo.alterar(anuncio):
        status_msg = "ativado" if anuncio.ativo else "desativado"
        logger.info(f"Anúncio {status_msg} ID: {id} - Vendedor: {usuario_logado.id}")
        informar_sucesso(request, f"Anúncio {status_msg} com sucesso!")
    else:
        informar_erro(request, "Erro ao alterar status do anúncio.")

    return RedirectResponse(
        url="/vendedor/anuncios",
        status_code=status.HTTP_303_SEE_OTHER
    )
