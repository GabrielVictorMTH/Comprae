from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.mensagem_dto import EnviarMensagemDTO
from model.mensagem_model import Mensagem
from repo import mensagem_repo, usuario_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.exceptions import FormValidationError

router = APIRouter(prefix="/mensagens")
templates = criar_templates("templates/mensagens")

# GET /mensagens/ → redireciona para /caixa-entrada
# GET /mensagens/caixa-entrada → lista mensagens recebidas
# GET /mensagens/conversa/{id_outro_usuario} → exibe conversa com outro usuário
# POST /mensagens/enviar → envia mensagem
# POST /mensagens/marcar-lida/{id} → marca mensagem como lida