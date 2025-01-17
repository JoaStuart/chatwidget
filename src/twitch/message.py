import abc
from enum import Enum
from typing import Any, Type

from log import LOG
from twitch.credentials import Credentials
from twitch.events import EventTypes
from twitch.twitch import TwitchConn


class TwitchMessage(abc.ABC):
    def __init__(self, json_data: dict[str, Any]):
        self._data = json_data

    @abc.abstractmethod
    def message_id(self) -> str:
        """
        Returns:
            str: The ID of the message
        """

        pass

    @abc.abstractmethod
    def handle(self) -> None:
        """Abstract method called when receiving the current message"""

        pass


class TwitchMessageWelcome(TwitchMessage):
    def message_id(self):
        """
        Returns:
            str: The ID of the message
        """

        return "session_welcome"

    def handle(self):
        """Method called when receiving the current message"""

        Credentials().session_id = self._data["payload"]["session"]["id"]

        EventTypes.register_all()


class TwitchMessageKeepAlive(TwitchMessage):
    def message_id(self):
        """
        Returns:
            str: The ID of the message
        """

        return "session_keepalive"

    def handle(self):
        """Method called when receiving the current message"""

        pass  # At this point we dont care about keepalive messages yet


class TwitchMessageNotification(TwitchMessage):
    def message_id(self):
        """
        Returns:
            str: The ID of the message
        """

        return "notification"

    def handle(self):
        """Method called when receiving the current message"""

        payload = self._data["payload"]
        subscription_id = payload["subscription"]["id"]

        EventTypes.trigger(subscription_id, payload["event"])


class TwitchMessageReconnect(TwitchMessage):
    def message_id(self):
        """
        Returns:
            str: The ID of the message
        """

        return "session_reconnect"

    def handle(self):
        """Method called when receiving the current message"""

        reconnect_url = self._data["payload"]["session"]["reconnect_url"]

        TwitchConn().reconnect(reconnect_url)


class TwitchMessageRevocation(TwitchMessage):
    def message_id(self):
        """
        Returns:
            str: The ID of the message
        """

        return "revocation"

    def handle(self):
        """Method called when receiving the current message"""

        LOG.warning("The user has revoked the permissions!")

        TwitchConn().stop()


class MessageTypes(Enum):
    MESSAGE_WELCOME = TwitchMessageWelcome
    MESSAGE_KEEP_ALIVE = TwitchMessageKeepAlive
    MESSAGE_NOTIFICATION = TwitchMessageNotification
    MESSAGE_RECONNECT = TwitchMessageReconnect
    MESSAGE_REVOCATION = TwitchMessageRevocation

    def __init__(self, msg_cls: Type[TwitchMessage]):
        self._msg_cls = msg_cls

    def for_data(self, json_data: dict[str, Any]) -> TwitchMessage:
        """Creates the event handler for the given message data

        Args:
            json_data (dict[str, Any]): The data to create the event for

        Returns:
            TwitchMessage: The constructed message handler
        """

        return self._msg_cls(json_data)

    @staticmethod
    def handle(json_data: dict[str, Any]) -> None:
        """Handles a message given in JSON format by Twitch

        Args:
            json_data (dict[str, Any]): The data of the message
        """

        msg_type = json_data["metadata"]["message_type"]

        for _, cls in MessageTypes._member_map_.items():
            inst: TwitchMessage = cls.value(json_data)
            if inst.message_id() == msg_type:
                inst.handle()
                break
        else:
            LOG.warning(f"Could not find handler for {json_data}")
