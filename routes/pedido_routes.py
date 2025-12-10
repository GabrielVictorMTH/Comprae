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
from repo import pedido_repo, anuncio_repo, endereco_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.status_pedido import StatusPedido
from util.template_util import criar_templates

# =============================================================================
# Configuracao do Router - Rotas do Comprador
# =============================================================================

router = APIRouter(prefix="/pedidos", tags=["Pedidos do Comprador"])
templates_pedido = criar_templates()


# =============================================================================
# Rotas do Comprador
# =============================================================================

@router.get("")
@requer_autenticacao()
async def listar_pedidos_comprador(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista os pedidos do comprador logado"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedidos = pedido_repo.obter_por_comprador_com_detalhes(usuario_logado.id)

    return templates_pedido.TemplateResponse(
        "pedidos/listar_comprador.html",
        {
            "request": request,
            "pedidos": pedidos,
            "usuario_logado": usuario_logado,
        },
    )


@router.get("/detalhes/{id}")
@requer_autenticacao()
async def detalhes_pedido(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe detalhes de um pedido"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedido = pedido_repo.obter_por_id_com_detalhes(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado.")
        return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se o usuario tem permissao (comprador ou vendedor do anuncio)
    is_comprador = pedido.id_comprador == usuario_logado.id
    is_vendedor = hasattr(pedido, 'id_vendedor') and pedido.id_vendedor == usuario_logado.id

    if not is_comprador and not is_vendedor:
        informar_erro(request, "Você não tem permissão para ver este pedido.")
        return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    return templates_pedido.TemplateResponse(
        "pedidos/detalhes.html",
        {
            "request": request,
            "pedido": pedido,
            "usuario_logado": usuario_logado,
            "is_comprador": is_comprador,
            "is_vendedor": is_vendedor,
            "pode_cancelar": StatusPedido.pode_cancelar(pedido.status),
        },
    )


@router.get("/criar")
@requer_autenticacao()
async def get_criar_pedido(
    request: Request,
    anuncio: int,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """Formulario para criar pedido (iniciar negociacao)"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Buscar anuncio
    anuncio_obj = anuncio_repo.obter_por_id_com_detalhes(anuncio)
    if not anuncio_obj:
        informar_erro(request, "Anúncio não encontrado.")
        return RedirectResponse(url="/anuncios", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se não é o próprio vendedor
    if anuncio_obj.id_vendedor == usuario_logado.id:
        informar_erro(request, "Você não pode comprar seu próprio anúncio.")
        return RedirectResponse(url=f"/anuncios/{anuncio}", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se anúncio está disponível
    if not anuncio_obj.ativo or anuncio_obj.estoque <= 0:
        informar_erro(request, "Este anúncio não está mais disponível.")
        return RedirectResponse(url="/anuncios", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se usuario tem endereco
    endereco = endereco_repo.obter_endereco_usuario(usuario_logado.id)
    if not endereco:
        informar_erro(request, "Você precisa cadastrar um endereço antes de fazer um pedido.")
        return RedirectResponse(url="/usuario/endereco/cadastrar", status_code=status.HTTP_303_SEE_OTHER)

    return templates_pedido.TemplateResponse(
        "pedidos/criar.html",
        {
            "request": request,
            "anuncio": anuncio_obj,
            "endereco": endereco,
            "usuario_logado": usuario_logado,
        },
    )


@router.post("/criar")
@requer_autenticacao()
async def post_criar_pedido(
    request: Request,
    id_anuncio: int = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Cria um novo pedido (status Negociando)"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Buscar anuncio
    anuncio = anuncio_repo.obter_por_id(id_anuncio)
    if not anuncio:
        informar_erro(request, "Anúncio não encontrado.")
        return RedirectResponse(url="/anuncios", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se nao e o proprio vendedor
    if anuncio.id_vendedor == usuario_logado.id:
        informar_erro(request, "Você não pode comprar seu próprio anúncio.")
        return RedirectResponse(url=f"/anuncios/{id_anuncio}", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se usuario tem endereco
    endereco = endereco_repo.obter_endereco_usuario(usuario_logado.id)
    if not endereco:
        informar_erro(request, "Você precisa cadastrar um endereço antes de fazer um pedido.")
        return RedirectResponse(url="/usuario/endereco/cadastrar", status_code=status.HTTP_303_SEE_OTHER)

    # Criar pedido com status Negociando
    pedido_id = pedido_repo.inserir_negociando(
        id_endereco=endereco.id,
        id_comprador=usuario_logado.id,
        id_anuncio=id_anuncio
    )

    if pedido_id:
        logger.info(f"Pedido criado ID: {pedido_id} - Comprador: {usuario_logado.id} - Anúncio: {id_anuncio}")
        informar_sucesso(request, "Pedido criado! Aguarde o vendedor definir o preço final.")
        return RedirectResponse(url=f"/pedidos/detalhes/{pedido_id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        informar_erro(request, "Erro ao criar pedido. Tente novamente.")
        return RedirectResponse(url=f"/anuncios/{id_anuncio}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/pagar/{id}")
@requer_autenticacao()
async def post_pagar_pedido(
    request: Request,
    id: int,
    csrf_token: str = Form(default=""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Simula pagamento do pedido"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedido = pedido_repo.obter_por_id(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado.")
        return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se é o comprador
    if pedido.id_comprador != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para pagar este pedido.")
        return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se o status permite pagamento
    if pedido.status != StatusPedido.PENDENTE.value:
        informar_erro(request, "Este pedido não pode ser pago no status atual.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

    if pedido_repo.marcar_como_pago(id):
        logger.info(f"Pedido pago ID: {id} - Comprador: {usuario_logado.id}")
        informar_sucesso(request, "Pagamento realizado com sucesso! Aguarde o envio.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        informar_erro(request, "Erro ao processar pagamento.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/cancelar/{id}")
@requer_autenticacao()
async def post_cancelar_pedido(
    request: Request,
    id: int,
    csrf_token: str = Form(default=""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Cancela um pedido (se permitido pelo status)"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedido = pedido_repo.obter_por_id_com_detalhes(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado.")
        return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se usuário tem permissão (comprador ou vendedor)
    is_comprador = pedido.id_comprador == usuario_logado.id
    is_vendedor = hasattr(pedido, 'id_vendedor') and pedido.id_vendedor == usuario_logado.id

    if not is_comprador and not is_vendedor:
        informar_erro(request, "Você não tem permissão para cancelar este pedido.")
        return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se pode cancelar
    if not StatusPedido.pode_cancelar(pedido.status):
        informar_erro(request, "Este pedido não pode mais ser cancelado.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

    if pedido_repo.cancelar(id):
        logger.info(f"Pedido cancelado ID: {id} - Usuario: {usuario_logado.id}")
        informar_sucesso(request, "Pedido cancelado com sucesso.")
    else:
        informar_erro(request, "Erro ao cancelar pedido.")

    return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/confirmar-entrega/{id}")
@requer_autenticacao()
async def post_confirmar_entrega(
    request: Request,
    id: int,
    csrf_token: str = Form(default=""),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Confirma recebimento do pedido (comprador)"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    pedido = pedido_repo.obter_por_id(id)

    if not pedido:
        informar_erro(request, "Pedido não encontrado.")
        return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se é o comprador
    if pedido.id_comprador != usuario_logado.id:
        informar_erro(request, "Você não tem permissão para confirmar este pedido.")
        return RedirectResponse(url="/pedidos", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se o status permite confirmação
    if pedido.status != StatusPedido.ENVIADO.value:
        informar_erro(request, "Este pedido ainda não foi enviado.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)

    if pedido_repo.marcar_como_entregue(id):
        logger.info(f"Pedido entregue ID: {id} - Comprador: {usuario_logado.id}")
        informar_sucesso(request, "Entrega confirmada com sucesso!")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        informar_erro(request, "Erro ao confirmar entrega.")
        return RedirectResponse(url=f"/pedidos/detalhes/{id}", status_code=status.HTTP_303_SEE_OTHER)
