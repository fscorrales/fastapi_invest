__all__ = ["WSMarketData"]

from .base_websocket import BaseWebsocket


# --------------------------------------------------
class WSMarketData(BaseWebsocket):
    # --------------------------------------------------
    def __init__(self, instruments: list):
        super().__init__()
        self.instruments = instruments
        # Configuración adicional si se necesita

    # --------------------------------------------------
    async def connect(self):
        # Lógica para conectar a WebSocket y recibir datos
        # Solo suscribirse a acciones, bonos, ON
        pass
