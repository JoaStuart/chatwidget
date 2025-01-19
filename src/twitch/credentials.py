from threading import Event
from typing import Optional

from singleton import singleton
from twitch.emotes.emotes import EmoteManager


@singleton
class Credentials:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._session_id: Optional[str] = None
        self._emote_manager: Optional[EmoteManager] = None
        self._shutdown = Event()

    @property
    def access_token(self) -> Optional[str]:
        """
        Returns:
            Optional[str]: The access token gotten from the OAuth
        """

        return self._access_token

    @access_token.setter
    def access_token(self, token: str) -> None:
        self._access_token = token

    @property
    def session_id(self) -> Optional[str]:
        """
        Returns:
            Optional[str]: The session ID of the current WebSocket connection
        """

        return self._session_id

    @session_id.setter
    def session_id(self, id: str) -> None:
        self._session_id = id

    @property
    def emote_manager(self) -> Optional[EmoteManager]:
        """
        Returns:
            Optional[EmoteManager]: The emote manager currently in use
        """

        return self._emote_manager

    @emote_manager.setter
    def emote_manager(self, manager: EmoteManager) -> None:
        self._emote_manager = manager

    @property
    def shutdown(self) -> Event:
        return self._shutdown
