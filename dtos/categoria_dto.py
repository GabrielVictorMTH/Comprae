from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_id_positivo,
)

class CriarCategoriaDTO(BaseModel):
    nome: str
    descricao: str

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )

class AlterarCategoriaDTO(BaseModel):
    id: int
    nome: str
    descricao: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria("Descrição", tamanho_maximo=200)
    )