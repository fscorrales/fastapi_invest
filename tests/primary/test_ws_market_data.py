import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.modules.primary.schemas import PrimaryCredentials, WSMarketDataParams
from app.modules.primary.services.ws_market_data_service import WSMarketDataService


@pytest.mark.asyncio
async def test_stream_and_disconnect():
    # Mock de credenciales y parámetros
    credentials = PrimaryCredentials(
        username="testuser", password="testpass", url="https://api.mocked.com"
    )

    params = WSMarketDataParams(
        symbols=["GGAL"], entries=["LA", "BI", "OF"], settlement_type="24hs"
    )

    # Instancia del servicio
    service = WSMarketDataService()

    # Mocks
    mock_ws = AsyncMock()
    mock_ws.recv = AsyncMock(
        side_effect=[
            b'{"type":"Md","instrumentId":{"symbol":"GGAL - 24hs"},"timestamp":1,"marketData":{"LA":{"price":100,"size":10}}}',
            asyncio.CancelledError(),
        ]
    )

    mock_ws.send = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_get_token = AsyncMock(
        return_value=MagicMock(websocket_url="wss://mocked.url", x_auth_token="abc123")
    )

    # Parcheamos websockets.connect y get_token
    with (
        patch(
            "app.modules.primary.services.ws_market_data_service.websockets.connect",
            return_value=mock_ws,
        ),
        patch(
            "app.modules.primary.services.ws_market_data_service.get_token",
            mock_get_token,
        ),
    ):
        await service.stream_market_data(credentials, params)

        # Esperamos algunos mensajes
        await asyncio.sleep(0.5)

        # Desconectamos
        await service.disconnect()

        # Aserciones
        mock_ws.send.assert_called_once()
        mock_ws.recv.assert_called()
        mock_ws.close.assert_called_once()
        assert service.producer_task is None
        assert service.consumer_task is None
