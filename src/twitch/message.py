import abc
from enum import Enum
from typing import Any, Type

import constants
from log import LOG
from twitch.events import EventTypes


class TwitchMessage(abc.ABC):
    def __init__(self, json_data: dict[str, Any]):
        self._data = json_data

    @abc.abstractmethod
    def message_id(self) -> str:
        pass

    @abc.abstractmethod
    def handle(self) -> None:
        pass


class TwitchMessageWelcome(TwitchMessage):
    def message_id(self):
        return "session_welcome"

    def handle(self):
        constants.CREDENTIALS.session_id = self._data["payload"]["session"]["id"]

        EventTypes.register_all()


class TwitchMessageKeepAlive(TwitchMessage):
    def message_id(self):
        return "session_keepalive"

    def handle(self):
        return


class TwitchMessageNotification(TwitchMessage):
    def message_id(self):
        return "notification"

    def handle(self):
        payload = self._data["payload"]
        subscription_id = payload["subscription"]["id"]

        EventTypes.trigger(subscription_id, payload["event"])


class MessageTypes(Enum):
    MESSAGE_WELCOME = TwitchMessageWelcome
    MESSAGE_KEEP_ALIVE = TwitchMessageKeepAlive
    MESSAGE_NOTIFICATION = TwitchMessageNotification

    def __init__(self, msg_cls: Type[TwitchMessage]):
        self._msg_cls = msg_cls

    def for_data(self, json_data: dict[str, Any]) -> TwitchMessage:
        return self._msg_cls(json_data)

    @staticmethod
    def handle(json_data: dict[str, Any]) -> None:
        msg_type = json_data["metadata"]["message_type"]

        for _, cls in MessageTypes._member_map_.items():
            inst: TwitchMessage = cls.value(json_data)
            if inst.message_id() == msg_type:
                inst.handle()
                break
        else:
            LOG.warning(f"Could not find handler for {json_data}")
