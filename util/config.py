"""
Módulo de configurações centralizadas da aplicação.

Carrega e disponibiliza todas as variáveis de ambiente e configurações
do sistema em um único local, facilitando a manutenção e evitando duplicação.
"""
import os
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# === Configurações da Aplicação ===
APP_NAME = os.getenv("APP_NAME", "Sistema Web")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-mude-isso-em-producao")

# === Validação de Segurança ===
# Verifica se SECRET_KEY padrão está sendo usada em produção
RUNNING_MODE_CHECK = os.getenv("RUNNING_MODE", "Production")
if RUNNING_MODE_CHECK.lower() != "development":
    if SECRET_KEY == "sua-chave-secreta-super-segura-mude-isso-em-producao":
        raise ValueError(
            "SEGURANÇA CRÍTICA: SECRET_KEY padrão não pode ser usada em produção!\n"
            "Configure uma chave secreta forte no arquivo .env:\n"
            "SECRET_KEY=sua-chave-aleatoria-gerada-aqui\n"
            "Você pode gerar uma com: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

# === Configurações do Banco de Dados ===
DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")

# === Configurações de Logging ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))

# === Configurações de Email (Resend.com) ===
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "noreply@seudominio.com")
RESEND_FROM_NAME = os.getenv("RESEND_FROM_NAME", APP_NAME)

# === Configurações do Servidor ===
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# === Modo de Execução ===
RUNNING_MODE = os.getenv("RUNNING_MODE", "Production")
IS_DEVELOPMENT = RUNNING_MODE.lower() == "development"

# === Configurações de Fotos de Perfil ===
FOTO_PERFIL_TAMANHO_MAX = int(os.getenv("FOTO_PERFIL_TAMANHO_MAX", "256"))
# Tamanho máximo em bytes (5MB)
FOTO_MAX_UPLOAD_BYTES = int(os.getenv("FOTO_MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))

# === Configurações de Senha ===
PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
PASSWORD_MAX_LENGTH = int(os.getenv("PASSWORD_MAX_LENGTH", "128"))

# === Configurações de UI (Frontend) ===
TOAST_AUTO_HIDE_DELAY_MS = int(os.getenv("TOAST_AUTO_HIDE_DELAY_MS", "5000"))

# === Configurações de Rate Limiting ===
RATE_LIMIT_LOGIN_MAX = int(os.getenv("RATE_LIMIT_LOGIN_MAX", "5"))
RATE_LIMIT_LOGIN_MINUTOS = int(os.getenv("RATE_LIMIT_LOGIN_MINUTOS", "5"))
RATE_LIMIT_CADASTRO_MAX = int(os.getenv("RATE_LIMIT_CADASTRO_MAX", "3"))
RATE_LIMIT_CADASTRO_MINUTOS = int(os.getenv("RATE_LIMIT_CADASTRO_MINUTOS", "10"))
RATE_LIMIT_ESQUECI_SENHA_MAX = int(os.getenv("RATE_LIMIT_ESQUECI_SENHA_MAX", "1"))
RATE_LIMIT_ESQUECI_SENHA_MINUTOS = int(os.getenv("RATE_LIMIT_ESQUECI_SENHA_MINUTOS", "1"))

# === Versão da Aplicação ===
VERSION = "1.0.0"

# === Configurações de Timezone ===
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")
APP_TIMEZONE = ZoneInfo(TIMEZONE)
