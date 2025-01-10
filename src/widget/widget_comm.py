import asyncio
import json
import socket
from threading import Thread
import time
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
)

import constants
from log import LOG


class CommServer:
    CONNECTIONS: "set[CommServer]" = set()
    SEND_QUEUE: list[str] = []

    @staticmethod
    def recv_thread() -> None:
        asyncio.run(CommServer._recv_thread())

    @staticmethod
    async def _recv_thread() -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", constants.HTTP_PORT + 1))
        srv.listen(1)
        LOG.info(
            f"WebSocket server running on ws://localhost:{constants.HTTP_PORT + 1}/"
        )

        while True:
            sock, addr = srv.accept()
            Thread(target=CommServer.handle, args=(sock, addr)).start()

    @staticmethod
    def send_thread() -> None:
        while True:
            time.sleep(0.1)
            if len(CommServer.SEND_QUEUE) > 0:
                data_msg = CommServer.SEND_QUEUE.pop(0)

                for connection in CommServer.CONNECTIONS:
                    connection.send(data_msg)

    @staticmethod
    def broadcast(message: dict[str, Any]) -> None:
        data_msg = json.dumps(message)
        CommServer.SEND_QUEUE.append(data_msg)

    @staticmethod
    def handle(sock: socket.socket, peername: tuple[str, int]) -> None:
        LOG.info(f"New connection from {peername}")

        conn = WSConnection(ConnectionType.SERVER)
        obj = CommServer(conn, sock)
        CommServer.CONNECTIONS.add(obj)

        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break

                conn.receive_data(data)

                for event in conn.events():
                    if isinstance(event, CloseConnection):
                        LOG.info(f"Connection closed by {peername}")
                        return
                    elif isinstance(event, TextMessage):
                        LOG.info(f"Received message from {peername}: {event.data}")
                        # TODO write message to config
                    elif isinstance(event, Ping):
                        sock.sendall(conn.send(Pong(event.payload)))
                    elif isinstance(event, Request):
                        sock.sendall(conn.send(AcceptConnection()))
        finally:
            LOG.info(f"Cleaning up connection from {peername}")
            CommServer.CONNECTIONS.remove(obj)
            sock.close()

    def __init__(self, conn: WSConnection, sock: socket.socket):
        self._conn = conn
        self._sock = sock

    def send(self, message: str) -> None:
        self._sock.sendall(self._conn.send(TextMessage(message)))
