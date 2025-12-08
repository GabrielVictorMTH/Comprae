from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from repo import pedido_repo, anuncio_repo, endereco_repo, usuario_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/pedidos")
templates = criar_templates()

# Rate limiter para operações admin
admin_pedidos_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_pedidos",
)

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de pedidos"""
    return RedirectResponse("/admin/pedidos/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, status_filtro: Optional[str] = None, usuario_logado: Optional[dict] = None):
    """Lista todos os pedidos do sistema com filtro opcional por status"""
    if status_filtro and status_filtro != "todos":
        pedidos = pedido_repo.obter_por_status(status_filtro)
    else:
        pedidos = pedido_repo.obter_todos()

    # Carregar dados relacionados para exibição
    for pedido in pedidos:
        pedido.anuncio = anuncio_repo.obter_por_id(pedido.id_anuncio)
        pedido.comprador = usuario_repo.obter_por_id(pedido.id_comprador)
        pedido.endereco = endereco_repo.obter_por_id(pedido.id_endereco)

    return templates.TemplateResponse(
        "admin/pedidos/listar.html",
        {
            "request": request,
            "pedidos": pedidos,
            "status_filtro": status_filtro or "todos"
        }
    )

@router.get("/detalhes/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def detalhes(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes completos de um pedido"""
    pedido = pedido_repo.obter_por_id(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado")
        return RedirectResponse("/admin/pedidos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Carregar dados relacionados
    pedido.anuncio = anuncio_repo.obter_por_id(pedido.id_anuncio)
    pedido.comprador = usuario_repo.obter_por_id(pedido.id_comprador)
    pedido.endereco = endereco_repo.obter_por_id(pedido.id_endereco)

    if pedido.anuncio:
        pedido.anuncio.vendedor = usuario_repo.obter_por_id(pedido.anuncio.id_vendedor)

    return templates.TemplateResponse(
        "admin/pedidos/detalhes.html",
        {
            "request": request,
            "pedido": pedido
        }
    )

@router.post("/cancelar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def cancelar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Cancela um pedido (admin override)"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_pedidos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/pedidos/listar", status_code=status.HTTP_303_SEE_OTHER)

    pedido = pedido_repo.obter_por_id(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado")
        return RedirectResponse("/admin/pedidos/listar", status_code=status.HTTP_303_SEE_OTHER)

    if pedido.status == "Cancelado":
        informar_erro(request, "Pedido já está cancelado")
        return RedirectResponse(f"/admin/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

    try:
        pedido_repo.cancelar(id)
        logger.info(f"Pedido {id} cancelado por admin {usuario_logado['id']} (admin override)")
        informar_sucesso(request, "Pedido cancelado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao cancelar pedido {id}: {str(e)}")
        informar_erro(request, "Erro ao cancelar pedido. Tente novamente.")

    return RedirectResponse(f"/admin/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/estatisticas")
@requer_autenticacao([Perfil.ADMIN.value])
async def estatisticas(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe estatísticas gerais sobre pedidos"""
    todos = pedido_repo.obter_todos()

    stats = {
        "total": len(todos),
        "pendentes": len([p for p in todos if p.status == "Pendente"]),
        "pagos": len([p for p in todos if p.status == "Pago"]),
        "enviados": len([p for p in todos if p.status == "Enviado"]),
        "cancelados": len([p for p in todos if p.status == "Cancelado"]),
        "valor_total": sum(p.preco for p in todos if p.status != "Cancelado"),
    }

    return templates.TemplateResponse(
        "admin/pedidos/estatisticas.html",
        {
            "request": request,
            "stats": stats
        }
    )
