from dataclasses import dataclass
from typing import Optional
from util.perfis import Perfil

@dataclass
class Usuario:
    """
    Model de usuário do sistema.

    Attributes:
        id: Identificador único do usuário
        nome: Nome completo do usuário
        email: E-mail único do usuário
        senha: Hash da senha do usuário
        perfil: Perfil do usuário (usar Perfil.ADMIN.value ou Perfil.CLIENTE.value)
        foto: URL da foto de perfil (opcional)
        token_redefinicao: Token para redefinição de senha (opcional)
        data_token: Data de expiração do token (opcional)
        data_cadastro: Data de cadastro do usuário (opcional)
    """
    id: int
    nome: str
    email: str
    senha: str
    perfil: str = Perfil.ADMIN.value  # Usa Enum Perfil como fonte única da verdade
    foto: Optional[str] = None
    token_redefinicao: Optional[str] = None
    data_token: Optional[str] = None
    data_cadastro: Optional[str] = None
