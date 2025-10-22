"""
DTOs para gerenciamento de perfil do usuário.

Contém validações para edição de dados pessoais e alteração de senha.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_string_obrigatoria,
    validar_senhas_coincidem,
)


class EditarPerfilDTO(BaseModel):
    """DTO para edição de dados do perfil do usuário."""

    nome: str = Field(..., description="Nome completo do usuário", min_length=4, max_length=128)
    email: str = Field(..., description="E-mail do usuário", examples=["usuario@exemplo.com"])

    _validar_nome = field_validator("nome")(validar_nome_pessoa(min_palavras=2))
    _validar_email = field_validator("email")(validar_email())


class AlterarSenhaDTO(BaseModel):
    """DTO para alteração de senha do usuário."""

    senha_atual: str = Field(..., description="Senha atual do usuário", min_length=1, max_length=128)
    senha_nova: str = Field(..., description="Nova senha desejada", min_length=8, max_length=128)
    confirmar_senha: str = Field(..., description="Confirmação da nova senha", min_length=8, max_length=128)

    _validar_senha_atual = field_validator("senha_atual")(
        validar_string_obrigatoria("Senha atual")
    )
    _validar_senha_nova = field_validator("senha_nova")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(
        validar_string_obrigatoria(
            "Confirmação de senha", tamanho_minimo=8, tamanho_maximo=128
        )
    )

    _validar_senhas_match = model_validator(mode="after")(
        validar_senhas_coincidem("senha_nova", "confirmar_senha")
    )
