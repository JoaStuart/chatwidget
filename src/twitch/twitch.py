import json
from threading import Thread
from typing import Optional
import websocket

import constants
from log import LOG
from singleton import singleton


@singleton
class TwitchConn:
    def __init__(self):
        self._ws = self._make_ws(constants.TWITCH_ENDPOINT)
        self._connected: bool = False

    def _make_ws(self, url: str) -> websocket.WebSocketApp:
        return websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_ping=self._on_ping,
            on_close=self._on_close,
        )

    def run(self) -> None:
        self._connected = True
        Thread(
            target=self._ws.run_forever, name="TwitchConnection", daemon=True
        ).start()

    def stop(self) -> None:
        self._connected = False
        self._ws.close(status=1000, reason="Closing connection.")

    def reconnect(self, reconnect_url: str) -> None:
        self._ws.close()
        self._ws = self._make_ws(reconnect_url)
        self.run()

    def _on_message(self, ws: websocket.WebSocket, message: str) -> None:
        json_data = json.loads(message)

        if "metadata" not in json_data or "payload" not in json_data:
            LOG.warning(
                f"Twitch sent a message without `metadata` or `payload`: {json_data}"
            )
            return

        from twitch.message import MessageTypes

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

    @property
    def connected(self) -> bool:
        return self._connected

    @connected.setter
    def connected(self, con: bool) -> None:
        self._connected = con
