from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.logger_config import logger
from util.exceptions import FormValidationError

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
    assert usuario_logado is not None
    dados_formulario = {"nome": nome, "descricao": descricao}

    try:
        dto = CriarCategoriaDTO(nome=nome, descricao=descricao)
        categoria = Categoria(id=0, nome=dto.nome, descricao=dto.descricao)
        categoria_repo.inserir(categoria)

        logger.info(f"Categoria '{dto.nome}' criada por admin {usuario_logado['id']}")
        informar_sucesso(request, "Categoria cadastrada com sucesso!")
        return RedirectResponse("/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="categorias/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )

    except Exception as e:
        # Captura erro de UNIQUE constraint (categoria duplicada)
        erro_msg = str(e)
        if "UNIQUE constraint failed" in erro_msg or "nome" in erro_msg.lower():
            logger.warning(f"Tentativa de criar categoria duplicada '{nome}' por admin {usuario_logado['id']}")
            informar_erro(request, f"Já existe uma categoria com o nome '{nome}'.")
        else:
            logger.error(f"Erro ao criar categoria por admin {usuario_logado['id']}: {erro_msg}")
            informar_erro(request, "Erro ao cadastrar categoria.")

        return templates.TemplateResponse(
            "categorias/cadastro.html",
            {"request": request, "dados": dados_formulario}
        )