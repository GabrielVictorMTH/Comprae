"""
DTOs para operações com Anúncios (Produtos).
"""
from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
    validar_valor_monetario,
    validar_numero_positivo,
)


class CriarAnuncioDTO(BaseModel):
    """DTO para criação de anúncio"""

    id_categoria: int
    nome: str
    descricao: str
    peso: float
    preco: float
    estoque: int

    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_minimo=10, tamanho_maximo=1000)
    )
    _validar_peso = field_validator("peso")(validar_numero_positivo("Peso"))
    _validar_preco = field_validator("preco")(validar_valor_monetario())
    _validar_estoque = field_validator("estoque")(validar_numero_positivo("Estoque"))


class AlterarAnuncioDTO(BaseModel):
    """DTO para alteração de anúncio"""

    id: int
    id_categoria: int
    nome: str
    descricao: str
    peso: float
    preco: float
    estoque: int
    ativo: bool

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_minimo=10, tamanho_maximo=1000)
    )
    _validar_peso = field_validator("peso")(validar_numero_positivo("Peso"))
    _validar_preco = field_validator("preco")(validar_valor_monetario())
    _validar_estoque = field_validator("estoque")(validar_numero_positivo("Estoque"))


class FiltroAnuncioDTO(BaseModel):
    """DTO para filtrar anúncios na busca"""

    nome: Optional[str] = None
    id_categoria: Optional[int] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    apenas_ativos: bool = True

    # Validações opcionais
    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo())