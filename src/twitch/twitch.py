import json
from typing import Optional
import websocket

import constants
from log import LOG
from singleton import singleton
from twitch.message import MessageTypes


@singleton
class TwitchConn:
    def __init__(self):
        self._ws = websocket.WebSocketApp(
            constants.TWITCH_ENDPOINT,
            on_message=self._on_message,
            on_ping=self._on_ping,
            on_close=self._on_close,
        )

    def run(self) -> None:
        self._ws.run_forever()

    def stop(self) -> None:
        self._ws.close()

    def _on_message(self, ws: websocket.WebSocket, message: str) -> None:
        json_data = json.loads(message)

        if "metadata" not in json_data or "payload" not in json_data:
            LOG.warning(
                f"Twitch sent a message without `metadata` or `payload`: {json_data}"
            )
            return

        MessageTypes.handle(json_data)

    def _on_ping(self, ws: websocket.WebSocketApp, message: Optional[bytes]) -> None:
        ws.sock.pong(message)

    def _on_close(
        self,
        _: websocket.WebSocket,
        close_status_code: Optional[int],
        close_msg: Optional[str],
    ) -> None:
        LOG.warning(
            f"Twitch closed WebSocket connection: ({close_status_code}) {close_msg}"
        )
