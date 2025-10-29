"""
Módulo de utilitários para manipulação de datetime com timezone.

Centraliza toda criação de datetime no sistema para garantir
consistência de timezone em toda a aplicação.
"""
from datetime import datetime, date
from zoneinfo import ZoneInfo
from typing import Optional
from util.config import APP_TIMEZONE


def agora() -> datetime:
    """
    Retorna datetime atual no timezone configurado da aplicação.

    Esta função deve ser usada em vez de datetime.now() para garantir
    que todos os timestamps sejam criados com o timezone correto.

    Returns:
        datetime: Datetime atual com timezone configurado (America/Sao_Paulo)

    Example:
        >>> from util.datetime_util import agora
        >>> timestamp = agora()
        >>> print(timestamp)
        2025-10-28 14:30:00-03:00
    """
    return datetime.now(APP_TIMEZONE)


def hoje() -> date:
    """
    Retorna date de hoje no timezone configurado da aplicação.

    Returns:
        date: Data atual no timezone configurado

    Example:
        >>> from util.datetime_util import hoje
        >>> data = hoje()
        >>> print(data)
        2025-10-28
    """
    return agora().date()


def converter_para_timezone(dt: datetime, tz: Optional[ZoneInfo] = None) -> datetime:
    """
    Converte um datetime para o timezone especificado.

    Se o datetime fornecido for naive (sem timezone), assume UTC.
    Se o timezone de destino não for especificado, usa APP_TIMEZONE.

    Args:
        dt: Datetime a ser convertido
        tz: Timezone de destino (opcional, padrão: APP_TIMEZONE)

    Returns:
        datetime: Datetime convertido para o timezone especificado

    Example:
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> from util.datetime_util import converter_para_timezone
        >>>
        >>> # Converter UTC para timezone da aplicação
        >>> utc_time = datetime(2025, 10, 28, 17, 30, tzinfo=ZoneInfo("UTC"))
        >>> local_time = converter_para_timezone(utc_time)
        >>> print(local_time)
        2025-10-28 14:30:00-03:00
    """
    if tz is None:
        tz = APP_TIMEZONE

    # Se datetime é naive (sem timezone), assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    # Converte para o timezone de destino
    return dt.astimezone(tz)


def datetime_para_string_iso(dt: datetime) -> str:
    """
    Converte datetime para string ISO 8601 com timezone.

    Args:
        dt: Datetime a ser convertido

    Returns:
        str: String no formato ISO 8601 (YYYY-MM-DDTHH:MM:SS+HH:MM)

    Example:
        >>> from util.datetime_util import agora, datetime_para_string_iso
        >>> timestamp = agora()
        >>> iso_string = datetime_para_string_iso(timestamp)
        >>> print(iso_string)
        2025-10-28T14:30:00-03:00
    """
    return dt.isoformat()


def string_iso_para_datetime(iso_string: str) -> datetime:
    """
    Converte string ISO 8601 para datetime com timezone.

    Args:
        iso_string: String no formato ISO 8601

    Returns:
        datetime: Datetime parseado com timezone

    Example:
        >>> from util.datetime_util import string_iso_para_datetime
        >>> dt = string_iso_para_datetime("2025-10-28T14:30:00-03:00")
        >>> print(dt)
        2025-10-28 14:30:00-03:00
    """
    return datetime.fromisoformat(iso_string)
