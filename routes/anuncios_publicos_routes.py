# =============================================================================
# Imports
# =============================================================================

# Standard library
from typing import Optional
import math

# Third-party
from fastapi import APIRouter, Request, Query

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import anuncio_repo, categoria_repo

# Utilities
from util.auth_decorator import obter_usuario_logado
from util.flash_messages import informar_erro
from util.template_util import criar_templates

# =============================================================================
# Configuracao do Router
# =============================================================================

router = APIRouter(prefix="/anuncios", tags=["Anuncios Publicos"])
templates_anuncios = criar_templates()

# Configuracoes de paginacao
ANUNCIOS_POR_PAGINA = 12


# =============================================================================
# Rotas
# =============================================================================

@router.get("")
async def listar_anuncios(
    request: Request,
    pagina: int = Query(1, ge=1, description="Numero da pagina"),
    busca: Optional[str] = Query(None, description="Termo de busca"),
    categoria: Optional[int] = Query(None, description="ID da categoria"),
):
    """Lista anuncios publicos com paginacao e filtros"""
    usuario_logado: Optional[UsuarioLogado] = obter_usuario_logado(request)

    # Buscar anuncios com filtros
    anuncios, total = anuncio_repo.obter_ativos_paginados(
        pagina=pagina,
        por_pagina=ANUNCIOS_POR_PAGINA,
        termo=busca,
        id_categoria=categoria
    )

    # Calcular paginacao
    total_paginas = math.ceil(total / ANUNCIOS_POR_PAGINA) if total > 0 else 1

    # Obter categorias para o filtro
    categorias = categoria_repo.obter_todos()

    return templates_anuncios.TemplateResponse(
        "anuncios/listar.html",
        {
            "request": request,
            "anuncios": anuncios,
            "categorias": categorias,
            "usuario_logado": usuario_logado,
            # Filtros atuais
            "busca": busca or "",
            "categoria_selecionada": categoria,
            # Paginacao
            "pagina_atual": pagina,
            "total_paginas": total_paginas,
            "total_anuncios": total,
        },
    )


@router.get("/{id}")
async def detalhes_anuncio(request: Request, id: int):
    """Exibe detalhes de um anuncio"""
    usuario_logado: Optional[UsuarioLogado] = obter_usuario_logado(request)

    # Buscar anuncio com detalhes
    # Buscar anuncio com detalhes
    anuncio = anuncio_repo.obter_por_id_com_detalhes(id)

    if not anuncio:
        informar_erro(request, "Anúncio não encontrado.")
        return templates_anuncios.TemplateResponse(
            "anuncios/listar.html",
            {
                "request": request,
                "anuncios": [],
                "categorias": categoria_repo.obter_todos(),
                "usuario_logado": usuario_logado,
                "busca": "",
                "categoria_selecionada": None,
                "pagina_atual": 1,
                "total_paginas": 1,
                "total_anuncios": 0,
            },
        )
         # Incrementar contador de visualizacoes
    anuncio_repo.incrementar_visualizacoes(id)

    # Verificar se anúncio está ativo e com estoque
    if not anuncio.ativo or anuncio.estoque <= 0:
        informar_erro(request, "Este anúncio não está mais disponível.")

    return templates_anuncios.TemplateResponse(
        "anuncios/detalhes.html",
        {
            "request": request,
            "anuncio": anuncio,
            "usuario_logado": usuario_logado,
        },
    )
