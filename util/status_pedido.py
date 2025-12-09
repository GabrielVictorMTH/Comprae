from enum import Enum

class StatusPedido(str, Enum):
    NEGOCIANDO = "Negociando"
    PENDENTE = "Pendente"
    PAGO = "Pago"
    ENVIADO = "Enviado"
    ENTREGUE = "Entregue"
    CANCELADO = "Cancelado"

    @classmethod
    def valores(cls) -> list[str]:
        return [status.value for status in cls]

    @classmethod
    def pode_cancelar(cls, status: str) -> bool:
        """Verifica se o pedido pode ser cancelado no status atual"""
        return status in [cls.NEGOCIANDO.value, cls.PENDENTE.value]