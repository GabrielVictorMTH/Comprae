from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    genero: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    sobre_mim: Optional[str] = None
    token_redefinicao: Optional[str] = None
    data_token: Optional[datetime] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
