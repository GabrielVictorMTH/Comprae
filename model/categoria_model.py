from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Categoria:
    """
    Representa uma categoria do sistema.

    Atributos:
        id: Identificador único (gerado pelo banco)
        nome: Nome da categoria
        descricao: Descrição opcional
        data_cadastro: Timestamp de criação
        data_atualizacao: Timestamp da última atualização
    """
    id: Optional[int] = None
    nome: str = ""
    descricao: str = ""
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
