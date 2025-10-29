"""
Rotas para gerenciamento de chamados por usuários não-administradores.

Permite que usuários comuns:
- Listem seus próprios chamados
- Abram novos chamados
- Visualizem detalhes de chamados
- Excluam chamados próprios
"""

from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.chamado_dto import CriarChamadoDTO
from dtos.chamado_interacao_dto import CriarInteracaoDTO
from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from util.datetime_util import agora
from repo import chamado_repo, chamado_interacao_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.config import (
    RATE_LIMIT_CHAMADO_CRIAR_MAX,
    RATE_LIMIT_CHAMADO_CRIAR_MINUTOS,
    RATE_LIMIT_CHAMADO_RESPONDER_MAX,
    RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS,
)

router = APIRouter(prefix="/chamados")
templates = criar_templates("templates/chamados")

# Rate limiters
from util.rate_limiter import RateLimiter, obter_identificador_cliente

chamado_criar_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_CHAMADO_CRIAR_MAX,
    janela_minutos=RATE_LIMIT_CHAMADO_CRIAR_MINUTOS,
    nome="chamado_criar",
)
chamado_responder_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_CHAMADO_RESPONDER_MAX,
    janela_minutos=RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS,
    nome="chamado_responder",
)


@router.get("/listar")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os chamados do usuário logado."""
    assert usuario_logado is not None
    # Passa usuario_id para obter_por_usuario - a função já usa esse ID
    # para contar apenas mensagens de OUTROS usuários
    chamados = chamado_repo.obter_por_usuario(usuario_logado["id"])
    return templates.TemplateResponse(
        "chamados/listar.html",
        {"request": request, "chamados": chamados}
    )


@router.get("/cadastrar")
@requer_autenticacao()
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de abertura de chamado."""
    return templates.TemplateResponse(
        "chamados/cadastrar.html",
        {"request": request}
    )


@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar(
    request: Request,
    titulo: str = Form(),
    descricao: str = Form(),
    prioridade: str = Form(default="Média"),
    usuario_logado: Optional[dict] = None
):
    """Cadastra um novo chamado."""
    assert usuario_logado is not None

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not chamado_criar_limiter.verificar(ip):
        informar_erro(
            request,
            f"Muitas tentativas de criação de chamados. Aguarde {RATE_LIMIT_CHAMADO_CRIAR_MINUTOS} minuto(s).",
        )
        logger.warning(f"Rate limit excedido para criação de chamados - IP: {ip}")
        return templates.TemplateResponse(
            "chamados/cadastrar.html",
            {
                "request": request,
                "erros": {
                    "geral": f"Muitas tentativas de criação de chamados. Aguarde {RATE_LIMIT_CHAMADO_CRIAR_MINUTOS} minuto(s)."
                },
            },
        )

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": prioridade
    }

    try:
        # Validar com DTO
        dto = CriarChamadoDTO(
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade
        )

        # Criar chamado (sem descricao - será armazenada na interacao)
        chamado = Chamado(
            id=0,
            titulo=dto.titulo,
            prioridade=PrioridadeChamado(dto.prioridade),
            status=StatusChamado.ABERTO,
            usuario_id=usuario_logado["id"]
        )

        chamado_id = chamado_repo.inserir(chamado)

        # Criar interação inicial com a descrição do chamado
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_id,
            usuario_id=usuario_logado["id"],
            mensagem=dto.descricao,
            tipo=TipoInteracao.ABERTURA,
            data_interacao=agora(),
            status_resultante=StatusChamado.ABERTO.value
        )
        chamado_interacao_repo.inserir(interacao)

        logger.info(
            f"Chamado #{chamado_id} '{dto.titulo}' criado por usuário {usuario_logado['id']}"
        )

        informar_sucesso(request, "Chamado aberto com sucesso! Em breve responderemos.")
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="chamados/cadastrar.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
        )


@router.get("/{id}/visualizar")
@requer_autenticacao()
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes de um chamado específico com histórico de interações."""
    assert usuario_logado is not None
    chamado = chamado_repo.obter_por_id(id)

    # Verificar se chamado existe e pertence ao usuário
    if not chamado or chamado.usuario_id != usuario_logado["id"]:
        informar_erro(request, "Chamado não encontrado")
        logger.warning(
            f"Usuário {usuario_logado['id']} tentou acessar chamado {id} sem permissão"
        )
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Marcar mensagens como lidas (apenas as de outros usuários)
    chamado_interacao_repo.marcar_como_lidas(id, usuario_logado["id"])

    # Obter histórico de interações
    interacoes = chamado_interacao_repo.obter_por_chamado(id)

    return templates.TemplateResponse(
        "chamados/visualizar.html",
        {"request": request, "chamado": chamado, "interacoes": interacoes}
    )


@router.post("/{id}/responder")
@requer_autenticacao()
async def post_responder(
    request: Request,
    id: int,
    mensagem: str = Form(),
    usuario_logado: Optional[dict] = None
):
    """Permite que o usuário adicione uma resposta/mensagem ao seu próprio chamado."""
    assert usuario_logado is not None

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not chamado_responder_limiter.verificar(ip):
        informar_erro(
            request,
            f"Muitas tentativas de resposta em chamados. Aguarde {RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS} minuto(s).",
        )
        logger.warning(f"Rate limit excedido para resposta em chamados - IP: {ip}")
        return RedirectResponse(f"/chamados/{id}/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    chamado = chamado_repo.obter_por_id(id)

    # Verificar se chamado existe e pertence ao usuário
    if not chamado or chamado.usuario_id != usuario_logado["id"]:
        informar_erro(request, "Chamado não encontrado")
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    interacoes = chamado_interacao_repo.obter_por_chamado(id)
    dados_formulario: dict = {
        "mensagem": mensagem,
        "chamado": chamado,  # type: ignore[dict-item]
        "interacoes": interacoes  # type: ignore[dict-item]
    }

    try:
        # Validar com DTO
        dto = CriarInteracaoDTO(mensagem=mensagem)

        # Criar nova interação do usuário
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=id,
            usuario_id=usuario_logado["id"],
            mensagem=dto.mensagem,
            tipo=TipoInteracao.RESPOSTA_USUARIO,
            data_interacao=agora(),
            status_resultante=chamado.status.value  # Mantém status atual
        )
        chamado_interacao_repo.inserir(interacao)

        logger.info(
            f"Usuário {usuario_logado['id']} respondeu ao chamado {id}"
        )

        informar_sucesso(request, "Resposta adicionada com sucesso!")
        return RedirectResponse(f"/chamados/{id}/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="chamados/visualizar.html",
            dados_formulario=dados_formulario,
            campo_padrao="mensagem",
        )


@router.post("/{id}/excluir")
@requer_autenticacao()
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui um chamado do usuário (apenas se aberto e sem respostas de admin)."""
    assert usuario_logado is not None
    chamado = chamado_repo.obter_por_id(id)

    # Verificar se chamado existe e pertence ao usuário
    if not chamado or chamado.usuario_id != usuario_logado["id"]:
        informar_erro(request, "Chamado não encontrado")
        logger.warning(
            f"Usuário {usuario_logado['id']} tentou excluir chamado {id} sem permissão"
        )
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se chamado está aberto
    if chamado.status != StatusChamado.ABERTO:
        informar_erro(request, "Apenas chamados abertos podem ser excluídos")
        logger.warning(
            f"Usuário {usuario_logado['id']} tentou excluir chamado {id} com status {chamado.status.value}"
        )
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se há respostas de administrador
    if chamado_interacao_repo.tem_resposta_admin(id):
        informar_erro(request, "Não é possível excluir chamados que já possuem resposta do administrador")
        logger.warning(
            f"Usuário {usuario_logado['id']} tentou excluir chamado {id} que possui respostas de admin"
        )
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Tudo OK, pode excluir
    chamado_repo.excluir(id)
    logger.info(f"Chamado {id} excluído por usuário {usuario_logado['id']}")
    informar_sucesso(request, "Chamado excluído com sucesso!")

    return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
