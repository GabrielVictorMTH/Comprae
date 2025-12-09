from typing import Optional
from fastapi import APIRouter, Request, status, Query
from fastapi.responses import RedirectResponse

from repo import endereco_repo, usuario_repo, pedido_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/enderecos")
templates = criar_templates()

# Rate limiter para operações admin
admin_enderecos_limiter = RateLimiter(
    max_tentativas=20,
    janela_minutos=1,
    nome="admin_enderecos",
)


@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de endereços"""
    return RedirectResponse(
        "/admin/enderecos/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    uf_filtro: Optional[str] = Query(None),
    usuario_logado: Optional[dict] = None,
):
    """Lista todos os endereços do sistema com filtros opcionais"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_enderecos_limiter.verificar(ip):
        return templates.TemplateResponse(
            "admin/enderecos/listar.html",
            {
                "request": request,
                "enderecos": [],
                "erro": "Muitas requisições. Aguarde um momento.",
            },
        )

    try:
        # Buscar endereços
        if uf_filtro:
            enderecos = endereco_repo.obter_por_uf(uf_filtro)
            logger.info(
                f"Admin {usuario_logado['id']} listou endereços da UF {uf_filtro}"
            )
        else:
            enderecos = endereco_repo.obter_todos()
            logger.info(f"Admin {usuario_logado['id']} listou todos os endereços")

        # Carregar informações dos usuários
        enderecos_com_usuario = []
        for endereco in enderecos:
            usuario = usuario_repo.obter_por_id(endereco.id_usuario)
            enderecos_com_usuario.append({"endereco": endereco, "usuario": usuario})

        # Obter lista de UFs para o filtro
        ufs = sorted(set([e.uf for e in enderecos]))

        return templates.TemplateResponse(
            "admin/enderecos/listar.html",
            {
                "request": request,
                "enderecos": enderecos_com_usuario,
                "ufs": ufs,
                "uf_filtro": uf_filtro,
            },
        )

    except Exception as e:
        logger.error(f"Erro ao listar endereços: {e}", exc_info=True)
        return templates.TemplateResponse(
            "admin/enderecos/listar.html",
            {"request": request, "enderecos": [], "erro": "Erro ao carregar endereços"},
        )


@router.get("/detalhes/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def detalhes(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes completos de um endereço"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_enderecos_limiter.verificar(ip):
        return RedirectResponse(
            "/admin/enderecos/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Buscar endereço
        endereco = endereco_repo.obter_por_id(id)
        if not endereco:
            logger.warning(f"Endereço {id} não encontrado")
            return RedirectResponse(
                "/admin/enderecos/listar", status_code=status.HTTP_303_SEE_OTHER
            )

        # Buscar usuário
        usuario = usuario_repo.obter_por_id(endereco.id_usuario)

        # Buscar pedidos que usaram este endereço
        todos_pedidos = pedido_repo.obter_todos()
        pedidos_endereco = [p for p in todos_pedidos if p.id_endereco == id]

        logger.info(
            f"Admin {usuario_logado['id']} visualizou detalhes do endereço {id}"
        )

        return templates.TemplateResponse(
            "admin/enderecos/detalhes.html",
            {
                "request": request,
                "endereco": endereco,
                "usuario": usuario,
                "pedidos": pedidos_endereco,
            },
        )

    except Exception as e:
        logger.error(f"Erro ao exibir detalhes do endereço {id}: {e}", exc_info=True)
        return RedirectResponse(
            "/admin/enderecos/listar", status_code=status.HTTP_303_SEE_OTHER
        )


@router.get("/estatisticas")
@requer_autenticacao([Perfil.ADMIN.value])
async def estatisticas(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe estatísticas de endereços"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_enderecos_limiter.verificar(ip):
        return RedirectResponse(
            "/admin/enderecos/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Buscar estatísticas
        stats = endereco_repo.obter_estatisticas()
        por_uf = endereco_repo.contar_por_uf()
        por_cidade = endereco_repo.contar_por_cidade()

        logger.info(
            f"Admin {usuario_logado['id']} visualizou estatísticas de endereços"
        )

        return templates.TemplateResponse(
            "admin/enderecos/estatisticas.html",
            {
                "request": request,
                "stats": stats,
                "por_uf": por_uf,
                "por_cidade": por_cidade,
            },
        )

    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas de endereços: {e}", exc_info=True)
        return RedirectResponse(
            "/admin/enderecos/listar", status_code=status.HTTP_303_SEE_OTHER
        )


@router.get("/duplicados")
@requer_autenticacao([Perfil.ADMIN.value])
async def duplicados(request: Request, usuario_logado: Optional[dict] = None):
    """Lista endereços potencialmente duplicados para detecção de fraude"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_enderecos_limiter.verificar(ip):
        return RedirectResponse(
            "/admin/enderecos/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Buscar endereços duplicados
        duplicados_list = endereco_repo.obter_duplicados()

        logger.info(
            f"Admin {usuario_logado['id']} visualizou detecção de endereços duplicados"
        )

        return templates.TemplateResponse(
            "admin/enderecos/duplicados.html",
            {
                "request": request,
                "duplicados": duplicados_list,
                "total_grupos": len(duplicados_list),
            },
        )

    except Exception as e:
        logger.error(f"Erro ao detectar endereços duplicados: {e}", exc_info=True)
        return RedirectResponse(
            "/admin/enderecos/listar", status_code=status.HTTP_303_SEE_OTHER
        )
