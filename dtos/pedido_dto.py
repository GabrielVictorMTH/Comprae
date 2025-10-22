"""
DTOs para operações com Pedidos.
"""
from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_id_positivo,
    validar_string_obrigatoria,
)


class CriarPedidoDTO(BaseModel):
    """DTO para criação de pedido (compra)"""

    id_endereco: int
    id_anuncio: int

    _validar_id_endereco = field_validator("id_endereco")(validar_id_positivo())
    _validar_id_anuncio = field_validator("id_anuncio")(validar_id_positivo())


class AtualizarStatusPedidoDTO(BaseModel):
    """DTO para vendedor atualizar status do pedido"""

    id_pedido: int
    status: str
    codigo_rastreio: Optional[str] = None

    _validar_id = field_validator("id_pedido")(validar_id_positivo())

    @field_validator("status")
    @classmethod
    def validar_status(cls, v: str) -> str:
        """Valida se o status é válido"""
        from util.status_pedido import StatusPedido
        if v not in StatusPedido.valores():
            raise ValueError(f"Status inválido. Use: {', '.join(StatusPedido.valores())}")
        return v


class AvaliarPedidoDTO(BaseModel):
    """DTO para comprador avaliar pedido após entrega"""

    id_pedido: int
    nota_avaliacao: int
    comentario_avaliacao: str

    _validar_id = field_validator("id_pedido")(validar_id_positivo())

    @field_validator("nota_avaliacao")
    @classmethod
    def validar_nota(cls, v: int) -> int:
        """Valida se a nota está entre 1 e 5"""
        if not 1 <= v <= 5:
            raise ValueError("Nota deve estar entre 1 e 5")
        return v

    _validar_comentario = field_validator("comentario_avaliacao")(
        validar_string_obrigatoria("Comentário", tamanho_minimo=10, tamanho_maximo=500)
    )


class CancelarPedidoDTO(BaseModel):
    """DTO para cancelar pedido"""

    id_pedido: int

    _validar_id = field_validator("id_pedido")(validar_id_positivo())