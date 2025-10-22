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
        token_redefinicao: Token para redefinição de senha (opcional)
        data_token: Data de expiração do token (opcional)
        data_cadastro: Data de cadastro do usuário (opcional)

    Nota: A foto do usuário é armazenada no filesystem em /static/img/usuarios/{id:06d}.jpg
          Use util.foto_util para manipular fotos de usuários.
    """
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    token_redefinicao: Optional[str] = None
    data_token: Optional[str] = None
    data_cadastro: Optional[str] = None
