from fastapi import APIRouter

from util.rate_limiter import RateLimiter
from util.template_util import criar_templates


router = APIRouter(prefix="/admin/curtidas")
templates = criar_templates("templates/admin/curtidas")

admin_curtidas_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_curtidas",
)