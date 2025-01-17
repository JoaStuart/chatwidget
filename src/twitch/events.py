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
        """
        Returns:
            str: The ID of the registered event
        """

        return self._id

    @abc.abstractmethod
    def _register(self) -> dict[str, Any]:
        """Abstract method creating the data to register this event with

        Returns:
            dict[str, Any]: The data to send to Twitch
        """

        pass

    @abc.abstractmethod
    def trigger(self, event: dict[str, Any]) -> None:
        """Abstract method which gets triggered when the event happens

        Args:
            event (dict[str, Any]): The data given to us through this event
        """

        pass

    def register_event(self) -> None:
        """Registers the current event"""

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
        """Deletes the current event"""

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
        """Creates an emote manager for the currently selected broadcaster

        Args:
            broadcaster_id (str): The ID of the broadcaster
        """

        Credentials().emote_manager = EmoteManager(broadcaster_id)

    def _register(self):
        """Creating the data to register this event with

        Returns:
            dict[str, Any]: The data to send to Twitch
        """

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
                "user_id": user_id if Config()["different_user"] else broadcaster_id,
            },
        }

    def trigger(self, event: dict[str, Any]) -> None:
        """Gets triggered when the event happens

        Args:
            event (dict[str, Any]): The data given to us through this event
        """

        ComboManager().read(event["message"]["text"], event["message"]["fragments"])


class EventTypes(Enum):
    CHAT_READ_EVENT = ChatReadEvent()

    @staticmethod
    def register_all() -> None:
        """Registers all known events"""

        for _, val in EventTypes._member_map_.items():
            val.value.register_event()

    @staticmethod
    def delete_all() -> None:
        """Deletes all known events"""

        for _, val in EventTypes._member_map_.items():
            val.value.delete_event()

    @staticmethod
    def trigger(id: str, event: dict[str, Any]) -> None:
        """Triggers an event by ID

        Args:
            id (str): The ID of the event to trigger
            event (dict[str, Any]): The event data to pass along
        """

        for _, cls in EventTypes._member_map_.items():
            evt: TwitchEvent = cls.value

            if evt.id == id:
                evt.trigger(event)

    @staticmethod
    def re_register() -> None:
        """Re-registers all known events"""

        EventTypes.delete_all()
        EventTypes.register_all()


# Makes the config re-register events when important config values change
cfg = Config()
cfg.add_change_callback("broadcaster_id", EventTypes.re_register)
cfg.add_change_callback("different_user", EventTypes.re_register)
cfg.add_change_callback("user_id", EventTypes.re_register)
