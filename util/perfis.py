from enum import Enum
from typing import Optional

class Perfil(str, Enum):
    """
    Enum centralizado para perfis de usuário.

    Este é a FONTE ÚNICA DA VERDADE para perfis no sistema.
    SEMPRE use este Enum ao referenciar perfis, NUNCA strings literais.

    Exemplos:
        - Correto: perfil = Perfil.ADMIN.value
        - Correto: perfil = Perfil.CLIENTE.value
        - Correto: perfil = Perfil.VENDEDOR.value
        - ERRADO: perfil = "admin"
        - ERRADO: perfil = "cliente"
        - ERRADO: perfil = "vendedor"
    """

    # PERFIS DO SEU SISTEMA #####################################
    ADMIN = "Administrador"
    CLIENTE = "Cliente"
    VENDEDOR = "Vendedor"
    # FIM DOS PERFIS ############################################

    def __str__(self) -> str:
        """Retorna o valor do perfil como string"""
        return self.value

    @classmethod
    def valores(cls) -> list[str]:
        """
        Retorna lista de todos os valores de perfis.

        Returns:
            Lista com os valores: ["admin", "cliente"]
        """
        return [perfil.value for perfil in cls]

    @classmethod
    def existe(cls, valor: str) -> bool:
        """
        Verifica se um valor de perfil é válido.

        Args:
            valor: String do perfil a validar

        Returns:
            True se o perfil existe, False caso contrário
        """
        return valor in cls.valores()

    @classmethod
    def from_string(cls, valor: str) -> Optional['Perfil']:
        """
        Converte uma string para o Enum Perfil correspondente.

        Args:
            valor: String do perfil ("admin" ou "cliente")

        Returns:
            Enum Perfil correspondente ou None se inválido

        Examples:
            >>> Perfil.from_string("admin")
            <Perfil.ADMIN: 'admin'>
            >>> Perfil.from_string("invalido")
            None
        """
        try:
            return cls(valor)
        except ValueError:
            return None

    @classmethod
    def validar(cls, valor: str) -> str:
        """
        Valida e retorna o valor do perfil, levantando exceção se inválido.

        Args:
            valor: String do perfil a validar

        Returns:
            O valor validado

        Raises:
            ValueError: Se o perfil não for válido
        """
        if not cls.existe(valor):
            raise ValueError(f'Perfil inválido: {valor}. Use: {", ".join(cls.valores())}')
        return valor
