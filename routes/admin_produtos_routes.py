from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.anuncio_dto import AlterarAnuncioDTO, ModerarProdutoDTO
from model.anuncio_model import Anuncio
from repo import anuncio_repo, categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/produtos")
templates = criar_templates("templates/admin/produtos")

# Rate limiter para operações admin
admin_produtos_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_produtos",
)

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de produtos"""
    return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os produtos do sistema"""
    # Obter todos os anúncios (ativos e inativos)
    anuncios = anuncio_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/produtos/listar.html",
        {"request": request, "anuncios": anuncios}
    )

@router.get("/moderar")
@requer_autenticacao([Perfil.ADMIN.value])
async def moderar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista produtos pendentes de moderação ou inativos"""
    # Obter todos os produtos inativos (pendentes de aprovação)
    anuncios = anuncio_repo.obter_todos()
    anuncios_pendentes = [a for a in anuncios if not a.ativo]

    return templates.TemplateResponse(
        "admin/produtos/moderar.html",
        {"request": request, "anuncios": anuncios_pendentes}
    )

@router.post("/aprovar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def aprovar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Aprova um produto (torna ativo)"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_produtos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    # Ativar produto
    anuncio.ativo = True
    anuncio_repo.alterar(anuncio)

    logger.info(f"Produto {id} ({anuncio.nome}) aprovado por admin {usuario_logado['id']}")
    informar_sucesso(request, f"Produto '{anuncio.nome}' aprovado com sucesso!")

    return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/reprovar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def reprovar(
    request: Request,
    id: int,
    motivo_reprovacao: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Reprova um produto com motivo"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_produtos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Validar motivo
        dto = ModerarProdutoDTO(
            id=id,
            motivo_reprovacao=motivo_reprovacao
        )

        # Manter produto inativo e registrar motivo no log
        logger.warning(
            f"Produto {id} ({anuncio.nome}) reprovado por admin {usuario_logado['id']}. "
            f"Motivo: {dto.motivo_reprovacao}"
        )

        # TODO: Em versão futura, enviar notificação ao vendedor com o motivo

        informar_sucesso(request, f"Produto '{anuncio.nome}' reprovado.")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        informar_erro(request, "Motivo de reprovação inválido (mínimo 10 caracteres)")
        return RedirectResponse("/admin/produtos/moderar", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de edição de produto (admin)"""
    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter categorias para o select
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/produtos/editar.html",
        {
            "request": request,
            "anuncio": anuncio,
            "categorias": categorias,
            "dados": anuncio.__dict__
        }
    )

@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    id_categoria: int = Form(...),
    nome: str = Form(...),
    descricao: str = Form(...),
    peso: float = Form(...),
    preco: float = Form(...),
    estoque: int = Form(...),
    ativo: Optional[str] = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Edita um produto (admin)"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_produtos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se anúncio existe
    anuncio_atual = anuncio_repo.obter_por_id(id)
    if not anuncio_atual:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Converter checkbox ativo
    ativo_bool = ativo == "true" if ativo else False

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "id": id,
        "id_categoria": id_categoria,
        "nome": nome,
        "descricao": descricao,
        "peso": peso,
        "preco": preco,
        "estoque": estoque,
        "ativo": ativo_bool
    }

    try:
        # Validar com DTO
        dto = AlterarAnuncioDTO(
            id=id,
            id_categoria=id_categoria,
            nome=nome,
            descricao=descricao,
            peso=peso,
            preco=preco,
            estoque=estoque,
            ativo=ativo_bool
        )

        # Atualizar anúncio
        anuncio_atualizado = Anuncio(
            id=id,
            id_vendedor=anuncio_atual.id_vendedor,  # Mantém vendedor original
            id_categoria=dto.id_categoria,
            nome=dto.nome,
            descricao=dto.descricao,
            peso=dto.peso,
            preco=dto.preco,
            estoque=dto.estoque,
            ativo=dto.ativo,
            data_cadastro=anuncio_atual.data_cadastro  # Mantém data original
        )

        anuncio_repo.alterar(anuncio_atualizado)
        logger.info(f"Produto {id} editado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Produto alterado com sucesso!")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Adicionar dados necessários para renderizar o template
        dados_formulario["anuncio"] = anuncio_repo.obter_por_id(id)
        dados_formulario["categorias"] = categoria_repo.obter_todos()
        raise FormValidationError(
            validation_error=e,
            template_path="admin/produtos/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )

@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui um produto"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_produtos_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    anuncio = anuncio_repo.obter_por_id(id)

    if not anuncio:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        anuncio_repo.excluir(id)
        logger.info(f"Produto {id} ({anuncio.nome}) excluído por admin {usuario_logado['id']}")
        informar_sucesso(request, "Produto excluído com sucesso!")
    except Exception as e:
        # Captura erro de FK constraint (produto com pedidos vinculados)
        logger.error(f"Erro ao excluir produto {id}: {str(e)}")
        informar_erro(request, "Não é possível excluir este produto pois existem pedidos vinculados a ele.")

    return RedirectResponse("/admin/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)
