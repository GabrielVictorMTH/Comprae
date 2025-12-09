from fastapi import APIRouter, Request, status

from repo import anuncio_repo
from util.template_util import criar_templates
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.flash_messages import informar_erro
from util.logger_config import logger

router = APIRouter()
templates_public = criar_templates()

# Rate limiter para páginas públicas (proteção contra DDoS)
public_limiter = DynamicRateLimiter(
    chave_max="rate_limit_public_max",
    chave_minutos="rate_limit_public_minutos",
    padrao_max=100,
    padrao_minutos=1,
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
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Obter ultimos anuncios para exibir na home
    ultimos_anuncios = anuncio_repo.obter_ultimos_ativos(limite=12)

    return templates_public.TemplateResponse(
        "index.html",
        {"request": request, "ultimos_anuncios": ultimos_anuncios}
    )


@router.get("/index")
async def index(request: Request):
    """
    Pagina publica inicial (Landing Page)
    Sempre exibe a pagina publica, independentemente de autenticacao
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisicoes. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para pagina publica - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Obter ultimos anuncios para exibir na home
    ultimos_anuncios = anuncio_repo.obter_ultimos_ativos(limite=12)

    return templates_public.TemplateResponse(
        "index.html",
        {"request": request, "ultimos_anuncios": ultimos_anuncios}
    )


@router.get("/sobre")
async def sobre(request: Request):
    """
    Página "Sobre" com informações do projeto acadêmico
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    return templates_public.TemplateResponse("sobre.html", {"request": request})
