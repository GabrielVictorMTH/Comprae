"""
Módulo de rate limiting reutilizável.

Implementa limitação de requisições (rate limiting) para proteger
rotas contra abuso, brute force e DDoS.

Uso:
    from util.rate_limiter import RateLimiter, verificar_rate_limit
    from util.config import RATE_LIMIT_LOGIN_MAX, RATE_LIMIT_LOGIN_MINUTOS

    # Criar instância global
    login_limiter = RateLimiter(max_tentativas=5, janela_minutos=5)

    # Em rota FastAPI
    @router.post("/login")
    async def post_login(request: Request, ...):
        ip = request.client.host if request.client else "unknown"

        if not login_limiter.verificar(ip):
            raise HTTPException(status_code=429, detail="Muitas tentativas")
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional
from util.logger_config import logger


class RateLimiter:
    """
    Rate limiter baseado em janela deslizante (sliding window).

    Mantém registro de tentativas por identificador (geralmente IP)
    e bloqueia se exceder limite em janela de tempo.

    Attributes:
        max_tentativas: Número máximo de tentativas permitidas
        janela: Timedelta representando janela de tempo
        tentativas: Dict de identificador -> lista de timestamps
    """

    def __init__(
        self,
        max_tentativas: int = 5,
        janela_minutos: int = 5,
        nome: str = "default",
    ):
        """
        Inicializa rate limiter.

        Args:
            max_tentativas: Número máximo de tentativas na janela
            janela_minutos: Tamanho da janela em minutos
            nome: Nome descritivo do limiter (para logs)
        """
        if max_tentativas <= 0:
            raise ValueError("max_tentativas deve ser positivo")
        if janela_minutos <= 0:
            raise ValueError("janela_minutos deve ser positivo")

        self.max_tentativas = max_tentativas
        self.janela = timedelta(minutes=janela_minutos)
        self.janela_minutos = janela_minutos
        self.nome = nome
        self.tentativas: defaultdict[str, list[datetime]] = defaultdict(list)

    def verificar(self, identificador: str) -> bool:
        """
        Verifica se identificador está dentro do limite.

        Remove tentativas antigas da janela e verifica se está
        abaixo do máximo. Se estiver, registra nova tentativa.

        Args:
            identificador: Identificador único (geralmente IP)

        Returns:
            True se dentro do limite (permitido)
            False se excedeu limite (bloqueado)
        """
        agora = datetime.now()

        # Limpar tentativas antigas (fora da janela)
        self.tentativas[identificador] = [
            t for t in self.tentativas[identificador] if agora - t < self.janela
        ]

        # Verificar se excedeu limite
        if len(self.tentativas[identificador]) >= self.max_tentativas:
            logger.warning(
                f"Rate limit excedido [{self.nome}] - "
                f"Identificador: {identificador}, "
                f"Tentativas: {len(self.tentativas[identificador])}/{self.max_tentativas}"
            )
            return False

        # Registrar nova tentativa
        self.tentativas[identificador].append(agora)
        return True

    def limpar(self, identificador: Optional[str] = None) -> None:
        """
        Limpa tentativas registradas.

        Args:
            identificador: Se fornecido, limpa apenas este identificador.
                          Se None, limpa todos (útil para testes).
        """
        if identificador:
            if identificador in self.tentativas:
                del self.tentativas[identificador]
                logger.debug(f"Limpo rate limit para identificador: {identificador}")
        else:
            self.tentativas.clear()
            logger.debug(f"Limpo todos os rate limits [{self.nome}]")

    def obter_tentativas_restantes(self, identificador: str) -> int:
        """
        Retorna número de tentativas restantes para identificador.

        Args:
            identificador: Identificador único

        Returns:
            Número de tentativas restantes (0 se bloqueado)
        """
        agora = datetime.now()

        # Limpar tentativas antigas
        self.tentativas[identificador] = [
            t for t in self.tentativas[identificador] if agora - t < self.janela
        ]

        tentativas_atuais = len(self.tentativas[identificador])
        return max(0, self.max_tentativas - tentativas_atuais)

    def obter_tempo_reset(self, identificador: str) -> Optional[timedelta]:
        """
        Retorna tempo até o reset do limite.

        Args:
            identificador: Identificador único

        Returns:
            Timedelta até reset, ou None se não bloqueado
        """
        if identificador not in self.tentativas or not self.tentativas[identificador]:
            return None

        agora = datetime.now()

        # Limpar tentativas antigas
        self.tentativas[identificador] = [
            t for t in self.tentativas[identificador] if agora - t < self.janela
        ]

        # Se ainda está bloqueado, calcular tempo até reset
        if len(self.tentativas[identificador]) >= self.max_tentativas:
            # Reset quando a tentativa mais antiga sair da janela
            tentativa_mais_antiga = self.tentativas[identificador][0]
            tempo_reset = (tentativa_mais_antiga + self.janela) - agora
            return tempo_reset if tempo_reset.total_seconds() > 0 else None

        return None

    def __repr__(self) -> str:
        """Representação string do limiter."""
        return (
            f"RateLimiter(nome='{self.nome}', "
            f"max_tentativas={self.max_tentativas}, "
            f"janela_minutos={self.janela_minutos})"
        )


def obter_identificador_cliente(request) -> str:
    """
    Extrai identificador único do cliente (geralmente IP).

    Args:
        request: FastAPI Request object

    Returns:
        String identificadora (IP ou "unknown")
    """
    if hasattr(request, "client") and request.client:
        return request.client.host
    return "unknown"
