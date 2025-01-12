from typing import Optional

from singleton import singleton
from twitch.emotes.emotes import EmoteManager


@singleton
class Credentials:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._session_id: Optional[str] = None
        self._emote_manager: Optional[EmoteManager] = None

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    @access_token.setter
    def access_token(self, token: str) -> None:
        self._access_token = token

    @property
    def session_id(self) -> Optional[str]:
        return self._session_id

    @session_id.setter
    def session_id(self, id: str) -> None:
        self._session_id = id

    @property
    def emote_manager(self) -> Optional[EmoteManager]:
        return self._emote_manager

    @emote_manager.setter
    def emote_manager(self, manager: EmoteManager) -> None:
        self._emote_manager = manager
