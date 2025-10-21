from pydantic import BaseModel, field_validator, model_validator
from dtos.validators import (
    validar_email,
    validar_perfil_usuario,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_string_obrigatoria,
)
from util.perfis import Perfil


class LoginDTO(BaseModel):
    """DTO para validação de dados de login"""

    email: str
    senha: str

    _validar_email = field_validator("email")(validar_email())
    _validar_senha = field_validator("senha")(validar_senha_forte())


class CadastroDTO(BaseModel):
    """DTO para validação de dados de cadastro"""

    perfil: str
    nome: str
    email: str
    senha: str
    confirmar_senha: str

    _validar_perfil = field_validator("perfil")(validar_perfil_usuario(Perfil))
    _validar_nome = field_validator("nome")(validar_nome_pessoa())
    _validar_email = field_validator("email")(validar_email())
    _validar_senha = field_validator("senha")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(
        validar_string_obrigatoria(
            "Confirmação de Senha", tamanho_minimo=8, tamanho_maximo=128
        )
    )

    @model_validator(mode="after")
    def validar_senhas_coincidem(self) -> "CadastroDTO":
        """Valida se senha e confirmação são iguais"""
        if self.senha != self.confirmar_senha:
            raise ValueError("As senhas não coincidem.")
        return self


class EsqueciSenhaDTO(BaseModel):
    """DTO para validação de recuperação de senha"""

    email: str

    _validar_email = field_validator("email")(validar_email())


class RedefinirSenhaDTO(BaseModel):
    """DTO para validação de redefinição de senha"""

    token: str
    senha: str
    confirmar_senha: str

    _validar_token = field_validator("token")(
        validar_string_obrigatoria("Token", tamanho_minimo=1)
    )
    _validar_senha = field_validator("senha")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(
        validar_string_obrigatoria()
    )

    @model_validator(mode="after")
    def validar_senhas_coincidem(self) -> "RedefinirSenhaDTO":
        """Valida se senha e confirmação são iguais"""
        if self.senha != self.confirmar_senha:
            raise ValueError("As senhas não coincidem.")
        return self
