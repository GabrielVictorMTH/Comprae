"""DTOs - Data Transfer Objects para validação de dados"""

from .auth_dto import LoginDTO, CadastroDTO, EsqueciSenhaDTO, RedefinirSenhaDTO
from .usuario_dto import CriarUsuarioDTO, AlterarUsuarioDTO
from .tarefa_dto import CriarTarefaDTO, AlterarTarefaDTO
from .perfil_dto import EditarPerfilDTO, AlterarSenhaDTO

__all__ = [
    "LoginDTO",
    "CadastroDTO",
    "EsqueciSenhaDTO",
    "RedefinirSenhaDTO",
    "CriarUsuarioDTO",
    "AlterarUsuarioDTO",
    "CriarTarefaDTO",
    "AlterarTarefaDTO",
    "EditarPerfilDTO",
    "AlterarSenhaDTO",
]
