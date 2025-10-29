from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_texto_minimo_palavras,
    validar_comprimento,
    validar_id_positivo,
)


class CriarTarefaDTO(BaseModel):
    titulo: str
    descricao: str = ""

    _validar_titulo = field_validator("titulo")(
        validar_texto_minimo_palavras(
            min_palavras=2, tamanho_maximo=128, nome_campo="Título"
        )
    )
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=512)
    )


class AlterarTarefaDTO(BaseModel):
    id: int
    titulo: str
    descricao: str = ""
    concluida: bool = False

    _validar_id = field_validator("id")(validar_id_positivo("ID"))
    _validar_titulo = field_validator("titulo")(
        validar_texto_minimo_palavras(
            min_palavras=2, tamanho_maximo=128, nome_campo="Título"
        )
    )
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=500)
    )
