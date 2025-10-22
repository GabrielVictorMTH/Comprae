from enum import Enum

class StatusPedido(str, Enum):
    PENDENTE = "Pendente"
    PAGO = "Pago"
    ENVIADO = "Enviado"
    ENTREGUE = "Entregue"
    CANCELADO = "Cancelado"

    @classmethod
    def valores(cls) -> list[str]:
        return [status.value for status in cls]