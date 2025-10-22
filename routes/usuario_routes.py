from typing import Optional
from fastapi import APIRouter, Request
from util.template_util import criar_templates
from util.auth_decorator import requer_autenticacao

router = APIRouter()
templates_usuario = criar_templates("templates")


@router.get("/usuario")
@requer_autenticacao()
async def dashboard(request: Request, usuario_logado: Optional[dict] = None):
    """
    Dashboard do usuário (área privada)
    Requer autenticação
    """
    assert usuario_logado is not None
    return templates_usuario.TemplateResponse(
        "home.html",
        {
            "request": request,
            "usuario": usuario_logado
        }
    )
