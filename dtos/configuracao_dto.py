"""
DTOs para validação de configurações do sistema.

Cada categoria de configuração tem validações específicas para prevenir
valores perigosos ou inválidos.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ConfiguracaoBaseDTO(BaseModel):
    """DTO base para configurações"""
    chave: str = Field(..., min_length=1, max_length=100)
    valor: str = Field(..., min_length=1, max_length=1000)
    descricao: Optional[str] = Field(default="", max_length=500)


class ConfiguracaoAplicacaoDTO(BaseModel):
    """DTO para configurações de aplicação (nome, email, etc)"""
    app_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    resend_from_email: Optional[str] = Field(default=None, min_length=5, max_length=255)
    resend_from_name: Optional[str] = Field(default=None, min_length=1, max_length=100)

    @field_validator('resend_from_email')
    @classmethod
    def validar_email(cls, v):
        if v is None:
            return v
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Email inválido')
        return v


class ConfiguracaoFotosDTO(BaseModel):
    """DTO para configurações de fotos"""
    foto_perfil_tamanho_max: Optional[int] = Field(default=None, ge=64, le=2048)
    foto_max_upload_bytes: Optional[int] = Field(default=None, ge=102400, le=52428800)  # 100KB - 50MB

    @field_validator('foto_perfil_tamanho_max')
    @classmethod
    def validar_tamanho_foto(cls, v):
        if v is not None and v % 2 != 0:
            raise ValueError('Tamanho deve ser número par de pixels')
        return v


class ConfiguracaoRateLimitDTO(BaseModel):
    """DTO genérico para configurações de rate limiting"""
    max_tentativas: int = Field(..., ge=1, le=1000, description="Máximo de tentativas permitidas")
    minutos: int = Field(..., ge=1, le=1440, description="Período em minutos (máx 24h)")

    @field_validator('max_tentativas')
    @classmethod
    def validar_max_tentativas(cls, v):
        if v < 1:
            raise ValueError('Deve permitir pelo menos 1 tentativa')
        if v > 1000:
            raise ValueError('Limite muito alto (máximo 1000)')
        return v

    @field_validator('minutos')
    @classmethod
    def validar_minutos(cls, v):
        if v < 1:
            raise ValueError('Período deve ser pelo menos 1 minuto')
        if v > 1440:  # 24 horas
            raise ValueError('Período máximo é 24 horas (1440 minutos)')
        return v


class ConfiguracaoRateLimitLoginDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de login (validações mais restritas)"""
    max_tentativas: int = Field(..., ge=3, le=20, description="Tentativas de login (3-20)")
    minutos: int = Field(..., ge=1, le=60, description="Período em minutos (1-60)")


class ConfiguracaoRateLimitCadastroDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de cadastro"""
    max_tentativas: int = Field(..., ge=1, le=10, description="Tentativas de cadastro (1-10)")
    minutos: int = Field(..., ge=5, le=120, description="Período em minutos (5-120)")


class ConfiguracaoRateLimitSenhaDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de recuperação/alteração de senha"""
    max_tentativas: int = Field(..., ge=1, le=10, description="Tentativas (1-10)")
    minutos: int = Field(..., ge=1, le=60, description="Período em minutos (1-60)")


class ConfiguracaoUIDTO(BaseModel):
    """DTO para configurações de interface"""
    toast_auto_hide_delay_ms: Optional[int] = Field(default=None, ge=1000, le=30000)

    @field_validator('toast_auto_hide_delay_ms')
    @classmethod
    def validar_delay(cls, v):
        if v is not None:
            if v < 1000:
                raise ValueError('Delay mínimo é 1000ms (1 segundo)')
            if v > 30000:
                raise ValueError('Delay máximo é 30000ms (30 segundos)')
        return v


class EditarConfiguracaoDTO(BaseModel):
    """DTO para edição de uma configuração individual"""
    chave: str = Field(..., min_length=1, max_length=100)
    valor: str = Field(..., min_length=1, max_length=1000)

    @field_validator('valor')
    @classmethod
    def validar_valor_nao_vazio(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Valor não pode ser vazio')
        return v.strip()

    @field_validator('chave')
    @classmethod
    def validar_chave_formato(cls, v):
        """Valida que a chave segue o padrão snake_case"""
        import re
        if not re.match(r'^[a-z][a-z0-9_]*$', v):
            raise ValueError('Chave deve estar em snake_case (apenas letras minúsculas, números e underscore)')
        return v


class ValidarRateLimitDTO(BaseModel):
    """DTO para validação de qualquer par max/minutos de rate limit"""
    max_tentativas: str = Field(..., description="Máximo de tentativas")
    minutos: str = Field(..., description="Período em minutos")

    @field_validator('max_tentativas', 'minutos')
    @classmethod
    def validar_numerico(cls, v, info):
        """Valida que os valores são números inteiros positivos"""
        try:
            num = int(v)
            if num < 1:
                raise ValueError(f'{info.field_name} deve ser pelo menos 1')
            if info.field_name == 'max_tentativas' and num > 1000:
                raise ValueError('Máximo de tentativas não pode exceder 1000')
            if info.field_name == 'minutos' and num > 1440:
                raise ValueError('Período não pode exceder 1440 minutos (24 horas)')
            return v
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f'{info.field_name} deve ser um número inteiro')
            raise
