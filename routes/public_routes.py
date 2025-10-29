from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.template_util import criar_templates
from util.auth_decorator import obter_usuario_logado
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.flash_messages import informar_erro
from util.logger_config import logger
from util.config import (
    RATE_LIMIT_PUBLIC_MAX,
    RATE_LIMIT_PUBLIC_MINUTOS,
)

router = APIRouter()
templates_public = criar_templates("templates")

# Rate limiter para páginas públicas (proteção contra DDoS)
public_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_PUBLIC_MAX,
    janela_minutos=RATE_LIMIT_PUBLIC_MINUTOS,
    nome="public_pages",
)


@router.get("/")
async def home(request: Request):
    """
    Rota inicial - Landing Page pública (sempre)
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, f"Muitas requisições. Aguarde {RATE_LIMIT_PUBLIC_MINUTOS} minuto(s).")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

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
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, f"Muitas requisições. Aguarde {RATE_LIMIT_PUBLIC_MINUTOS} minuto(s).")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    return templates_public.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.get("/sobre")
async def sobre(request: Request):
    """
    Página "Sobre" com informações do projeto acadêmico
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, f"Muitas requisições. Aguarde {RATE_LIMIT_PUBLIC_MINUTOS} minuto(s).")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    return templates_public.TemplateResponse(
        "sobre.html",
        {"request": request}
    )