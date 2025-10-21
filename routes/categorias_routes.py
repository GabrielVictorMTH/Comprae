from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil

router = APIRouter(prefix="/categorias")
templates = criar_templates("templates/categorias")

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value, Perfil.VENDEDOR.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    categorias = categoria_repo.obter_todos()
    return templates.TemplateResponse(
        "categorias/listar.html",
        {"request": request, "categorias": categorias}
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    return templates.TemplateResponse(
        "categorias/cadastro.html",
        {"request": request}
    )

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    try:
        dto = CriarCategoriaDTO(nome=nome, descricao=descricao)
        categoria = Categoria(id=0, nome=dto.nome, descricao=dto.descricao)
        categoria_repo.inserir(categoria)
        informar_sucesso(request, "Categoria cadastrada com sucesso!")
        return RedirectResponse("/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        informar_erro(request, str(e))
        return templates.TemplateResponse(
            "categorias/cadastro.html",
            {"request": request, "dados": {"nome": nome, "descricao": descricao}}
        )