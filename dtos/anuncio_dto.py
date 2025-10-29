"""
DTOs para operações com Anúncios (Produtos).
"""
from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
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

    @field_validator("peso")
    @classmethod
    def validar_peso(cls, v: float) -> float:
        """Valida se o peso é positivo"""
        if v <= 0:
            raise ValueError("Peso deve ser maior que zero")
        return v

    @field_validator("preco")
    @classmethod
    def validar_preco(cls, v: float) -> float:
        """Valida se o preço é positivo"""
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return v

    @field_validator("estoque")
    @classmethod
    def validar_estoque(cls, v: int) -> int:
        """Valida se o estoque não é negativo"""
        if v < 0:
            raise ValueError("Estoque não pode ser negativo")
        return v


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

    @field_validator("peso")
    @classmethod
    def validar_peso(cls, v: float) -> float:
        """Valida se o peso é positivo"""
        if v <= 0:
            raise ValueError("Peso deve ser maior que zero")
        return v

    @field_validator("preco")
    @classmethod
    def validar_preco(cls, v: float) -> float:
        """Valida se o preço é positivo"""
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return v

    @field_validator("estoque")
    @classmethod
    def validar_estoque(cls, v: int) -> int:
        """Valida se o estoque não é negativo"""
        if v < 0:
            raise ValueError("Estoque não pode ser negativo")
        return v


class FiltroAnuncioDTO(BaseModel):
    """DTO para filtrar anúncios na busca"""

    nome: Optional[str] = None
    id_categoria: Optional[int] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    apenas_ativos: bool = True

    # Validações opcionais
    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo())


class ModerarProdutoDTO(BaseModel):
    """DTO para reprovar/moderar produto"""
    id: int
    motivo_reprovacao: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_motivo = field_validator("motivo_reprovacao")(
        validar_string_obrigatoria("Motivo", tamanho_minimo=10, tamanho_maximo=500)
    )