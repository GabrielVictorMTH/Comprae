"""
DTOs para operações com Mensagens.
"""
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
)


class EnviarMensagemDTO(BaseModel):
    """DTO para enviar mensagem"""

    id_destinatario: int
    mensagem: str

    _validar_id_destinatario = field_validator("id_destinatario")(validar_id_positivo())
    _validar_mensagem = field_validator("mensagem")(
        validar_string_obrigatoria("Mensagem", tamanho_minimo=1, tamanho_maximo=500)
    )


class MarcarMensagemLidaDTO(BaseModel):
    """DTO para marcar mensagem como lida"""

    id_mensagem: int

    _validar_id = field_validator("id_mensagem")(validar_id_positivo())