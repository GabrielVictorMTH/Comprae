from typing import Optional
from fastapi import APIRouter, Form, Request, logger, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from model.curtida_model import Curtida
from repo import curtida_repo
from util.auth_decorator import requer_autenticacao
from util.exceptions import FormValidationError
from util.flash_messages import informar_erro, informar_sucesso
from util.perfis import Perfil
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.template_util import criar_templates


router = APIRouter(prefix="/admin/curtidas")
templates = criar_templates()

admin_curtidas_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_curtidas",
)

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista"""
    return RedirectResponse("/admin/curtidas/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os registros"""
    itens = curtida_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/curtidas/listar.html",
        {"request": request, "itens": itens}
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro"""
    return templates.TemplateResponse(
        "admin/curtidas/cadastro.html",
        {"request": request}
    )

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    # Liste aqui todos os campos do formulário:
    id_usuario: str = Form(...),
    id_anuncio: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Cadastra um novo registro"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_curtidas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/curtidas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "id_usuario": id_usuario,
        "id_anuncio": id_anuncio,
    }

    try:
        # Criar objeto
        item = Curtida(
            id_usuario=id_usuario,
            id_anuncio=id_anuncio
        )

        curtida_repo.inserir(item)
        logger.info(f"Curtida cadastrada por admin {usuario_logado['nome']}:{item}")

        informar_sucesso(request, "Curtida cadastrada com sucesso!")
        return RedirectResponse("/admin/curtidas/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/curtidas/cadastro.html",
            dados_formulario=dados_formulario
        )
    
@router.get("/editar/{id_usuario}/{id_anuncio}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id_usuario: int, id_anuncio: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de alteração"""
    item = curtida_repo.obter_por_id(id_usuario, id_anuncio)

    if not item:
        informar_erro(request, "Curtida não encontrada")
        return RedirectResponse("/admin/curtidas/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/curtidas/editar.html",
        {
            "request": request,
            "item": item,
            "dados": item.__dict__
        }
    )

@router.post("/editar/{id_usuario}/{id_anuncio}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id_usuario: int,
    id_anuncio: int,
    usuario_logado: Optional[dict] = None
):
    """Altera dados de um registro"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_curtidas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/curtidas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se existe
    item_atual = curtida_repo.obter_por_id(id_usuario, id_anuncio)
    if not item_atual:
        informar_erro(request, "Curtida não encontrada")
        return RedirectResponse("/admin/curtidas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "id_usuario": id_usuario,
        "id_anuncio": id_anuncio
    }

    try:
        # Atualizar objeto
        item_atualizado = [Curtida](
            id_usuario=id_usuario,
            id_anuncio=id_anuncio
        )

        curtida_repo.alterar(item_atualizado)
        logger.info(f"Curtida {id_anuncio} alterada por admin {usuario_logado['nome']}")

        informar_sucesso(request, "Curtida alterada com sucesso!")
        return RedirectResponse("/admin/curtida/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Adicionar item aos dados para renderizar o template
        dados_formulario = curtida_repo.obter_por_id(id_usuario, id_anuncio)
        raise FormValidationError(
            validation_error=e,
            template_path="admin/curtidas/editar.html",
            dados_formulario=dados_formulario.__dict__
        )

@router.post("/excluir/{id_usuario}/{id_anuncio}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id_usuario: int, id_anuncio: int, usuario_logado: Optional[dict] = None):
    """Exclui um registro"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_curtidas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/[seu_recurso]/listar", status_code=status.HTTP_303_SEE_OTHER)

    item = curtida_repo.obter_por_id(id_usuario, id_anuncio)

    if not item:
        informar_erro(request, "Curtida não encontrada")
        return RedirectResponse("/admin/curtidas/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        curtida_repo.excluir(id_usuario, id_anuncio)
        logger.info(f"Curtida excluída por admin {usuario_logado['nome']}")
        informar_sucesso(request, "Curtida excluída com sucesso!")
    except Exception as e:
        # Captura erro de FK constraint (registros vinculados)
        logger.error(f"Erro ao excluir Curtida {id_usuario}, {id_anuncio}: {str(e)}")
        informar_erro(request, "Não é possível excluir este registro pois existem dados vinculados a ele.")

    return RedirectResponse("/admin/curtidas/listar", status_code=status.HTTP_303_SEE_OTHER)