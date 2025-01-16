import re
import time

from singleton import singleton
from twitch.credentials import Credentials
from widget.config import Config
from widget.widget_comm import CommServer


@singleton
class ComboManager:
    def __init__(self):
        self._combos: list[ChatCombo] = []

    def read(self, message: str) -> None:
        if self._add_to_existing(message):
            return

        self._combos.append(ChatCombo(message))

    def _add_to_existing(self, message: str) -> bool:
        found = False

        for c in self._combos:
            if c.compare(message):
                c.add_entry()
                found = True

        return found

    def combo_thread(self) -> None:
        while True:
            time.sleep(0.5)
            cur_time = time.time()

            for c in self._combos.copy():
                if c.expires < cur_time:
                    c.remove_combo()
                    self._combos.remove(c)


class ChatCombo:
    ACTIVE_COMBOS = 0

    def __init__(self, text: str):
        self._text = text
        self._entries = 1
        self._expires = self._make_expiry()
        self._active = False

    def _make_expiry(self) -> float:
        return time.time() + Config()["combo_timeout"]

    def compare(self, message: str) -> bool:
        if " " in message:
            removal = [".", ",", "!", "?", ":"]
            c_str = self.text
            m_str = message
            for c in removal:
                c_str = c_str.replace(c, "")
                m_str = m_str.replace(c, "")

            return c_str.lower() == m_str.lower()
        else:
            return self.text.lower() == message.lower()

    def add_entry(self) -> None:
        self._entries += 1
        self._expires = self._make_expiry()

        if self._entries < Config()["combo_threshold"]:
            return

        if self._active:
            self._update_combo()
        else:
            self._activate()

    def _activate(self) -> None:
        if self.ACTIVE_COMBOS < Config()["max_combo"]:
            self._active = True
            self._create_combo()
            self.ACTIVE_COMBOS += 1

    def _create_combo(self) -> None:
        if Credentials().emote_manager is not None:
            emote_string = Credentials().emote_manager.make_emote_string(self.text)
        else:
            emote_string = [{"type": "text", "value": self.text}]

        CommServer.broadcast(
            {
                "event": "combo_create",
                "data": {
                    "type": "text",
                    "text": self.text,
                    "combo": self.entries,
                    "emote": emote_string,
                },
            }
        )

    def _update_combo(self) -> None:
        CommServer.broadcast(
            {
                "event": "combo_update",
                "data": {
                    "text": self.text,
                    "combo": self.entries,
                },
            }
        )

    def remove_combo(self) -> None:
        if not self._active:
            return

        CommServer.broadcast(
            {
                "event": "combo_remove",
                "data": {
                    "text": self.text,
                },
            }
        )

    @property
    def entries(self) -> int:
        return self._entries

    @property
    def expires(self) -> float:
        return self._expires

    @property
    def text(self) -> str:
        return self._text
