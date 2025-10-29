from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.tarefa_dto import CriarTarefaDTO
from model.tarefa_model import Tarefa
from repo import tarefa_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.config import (
    RATE_LIMIT_TAREFA_CRIAR_MAX,
    RATE_LIMIT_TAREFA_CRIAR_MINUTOS,
    RATE_LIMIT_TAREFA_OPERACAO_MAX,
    RATE_LIMIT_TAREFA_OPERACAO_MINUTOS,
)

router = APIRouter(prefix="/tarefas")
templates = criar_templates("templates/tarefas")

# Rate limiters
from util.rate_limiter import RateLimiter, obter_identificador_cliente

tarefa_criar_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_TAREFA_CRIAR_MAX,
    janela_minutos=RATE_LIMIT_TAREFA_CRIAR_MINUTOS,
    nome="tarefa_criar",
)
tarefa_operacao_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_TAREFA_OPERACAO_MAX,
    janela_minutos=RATE_LIMIT_TAREFA_OPERACAO_MINUTOS,
    nome="tarefa_operacao",
)

@router.get("/listar")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as tarefas do usuário logado"""
    assert usuario_logado is not None
    tarefas = tarefa_repo.obter_todos_por_usuario(usuario_logado["id"])
    return templates.TemplateResponse(
        "tarefas/listar.html",
        {"request": request, "tarefas": tarefas}
    )

@router.get("/cadastrar")
@requer_autenticacao()
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de tarefa"""
    return templates.TemplateResponse("tarefas/cadastrar.html", {"request": request})

@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar(
    request: Request,
    titulo: str = Form(),
    descricao: str = Form(),
    usuario_logado: Optional[dict] = None
):
    """Cadastra uma nova tarefa"""
    assert usuario_logado is not None

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not tarefa_criar_limiter.verificar(ip):
        informar_erro(
            request,
            f"Muitas tentativas de criação de tarefas. Aguarde {RATE_LIMIT_TAREFA_CRIAR_MINUTOS} minuto(s).",
        )
        logger.warning(f"Rate limit excedido para criação de tarefas - IP: {ip}")
        return templates.TemplateResponse(
            "tarefas/cadastrar.html",
            {
                "request": request,
                "erros": {
                    "geral": f"Muitas tentativas de criação de tarefas. Aguarde {RATE_LIMIT_TAREFA_CRIAR_MINUTOS} minuto(s)."
                },
            },
        )

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario = {"titulo": titulo, "descricao": descricao}

    try:
        # Validar com DTO
        dto = CriarTarefaDTO(titulo=titulo, descricao=descricao)

        # Criar tarefa
        tarefa = Tarefa(
            id=0,
            titulo=dto.titulo,
            descricao=dto.descricao,
            concluida=False,
            usuario_id=usuario_logado["id"]
        )

        tarefa_repo.inserir(tarefa)
        logger.info(f"Tarefa '{dto.titulo}' criada por usuário {usuario_logado['id']}")

        informar_sucesso(request, "Tarefa criada com sucesso!")
        return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="tarefas/cadastrar.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
        )

@router.post("/{id}/concluir")
@requer_autenticacao()
async def concluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Marca tarefa como concluída"""
    assert usuario_logado is not None

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not tarefa_operacao_limiter.verificar(ip):
        informar_erro(
            request,
            f"Muitas operações em tarefas. Aguarde {RATE_LIMIT_TAREFA_OPERACAO_MINUTOS} minuto(s).",
        )
        logger.warning(f"Rate limit excedido para operações em tarefas - IP: {ip}")
        return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)

    tarefa = tarefa_repo.obter_por_id(id)

    # Verificar se tarefa existe e pertence ao usuário
    if not tarefa or tarefa.usuario_id != usuario_logado["id"]:
        informar_erro(request, "Tarefa não encontrada")
        logger.warning(f"Usuário {usuario_logado['id']} tentou concluir tarefa {id} sem permissão")
        return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)

    tarefa_repo.marcar_concluida(id)
    logger.info(f"Tarefa {id} concluída por usuário {usuario_logado['id']}")
    informar_sucesso(request, "Tarefa concluída!")
    return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/{id}/excluir")
@requer_autenticacao()
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui tarefa"""
    assert usuario_logado is not None

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not tarefa_operacao_limiter.verificar(ip):
        informar_erro(
            request,
            f"Muitas operações em tarefas. Aguarde {RATE_LIMIT_TAREFA_OPERACAO_MINUTOS} minuto(s).",
        )
        logger.warning(f"Rate limit excedido para operações em tarefas - IP: {ip}")
        return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)

    tarefa = tarefa_repo.obter_por_id(id)

    # Verificar se tarefa existe e pertence ao usuário
    if tarefa and tarefa.usuario_id == usuario_logado["id"]:
        tarefa_repo.excluir(id)
        logger.info(f"Tarefa {id} excluída por usuário {usuario_logado['id']}")
        informar_sucesso(request, "Tarefa excluída com sucesso!")
    else:
        informar_erro(request, "Tarefa não encontrada")
        logger.warning(f"Usuário {usuario_logado['id']} tentou excluir tarefa {id} sem permissão")

    return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)
