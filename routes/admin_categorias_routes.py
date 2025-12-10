from typing import Optional
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.exceptions import ErroValidacaoFormulario
from util.perfis import Perfil
from util.template_util import criar_templates

# Configura o roteador com prefixo /admin/categorias
router = APIRouter(prefix="/admin/categorias")

# Configura os templates HTML com as funções globais necessárias (csrf_input, etc.)
templates = criar_templates()

# Rate Limiter: máximo 10 operações por minuto
admin_categorias_limiter = RateLimiter(
    max_tentativas=10, janela_minutos=1, nome="admin_categorias"
)


@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona a raiz para /listar"""
    return RedirectResponse(
        url="/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """
    Lista todas as categorias.
    """
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/categorias/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categorias": categorias,
        },
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    return templates.TemplateResponse(
        "admin/categorias/cadastro.html",
        {"request": request, "usuario_logado": usuario_logado},
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    usuario_logado: Optional[dict] = None,
    nome: str = Form(""),
    descricao: str = Form(""),
):
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url="/admin/categorias/cadastrar", status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        dto = CriarCategoriaDTO(nome=nome, descricao=descricao)

        categoria_existente = categoria_repo.obter_por_nome(dto.nome)
        if categoria_existente:
            informar_erro(request, "Já existe uma categoria com este nome.")
            return RedirectResponse(
                url="/admin/categorias/cadastrar", status_code=status.HTTP_303_SEE_OTHER
            )

        nova_categoria = Categoria(nome=dto.nome, descricao=dto.descricao)
        categoria_inserida = categoria_repo.inserir(nova_categoria)

        if categoria_inserida:
            informar_sucesso(request, "Categoria cadastrada com sucesso!")
            return RedirectResponse(
                url="/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao cadastrar categoria.")
            return RedirectResponse(
                url="/admin/categorias/cadastrar", status_code=status.HTTP_303_SEE_OTHER
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/categorias/cadastro.html",
            dados_formulario={"nome": nome, "descricao": descricao},
            campo_padrao="nome",
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    categoria = categoria_repo.obter_por_id(id)

    if not categoria:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        "admin/categorias/editar.html",
        {"request": request, "usuario_logado": usuario_logado, "categoria": categoria},
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[dict] = None,
    nome: str = Form(""),
    descricao: str = Form(""),
):
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url=f"/admin/categorias/editar/{id}", status_code=status.HTTP_303_SEE_OTHER
        )

    categoria_atual = categoria_repo.obter_por_id(id)
    if not categoria_atual:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        dto = AlterarCategoriaDTO(nome=nome, descricao=descricao)

        if dto.nome != categoria_atual.nome:
            categoria_existente = categoria_repo.obter_por_nome(dto.nome)
            if categoria_existente:
                informar_erro(request, "Já existe uma categoria com este nome.")
                return RedirectResponse(
                    url=f"/admin/categorias/editar/{id}",
                    status_code=status.HTTP_303_SEE_OTHER,
                )

        categoria_atual.nome = dto.nome
        categoria_atual.descricao = dto.descricao

        if categoria_repo.alterar(categoria_atual):
            informar_sucesso(request, "Categoria alterada com sucesso!")
            return RedirectResponse(
                url="/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao alterar categoria.")
            return RedirectResponse(
                url=f"/admin/categorias/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/categorias/editar.html",
            dados_formulario={"nome": nome, "descricao": descricao, "id": id},
            campo_padrao="nome",
        )


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(
    request: Request,
    id: int,
    csrf_token: str = Form(default=""),
    usuario_logado: Optional[dict] = None,
):
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url="/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    categoria = categoria_repo.obter_por_id(id)
    if not categoria:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    if categoria_repo.excluir(id):
        informar_sucesso(request, f"Categoria '{categoria.nome}' excluída com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir categoria.")

    return RedirectResponse(
        url="/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER
    )
