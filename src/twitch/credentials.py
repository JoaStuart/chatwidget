from typing import Optional

from singleton import singleton


@singleton
class Credentials:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._session_id: Optional[str] = None

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
