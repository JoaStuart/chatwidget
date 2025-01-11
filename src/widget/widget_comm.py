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
from widget.config import Config


class CommServer:
    CONNECTIONS: "set[CommServer]" = set()
    SEND_QUEUE: list[str] = []

    @staticmethod
    def recv_thread() -> None:
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
        data_msg = json.dumps(message)
        for connection in CommServer.CONNECTIONS:
            connection.send(data_msg)

    def __init__(self, conn: WSConnection, sock: socket.socket):
        self._conn = conn
        self._sock = sock

    def send(self, message: str) -> None:
        self._sock.sendall(self._conn.send(TextMessage(message)))

    def handle(self, peername: tuple[str, int]) -> None:
        LOG.info(f"WebSocket incoming from {peername}")

        try:
            self._read(peername)
        finally:
            LOG.info(f"WebSocket cleanup for {peername}")
            CommServer.CONNECTIONS.remove(self)
            self._sock.close()

    def _read(self, peername: tuple[str, int]) -> None:
        while True:
            data = self._sock.recv(4096)
            if not data:
                break

            self._conn.receive_data(data)

            for event in self._conn.events():
                if isinstance(event, CloseConnection):
                    LOG.info(f"Connection closed by {peername}")
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
                    )

    def _recv_msg(self, evt: TextMessage) -> None:
        try:
            data = json.loads(evt.data)
            event = data["event"]

            if event == "config_set":
                key = data["data"]["key"]
                val = data["data"]["value"]
                Config()[key] = val

        except Exception:
            pass

    def _send_event(self, *event: Event) -> None:
        for e in event:
            data = self._conn.send(e)
            self._sock.sendall(data)
