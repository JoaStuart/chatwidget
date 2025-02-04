import json
import socket
from threading import Thread
from typing import Any
from wsproto import WSConnection
from wsproto.connection import ConnectionType
from wsproto.events import (
    TextMessage,
    CloseConnection,
    Ping,
    Pong,
    Request,
    AcceptConnection,
    Event,
)

import constants
from log import LOG
from twitch.credentials import Credentials
from twitch.twitch import TwitchConn
from widget.config import Config


class CommServer:
    CONNECTIONS: "set[CommServer]" = set()
    SEND_QUEUE: list[str] = []

    @staticmethod
    def recv_thread() -> None:
        """Starts the receive thread for the communication server"""

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", constants.HTTP_PORT + 1))
        srv.listen(1)
        LOG.info(
            f"WebSocket server running on ws://localhost:{constants.HTTP_PORT + 1}/"
        )

        while True:
            sock, addr = srv.accept()

            conn = WSConnection(ConnectionType.SERVER)
            obj = CommServer(conn, sock)
            CommServer.CONNECTIONS.add(obj)

            Thread(
                target=obj.handle, args=(addr,), name="CommsConnection", daemon=True
            ).start()

    @staticmethod
    def broadcast(message: dict[str, Any]) -> None:
        """Broadcasts the given message to all connected WebSockets

        Args:
            message (dict[str, Any]): The message to broadcast
        """

        data_msg = json.dumps(message)
        for connection in CommServer.CONNECTIONS:
            connection.send(data_msg)

    @staticmethod
    def close_all() -> None:
        """Closes all open connections"""

        for connection in CommServer.CONNECTIONS:
            connection.close()

    def __init__(self, conn: WSConnection, sock: socket.socket):
        self._conn = conn
        self._sock = sock
        self._closing: bool = False

    def send(self, message: str) -> None:
        """Sends a message to the current WebSocket

        Args:
            message (str): The message to send
        """

        self._sock.sendall(self._conn.send(TextMessage(message)))

    def handle(self, peername: tuple[str, int]) -> None:
        """Handles the current WebSocket connection

        Args:
            peername (tuple[str, int]): The peername the connection comes from
        """

        LOG.info(f"WebSocket incoming from {peername}")

        try:
            self._read()
        finally:
            LOG.info(f"WebSocket closed for {peername}")
            CommServer.CONNECTIONS.remove(self)
            self._sock.close()

    def close(self) -> None:
        """Closes the current connection"""

        self._send_event(CloseConnection(1000, "Closing connection."))
        self._closing = True

    def _read(self) -> None:
        """Reads data from the WebSocket and handles it"""

        while True:
            data = self._sock.recv(4096)
            if not data:
                break

            self._conn.receive_data(data)

            for event in self._conn.events():
                if isinstance(event, CloseConnection):
                    if not self._closing:
                        self._send_event(CloseConnection(event.code, event.reason))
                    self._sock.close()
                    return

                elif isinstance(event, TextMessage):
                    self._recv_msg(event)

                elif isinstance(event, Ping):
                    self._send_event(Pong(event.payload))

                elif isinstance(event, Request):
                    self._send_event(
                        AcceptConnection(),
                        TextMessage(
                            json.dumps({"event": "config", "data": Config().dump()})
                        ),
                        TextMessage(
                            json.dumps(
                                {
                                    "event": "connect",
                                    "data": {"connected": TwitchConn().connected},
                                }
                            )
                        ),
                    )

    def _recv_msg(self, evt: TextMessage) -> None:
        """Callback for receiving text messages

        Args:
            evt (TextMessage): The message received
        """

        try:
            data = json.loads(evt.data)
            event = data["event"]

            if event == "config_set":
                key = data["data"]["key"]
                val = data["data"]["value"]
                Config()[key] = val

            elif event == "config_reset":
                cfg = Config()
                cfg.reset_all()

            elif event == "shutdown":
                Credentials().shutdown.set()

        except Exception:
            pass

    def _send_event(self, *event: Event) -> None:
        """Sends an event to the current WebSocket"""

        for e in event:
            data = self._conn.send(e)
            self._sock.sendall(data)
