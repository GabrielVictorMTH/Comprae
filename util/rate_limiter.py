"""
Módulo de rate limiting reutilizável.

Implementa limitação de requisições (rate limiting) para proteger
rotas contra abuso, brute force e DDoS.

Oferece duas classes:
    - RateLimiter: Rate limiter estático (valores fixos na inicialização)
    - DynamicRateLimiter: Rate limiter dinâmico (lê valores do config_cache)

Uso do RateLimiter (estático):
    from util.rate_limiter import RateLimiter

    # Criar instância global
    login_limiter = RateLimiter(max_tentativas=5, janela_minutos=5)

    # Em rota FastAPI
    @router.post("/login")
    async def post_login(request: Request, ...):
        ip = request.client.host if request.client else "unknown"

        if not login_limiter.verificar(ip):
            raise HTTPException(status_code=429, detail="Muitas tentativas")

Uso do DynamicRateLimiter (recomendado):
    from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente

    # Criar instância global (lê valores do banco de dados)
    login_limiter = DynamicRateLimiter(
        chave_max="rate_limit_login_max",
        chave_minutos="rate_limit_login_minutos",
        padrao_max=5,
        padrao_minutos=5,
        nome="login"
    )

    # Em rota FastAPI (igual ao uso estático)
    @router.post("/login")
    async def post_login(request: Request, ...):
        ip = obter_identificador_cliente(request)

        if not login_limiter.verificar(ip):
            raise HTTPException(status_code=429, detail="Muitas tentativas")

    # Mudanças nas configurações no banco são aplicadas automaticamente!
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional
from util.logger_config import logger
from util.config_cache import config


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


class DynamicRateLimiter(RateLimiter):
    """
    Rate limiter dinâmico que busca valores do config_cache a cada verificação.

    Permite alteração de rate limits sem reiniciar o servidor. Os valores
    max_tentativas e janela_minutos são lidos do cache de configuração
    usando as chaves fornecidas.

    Attributes:
        chave_max: Chave de configuração para max_tentativas
        chave_minutos: Chave de configuração para janela_minutos
        padrao_max: Valor padrão se chave não existir
        padrao_minutos: Valor padrão se chave não existir
    """

    def __init__(
        self,
        chave_max: str,
        chave_minutos: str,
        padrao_max: int = 5,
        padrao_minutos: int = 5,
        nome: str = "dynamic",
    ):
        """
        Inicializa rate limiter dinâmico.

        Args:
            chave_max: Chave de configuração para max_tentativas
            chave_minutos: Chave de configuração para janela_minutos
            padrao_max: Valor padrão para max_tentativas
            padrao_minutos: Valor padrão para janela_minutos
            nome: Nome descritivo do limiter (para logs)
        """
        # Validar valores padrão
        if padrao_max <= 0:
            raise ValueError("padrao_max deve ser positivo")
        if padrao_minutos <= 0:
            raise ValueError("padrao_minutos deve ser positivo")

        self.chave_max = chave_max
        self.chave_minutos = chave_minutos
        self.padrao_max = padrao_max
        self.padrao_minutos = padrao_minutos

        # Inicializar com valores atuais do config
        max_tentativas = config.obter_int(chave_max, padrao_max)
        janela_minutos = config.obter_int(chave_minutos, padrao_minutos)

        super().__init__(
            max_tentativas=max_tentativas,
            janela_minutos=janela_minutos,
            nome=nome
        )

    def _atualizar_valores(self) -> None:
        """
        Atualiza valores de max_tentativas e janela_minutos do config_cache.

        Chamado internamente antes de cada verificação para garantir
        que está usando os valores mais recentes.
        """
        max_tentativas = config.obter_int(self.chave_max, self.padrao_max)
        janela_minutos = config.obter_int(self.chave_minutos, self.padrao_minutos)

        # Atualizar apenas se mudou
        if max_tentativas != self.max_tentativas:
            logger.debug(
                f"Rate limiter [{self.nome}] atualizou max_tentativas: "
                f"{self.max_tentativas} -> {max_tentativas}"
            )
            self.max_tentativas = max_tentativas

        if janela_minutos != self.janela_minutos:
            logger.debug(
                f"Rate limiter [{self.nome}] atualizou janela_minutos: "
                f"{self.janela_minutos} -> {janela_minutos}"
            )
            self.janela_minutos = janela_minutos
            self.janela = timedelta(minutes=janela_minutos)

    def verificar(self, identificador: str) -> bool:
        """
        Verifica se identificador está dentro do limite (com valores atualizados).

        Atualiza valores do config_cache antes de verificar, garantindo
        que mudanças em configurações sejam aplicadas imediatamente.

        Args:
            identificador: Identificador único (geralmente IP)

        Returns:
            True se dentro do limite (permitido)
            False se excedeu limite (bloqueado)
        """
        # Atualizar valores antes de verificar
        self._atualizar_valores()

        # Usar lógica da classe pai
        return super().verificar(identificador)

    def obter_tentativas_restantes(self, identificador: str) -> int:
        """
        Retorna número de tentativas restantes (com valores atualizados).

        Args:
            identificador: Identificador único

        Returns:
            Número de tentativas restantes (0 se bloqueado)
        """
        self._atualizar_valores()
        return super().obter_tentativas_restantes(identificador)

    def obter_tempo_reset(self, identificador: str) -> Optional[timedelta]:
        """
        Retorna tempo até o reset do limite (com valores atualizados).

        Args:
            identificador: Identificador único

        Returns:
            Timedelta até reset, ou None se não bloqueado
        """
        self._atualizar_valores()
        return super().obter_tempo_reset(identificador)

    def __repr__(self) -> str:
        """Representação string do limiter dinâmico."""
        return (
            f"DynamicRateLimiter(nome='{self.nome}', "
            f"chave_max='{self.chave_max}', "
            f"chave_minutos='{self.chave_minutos}', "
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
