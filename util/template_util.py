from jinja2 import Environment, FileSystemLoader
from fastapi.templating import Jinja2Templates
from util.flash_messages import obter_mensagens
from util.config import APP_NAME, VERSION
from datetime import datetime

def formatar_data_br(data_str):
    """
    Converte data ISO (YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS) para formato brasileiro (DD/MM/YYYY)

    Args:
        data_str: String com data no formato ISO ou objeto datetime

    Returns:
        String formatada no padrão brasileiro ou string vazia se inválido
    """
    if not data_str:
        return ""

    try:
        # Se já for um objeto datetime
        if isinstance(data_str, datetime):
            return data_str.strftime("%d/%m/%Y")

        # Se for string, tentar parsear
        data_str = str(data_str).strip()

        # Tentar formato completo com hora (YYYY-MM-DD HH:MM:SS)
        if len(data_str) > 10:
            data = datetime.strptime(data_str[:19], "%Y-%m-%d %H:%M:%S")
        else:
            # Formato apenas data (YYYY-MM-DD)
            data = datetime.strptime(data_str[:10], "%Y-%m-%d")

        return data.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return data_str  # Retorna o valor original se não conseguir converter

def formatar_data_hora_br(data_str):
    """
    Converte data/hora ISO para formato brasileiro completo (DD/MM/YYYY HH:MM:SS)

    Args:
        data_str: String com data/hora no formato ISO ou objeto datetime

    Returns:
        String formatada no padrão brasileiro ou string vazia se inválido
    """
    if not data_str:
        return ""

    try:
        # Se já for um objeto datetime
        if isinstance(data_str, datetime):
            return data_str.strftime("%d/%m/%Y %H:%M:%S")

        # Se for string, tentar parsear
        data_str = str(data_str).strip()

        # Tentar formato completo com hora
        if len(data_str) > 10:
            data = datetime.strptime(data_str[:19], "%Y-%m-%d %H:%M:%S")
            return data.strftime("%d/%m/%Y %H:%M:%S")
        else:
            # Se só tiver data, adicionar 00:00:00
            data = datetime.strptime(data_str[:10], "%Y-%m-%d")
            return data.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return data_str

def foto_usuario(id: int) -> str:
    """
    Retorna o caminho da foto do usuário para uso em templates.

    Args:
        id: ID do usuário

    Returns:
        String com caminho da foto (ex: /static/img/usuarios/000001.jpg)
    """
    return f"/static/img/usuarios/{id:06d}.jpg"

def criar_templates(pasta: str):
    """Cria Jinja2Templates com funções globais customizadas"""
    # Usar o diretório raiz 'templates' para permitir acesso a base.html e subpastas
    env = Environment(loader=FileSystemLoader("templates"))

    # Adicionar função global para obter mensagens
    env.globals['obter_mensagens'] = obter_mensagens

    # Adicionar variáveis globais de configuração
    env.globals['APP_NAME'] = APP_NAME
    env.globals['VERSION'] = VERSION

    # Adicionar filtros customizados
    env.filters['data_br'] = formatar_data_br
    env.filters['data_hora_br'] = formatar_data_hora_br
    env.filters['foto_usuario'] = foto_usuario

    templates = Jinja2Templates(env=env)
    return templates
