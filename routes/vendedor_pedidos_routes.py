# =============================================================================
# Imports
# =============================================================================

# Standard library
from typing import Optional

# Third-party
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import pedido_repo, anuncio_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.status_pedido import StatusPedido
from util.template_util import criar_templates

# =============================================================================
# Configuracao do Router - Rotas do Vendedor
# =============================================================================

router = APIRouter(prefix="/vendedor/pedidos", tags=["Pedidos do Vendedor"])
templates_pedido = criar_templates()


# =============================================================================
# Rotas do Vendedor
# =============================================================================

@router.get("")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def listar_pedidos_vendedor(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista os pedidos recebidos pelo vendedor"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedidos = pedido_repo.obter_por_vendedor_com_detalhes(usuario_logado.id)

    return templates_pedido.TemplateResponse(
        "pedidos/listar_vendedor.html",
        {
            "request": request,
            "pedidos": pedidos,
            "usuario_logado": usuario_logado,
        },
    )


@router.get("/definir-preco/{id}")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def get_definir_preco(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Formulario para definir preco final do pedido"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedido = pedido_repo.obter_por_id_com_detalhes(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado.")
        return RedirectResponse(url="/vendedor/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se é o vendedor do anúncio
    if not hasattr(pedido, 'id_vendedor') or pedido.id_vendedor != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para definir preco deste pedido.")
        return RedirectResponse(url="/vendedor/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se o status permite definição de preço
    if pedido.status != StatusPedido.NEGOCIANDO.value:
        informar_erro(request, "O preço só pode ser definido quando o pedido está em negociação.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

    # Buscar anuncio para preco sugerido
    anuncio = anuncio_repo.obter_por_id(pedido.id_anuncio)

    return templates_pedido.TemplateResponse(
        "pedidos/definir_preco.html",
        {
            "request": request,
            "pedido": pedido,
            "anuncio": anuncio,
            "usuario_logado": usuario_logado,
        },
    )


@router.post("/definir-preco/{id}")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def post_definir_preco(
    request: Request,
    id: int,
    preco: float = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Define o preço final e muda status para Pendente"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedido = pedido_repo.obter_por_id_com_detalhes(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado.")
        return RedirectResponse(url="/vendedor/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se é o vendedor do anúncio
    if not hasattr(pedido, 'id_vendedor') or pedido.id_vendedor != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para definir preço deste pedido.")
        return RedirectResponse(url="/vendedor/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se o status permite definição de preço
    if pedido.status != StatusPedido.NEGOCIANDO.value:
        informar_erro(request, "O preço só pode ser definido quando o pedido está em negociação.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

    # Validar preço
    if preco <= 0:
        informar_erro(request, "O preço deve ser maior que zero.")
        return RedirectResponse(url=f"/vendedor/pedidos/definir-preco/{id}", status_code=status.HTTP_303_SEE_OTHER)

    if pedido_repo.definir_preco_final(id, preco):
        logger.info(f"Preço definido para pedido ID: {id} - Vendedor: {usuario_logado.id} - Preço: {preco}")
        informar_sucesso(request, f"Preço definido! Aguardando pagamento do comprador.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        informar_erro(request, "Erro ao definir preço.")
        return RedirectResponse(url=f"/vendedor/pedidos/definir-preco/{id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/enviar/{id}")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def get_enviar_pedido(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Formulario para informar envio do pedido"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedido = pedido_repo.obter_por_id_com_detalhes(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado.")
        return RedirectResponse(url="/vendedor/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se é o vendedor do anúncio
    if not hasattr(pedido, 'id_vendedor') or pedido.id_vendedor != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para enviar este pedido.")
        return RedirectResponse(url="/vendedor/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se o status permite envio
    if pedido.status != StatusPedido.PAGO.value:
        informar_erro(request, "O pedido só pode ser enviado após o pagamento.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

    return templates_pedido.TemplateResponse(
        "pedidos/enviar.html",
        {
            "request": request,
            "pedido": pedido,
            "usuario_logado": usuario_logado,
        },
    )


@router.post("/enviar/{id}")
@requer_autenticacao(perfis_permitidos=[Perfil.VENDEDOR.value])
async def post_enviar_pedido(
    request: Request,
    id: int,
    codigo_rastreio: str = Form(""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Marca pedido como enviado"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedido = pedido_repo.obter_por_id_com_detalhes(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado.")
        return RedirectResponse(url="/vendedor/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se é o vendedor do anúncio
    if not hasattr(pedido, 'id_vendedor') or pedido.id_vendedor != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para enviar este pedido.")
        return RedirectResponse(url="/vendedor/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se o status permite envio
    if pedido.status != StatusPedido.PAGO.value:
        informar_erro(request, "O pedido só pode ser enviado após o pagamento.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

    if pedido_repo.marcar_como_enviado(id, codigo_rastreio or ""):
        logger.info(f"Pedido enviado ID: {id} - Vendedor: {usuario_logado.id} - Rastreio: {codigo_rastreio}")
        informar_sucesso(request, "Pedido marcado como enviado!")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        informar_erro(request, "Erro ao marcar pedido como enviado.")
        return RedirectResponse(url=f"/vendedor/pedidos/enviar/{id}", status_code=status.HTTP_303_SEE_OTHER)
