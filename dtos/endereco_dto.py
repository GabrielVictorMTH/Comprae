"""
DTOs para operações com Endereços.
"""
from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
    validar_cep,
    validar_uf,
)


class CriarEnderecoDTO(BaseModel):
    """DTO para criação de endereço"""

    titulo: str
    logradouro: str
    numero: str
    complemento: Optional[str] = ""
    bairro: str
    cidade: str
    uf: str
    cep: str

    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria("Título", tamanho_maximo=50)
    )
    _validar_logradouro = field_validator("logradouro")(
        validar_string_obrigatoria("Logradouro", tamanho_maximo=100)
    )
    _validar_numero = field_validator("numero")(
        validar_string_obrigatoria("Número", tamanho_maximo=10)
    )
    # Complemento é opcional
    _validar_bairro = field_validator("bairro")(
        validar_string_obrigatoria("Bairro", tamanho_maximo=50)
    )
    _validar_cidade = field_validator("cidade")(
        validar_string_obrigatoria("Cidade", tamanho_maximo=50)
    )
    _validar_uf = field_validator("uf")(validar_uf())
    _validar_cep = field_validator("cep")(validar_cep())


class AlterarEnderecoDTO(BaseModel):
    """DTO para alteração de endereço"""

    id: int
    titulo: str
    logradouro: str
    numero: str
    complemento: Optional[str] = ""
    bairro: str
    cidade: str
    uf: str
    cep: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria("Título", tamanho_maximo=50)
    )
    _validar_logradouro = field_validator("logradouro")(
        validar_string_obrigatoria("Logradouro", tamanho_maximo=100)
    )
    _validar_numero = field_validator("numero")(
        validar_string_obrigatoria("Número", tamanho_maximo=10)
    )
    _validar_bairro = field_validator("bairro")(
        validar_string_obrigatoria("Bairro", tamanho_maximo=50)
    )
    _validar_cidade = field_validator("cidade")(
        validar_string_obrigatoria("Cidade", tamanho_maximo=50)
    )
    _validar_uf = field_validator("uf")(validar_uf())
    _validar_cep = field_validator("cep")(validar_cep())