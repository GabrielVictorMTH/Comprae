from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria


class CriarInteracaoDTO(BaseModel):
    mensagem: str

    _validar_mensagem = field_validator("mensagem")(
        validar_string_obrigatoria(
            nome_campo="Mensagem",
            tamanho_minimo=10,
            tamanho_maximo=2000
        )
    )
