from fastapi import APIRouter, Request
from util.template_util import criar_templates
from util.auth_decorator import obter_usuario_logado

router = APIRouter()
templates_public = criar_templates("templates")


@router.get("/")
async def home(request: Request):
    """
    Rota inicial - Landing Page pública (sempre)
    """
    return templates_public.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.get("/index")
async def index(request: Request):
    """
    Página pública inicial (Landing Page)
    Sempre exibe a página pública, independentemente de autenticação
    """
    return templates_public.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.get("/sobre")
async def sobre(request: Request):
    """
    Página "Sobre" com informações do projeto acadêmico
    """
    return templates_public.TemplateResponse(
        "sobre.html",
        {"request": request}
    )