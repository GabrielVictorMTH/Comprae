"""
Rotas para pagina de favoritos do usuario
"""

from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from model.usuario_logado_model import UsuarioLogado
from repo import curtida_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates

router = APIRouter(prefix="/favoritos", tags=["Favoritos"])
templates = criar_templates()


@router.get("")
@requer_autenticacao()
async def listar_favoritos(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """Lista todos os anuncios curtidos pelo usuario"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Buscar anuncios curtidos
    favoritos = curtida_repo.obter_por_usuario(usuario_logado.id)
    total = curtida_repo.contar_por_usuario(usuario_logado.id)

    return templates.TemplateResponse(
        "favoritos/listar.html",
        {
            "request": request,
            "favoritos": favoritos,
            "total": total,
            "usuario_logado": usuario_logado,
        },
    )