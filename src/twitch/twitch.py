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
        """Creates the WebSocket for Twitch to callback with

        Args:
            url (str): The URL to connect this WebSocket to. Normally
                `constants.TWTICH_ENDPOINT`, but can be different for reconnecting

        Returns:
            websocket.WebSocketApp: The WebSocketApp created for the URL
        """

        return websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_ping=self._on_ping,
            on_close=self._on_close,
        )

    def run(self) -> None:
        """Runs the WebSocket message handler in a separate thread"""

        self._connected = True
        Thread(
            target=self._ws.run_forever, name="TwitchConnection", daemon=True
        ).start()

    def stop(self) -> None:
        """Stops the currently active handler and closes the WebSocketApp"""

        self._connected = False
        self._ws.close(status=1000, reason="Closing connection.")

    def reconnect(self, reconnect_url: str) -> None:
        """Reconnects the WebSocketApp using the provided URL

        Args:
            reconnect_url (str): The URL to reconnect to
        """

        self._ws.close()
        self._ws = self._make_ws(reconnect_url)
        self.run()

    def _on_message(self, ws: websocket.WebSocket, message: str) -> None:
        """The callback for receiving messages

        Args:
            ws (websocket.WebSocket): The socket receiving the message
            message (str): The message received
        """

        json_data = json.loads(message)

        if "metadata" not in json_data or "payload" not in json_data:
            LOG.warning(
                f"Twitch sent a message without `metadata` or `payload`: {json_data}"
            )
            return

        from twitch.message import MessageTypes

        MessageTypes.handle(json_data)

    def _on_ping(self, ws: websocket.WebSocketApp, message: Optional[bytes]) -> None:
        """The callback for receiving pings

        Args:
            ws (websocket.WebSocketApp): The socket receiving the message
            message (Optional[bytes]): The ping data to pong back
        """

        ws.sock.pong(message)

    def _on_close(
        self,
        _: websocket.WebSocket,
        close_status_code: Optional[int],
        close_msg: Optional[str],
    ) -> None:
        """The callback for when the WebSocket closes

        Args:
            _ (websocket.WebSocket): The WebSocket being closed
            close_status_code (Optional[int]): The status code for closing the connection
            close_msg (Optional[str]): The reason message received for closing
        """

        LOG.warning(
            f"Twitch closed WebSocket connection: ({close_status_code}) {close_msg}"
        )

    @property
    def connected(self) -> bool:
        """
        Returns:
            bool: Whether the WebSocket is currently connected
        """

        return self._connected

    @connected.setter
    def connected(self, con: bool) -> None:
        self._connected = con
