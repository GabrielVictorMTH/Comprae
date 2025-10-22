from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.exceptions import FormValidationError

router = APIRouter(prefix="/admin/categorias")
templates = criar_templates("templates/admin/categorias")

# GET /admin/categorias/ → redireciona para /listar
# GET /admin/categorias/listar → lista todas categorias
# GET /admin/categorias/cadastrar → formulário de cadastro
# POST /admin/categorias/cadastrar → processa cadastro
# GET /admin/categorias/editar/{id} → formulário de edição
# POST /admin/categorias/editar/{id} → processa edição
# POST /admin/categorias/excluir/{id} → exclui categoria