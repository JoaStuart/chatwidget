import abc
from enum import Enum
from tkinter import EventType
from typing import Any, Optional

import requests

from src import constants


class TwitchEvent(abc.ABC):
    def __init__(self):
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        return self._id

    @abc.abstractmethod
    def _register(self) -> dict[str, Any]:
        pass

    @abc.abstractmethod
    def trigger(self, event: dict[str, Any]) -> None:
        pass

    def register_event(self) -> None:
        register_data = self._register() | {
            "transport": {
                "method": "websocket",
                "session_id": constants.CREDENTIALS.session_id,
            }
        }

        req = requests.post(
            constants.TWITCH_EVENTSUB,
            headers={
                "Authorization": f"Bearer {constants.CREDENTIALS.access_token}",
                "Client-Id": constants.CLIENT_ID,
                "Content-Type": "application/json",
            },
            json=register_data,
        )

        req.raise_for_status()

        body = req.json()

        sub_data = body["data"][0]

        if sub_data & register_data != register_data:
            raise ValueError(f"Twitch did not subscribe to the right topic: {body}")

        self._id = body["data"][0]["id"]

    def delete_event(self) -> None:
        if self._id is None:
            return

        requests.delete(
            f"{constants.TWITCH_EVENTSUB}?id={self._id}",
            headers={
                "Authorization": f"Bearer {constants.CREDENTIALS.access_token}",
                "Client-Id": constants.CLIENT_ID,
            },
        )


class ChatReadEvent(TwitchEvent):
    def _register(self):
        return {
            "type": "channel.chat.message",
            "version": "1",
            "condition": {
                "broadcaster_user_id": constants.BROADCASTER_ID,
                "user_id": constants.BROADCASTER_ID,
            },
        }

    def trigger(self, event: dict[str, Any]) -> None:
        pass  # TODO Handle chat message


class EventTypes(Enum):
    CHAT_READ_EVENT = ChatReadEvent()

    @staticmethod
    def register_all() -> None:
        for _, val in EventTypes._member_map_.items():
            val.value.register_event()

    @staticmethod
    def delete_all() -> None:
        for _, val in EventType._member_map_.items():
            val.value.delete_event()

    @staticmethod
    def trigger(id: str, event: dict[str, Any]) -> None:
        for _, val in EventType._member_map_.items():
            evt: TwitchEvent = val.value
            if evt.id == id:
                evt.trigger(event)
