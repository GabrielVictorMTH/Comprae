from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.pedido_dto import CriarPedidoDTO, AvaliarPedidoDTO
from model.pedido_model import Pedido
from repo import pedido_repo, anuncio_repo, endereco_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.exceptions import FormValidationError

router = APIRouter(prefix="/pedidos")
templates = criar_templates("templates/pedidos")

# ROTAS DO COMPRADOR
# GET /pedidos/meus → lista pedidos do comprador
# GET /pedidos/detalhes/{id} → detalhes de um pedido
# POST /pedidos/criar → cria novo pedido (diminui estoque)
# POST /pedidos/pagar/{id} → marca como pago
# POST /pedidos/cancelar/{id} → cancela pedido (restaura estoque)
# POST /pedidos/avaliar/{id} → avalia pedido

# ROTAS DO VENDEDOR
# GET /pedidos/vendas → lista vendas (obter_por_vendedor)
# POST /pedidos/enviar/{id} → marca como enviado + rastreio