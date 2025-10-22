from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.endereco_dto import CriarEnderecoDTO, AlterarEnderecoDTO
from model.endereco_model import Endereco
from repo import endereco_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.exceptions import FormValidationError

router = APIRouter(prefix="/enderecos")
templates = criar_templates("templates/enderecos")

# GET /enderecos/ → redireciona para /listar
# GET /enderecos/listar → lista endereços do usuário logado
# GET /enderecos/cadastrar → formulário de cadastro
# POST /enderecos/cadastrar → processa cadastro
# GET /enderecos/editar/{id} → formulário de edição
# POST /enderecos/editar/{id} → processa edição
# POST /enderecos/excluir/{id} → exclui endereço