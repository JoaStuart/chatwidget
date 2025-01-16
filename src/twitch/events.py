import abc
from enum import Enum
from threading import Thread
from typing import Any, Optional

import requests

from log import LOG
import constants
from twitch.credentials import Credentials
from twitch.emotes.emotes import EmoteManager
from twitch.utils import TwitchUtils
from widget.combo import ComboManager
from widget.config import Config


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
                "session_id": Credentials().session_id,
            }
        }

        req = requests.post(
            constants.TWITCH_EVENTSUB,
            headers={
                "Authorization": f"Bearer {Credentials().access_token}",
                "Client-Id": constants.CLIENT_ID,
                "Content-Type": "application/json",
            },
            json=register_data,
        )

        req.raise_for_status()

        body = req.json()
        sub_data = body["data"][0]

        self._id = sub_data["id"]

    def delete_event(self) -> None:
        if self._id is None:
            return

        requests.delete(
            f"{constants.TWITCH_EVENTSUB}?id={self._id}",
            headers={
                "Authorization": f"Bearer {Credentials().access_token}",
                "Client-Id": constants.CLIENT_ID,
            },
        )


class ChatReadEvent(TwitchEvent):
    def _create_emote_manager(self, broadcaster_id: str) -> None:
        Credentials().emote_manager = EmoteManager(broadcaster_id)

    def _register(self):
        broadcaster_id = TwitchUtils.get_broadcaster_id(Config()["broadcaster_id"])
        user_id = TwitchUtils.get_broadcaster_id(Config()["user_id"])

        Thread(
            target=self._create_emote_manager,
            args=(broadcaster_id,),
            name="EmoteLoader",
            daemon=True,
        ).start()

        return {
            "type": "channel.chat.message",
            "version": "1",
            "condition": {
                "broadcaster_user_id": broadcaster_id,
                "user_id": user_id or broadcaster_id,
            },
        }

    def trigger(self, event: dict[str, Any]) -> None:
        ComboManager().read(event["message"]["text"])


class EventTypes(Enum):
    CHAT_READ_EVENT = ChatReadEvent()

    @staticmethod
    def register_all() -> None:
        for _, val in EventTypes._member_map_.items():
            val.value.register_event()

    @staticmethod
    def delete_all() -> None:
        for _, val in EventTypes._member_map_.items():
            val.value.delete_event()

    @staticmethod
    def trigger(id: str, event: dict[str, Any]) -> None:
        for _, cls in EventTypes._member_map_.items():
            evt: TwitchEvent = cls.value

            if evt.id == id:
                evt.trigger(event)
