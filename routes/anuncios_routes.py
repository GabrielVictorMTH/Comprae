from typing import Optional
from fastapi import APIRouter, Form, Request, Query, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.anuncio_dto import CriarAnuncioDTO, AlterarAnuncioDTO
from model.anuncio_model import Anuncio
from repo import anuncio_repo, categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.perfis import Perfil
from util.exceptions import FormValidationError

router = APIRouter(prefix="/anuncios")
templates = criar_templates("templates/anuncios")

# ROTAS PÚBLICAS (ou autenticadas para compra)
# GET /anuncios/ → vitrine de produtos (buscar_com_filtros)
# GET /anuncios/detalhes/{id} → detalhes de um produto

# ROTAS DO VENDEDOR
# GET /anuncios/meus → lista anúncios do vendedor logado
# GET /anuncios/cadastrar → formulário de cadastro (select de categorias)
# POST /anuncios/cadastrar → processa cadastro
# GET /anuncios/editar/{id} → formulário de edição
# POST /anuncios/editar/{id} → processa edição
# POST /anuncios/excluir/{id} → exclui anúncio
# POST /anuncios/ativar/{id} → ativa/desativa anúncio