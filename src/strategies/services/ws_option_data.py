__all__ = ["WSOptionData"]

from .base_websocket import BaseWebsocket


# --------------------------------------------------
class WSOptionData(BaseWebsocket):
    # --------------------------------------------------
    def __init__(self, options_symbols: list):
        super().__init__()
        self.options_symbols = options_symbols

    # --------------------------------------------------
    async def connect(self):
        # Conectar y suscribirse solo a opciones
        pass
