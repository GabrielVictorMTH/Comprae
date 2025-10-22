from typing import Dict, Any
import sqlite3
from repo import configuracao_repo
from util.logger_config import logger

class ConfigCache:
    """Cache de configurações do sistema para melhor performance"""
    _cache: Dict[str, Any] = {}

    @classmethod
    def obter(cls, chave: str, padrao: str = "") -> str:
        """
        Obtém configuração com cache e tratamento de erros

        Args:
            chave: Chave da configuração
            padrao: Valor padrão se não encontrado

        Returns:
            Valor da configuração ou padrão

        Raises:
            Nenhuma exceção - retorna padrao em caso de erro
        """
        # Retorna do cache se disponível
        if chave in cls._cache:
            return cls._cache[chave]

        # Tenta buscar do banco com error handling
        try:
            config = configuracao_repo.obter_por_chave(chave)
            if config:
                cls._cache[chave] = config.valor
                return config.valor
            else:
                cls._cache[chave] = padrao
                return padrao

        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar configuração '{chave}' do banco: {e}")
            # Retorna padrão em vez de crashar a aplicação
            return padrao

        except Exception as e:
            logger.critical(f"Erro crítico ao acessar configuração '{chave}': {e}")
            # Ainda retorna padrão, mas loga como crítico
            return padrao

    @classmethod
    def limpar(cls):
        """Limpa todo o cache de configurações"""
        cls._cache = {}

    @classmethod
    def limpar_chave(cls, chave: str):
        """Limpa cache de uma chave específica"""
        if chave in cls._cache:
            del cls._cache[chave]

# Instância global para uso em toda a aplicação
config = ConfigCache()
