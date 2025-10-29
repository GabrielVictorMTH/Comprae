"""
DTOs para validação de dados do sistema de chat.
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

from dtos.validators import validar_string_obrigatoria, validar_comprimento


class CriarSalaDTO(BaseModel):
    """DTO para criar ou obter uma sala de chat."""
    outro_usuario_id: int

    @field_validator('outro_usuario_id')
    @classmethod
    def validar_outro_usuario_id(cls, v):
        if v <= 0:
            raise ValueError('ID do usuário deve ser um número positivo.')
        return v


class EnviarMensagemDTO(BaseModel):
    """DTO para enviar uma mensagem em uma sala."""
    sala_id: str
    mensagem: str

    _validar_sala_id = field_validator('sala_id')(validar_string_obrigatoria())
    _validar_mensagem = field_validator('mensagem')(validar_string_obrigatoria())
    _validar_comprimento = field_validator('mensagem')(validar_comprimento(tamanho_minimo=1, tamanho_maximo=5000))


class ConversaResumoDTO(BaseModel):
    """DTO para resumo de uma conversa na lista."""
    sala_id: str
    outro_usuario: dict  # {id, nome, email, foto_url}
    ultima_mensagem: Optional[dict] = None  # {mensagem, data_envio, usuario_id}
    nao_lidas: int = 0
    ultima_atividade: datetime


class UsuarioBuscaDTO(BaseModel):
    """DTO para resultado de busca de usuários."""
    id: int
    nome: str
    email: str
    foto_url: str
