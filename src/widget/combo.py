import time

import constants
from widget.widget_comm import CommServer


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


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
            if c.text.lower() in message.lower():
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
    def __init__(self, text: str):
        self._text = text
        self._entries = 1
        self._expires = self._make_expiry()

    def _make_expiry(self) -> float:
        return time.time() + constants.COMBO_TIMEOUT

    def add_entry(self) -> None:
        self._entries += 1
        self._expires = self._make_expiry()

        if self._entries < constants.COMBO_THRESHOLD:
            return

        if self._entries == constants.COMBO_THRESHOLD:
            self._create_combo()
            return

        self._update_combo()

    def _create_combo(self) -> None:
        CommServer.broadcast(
            {
                "event": "combo_create",
                "data": {
                    "type": "text",
                    "text": self.text,
                    "combo": self.entries,
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
        if self.entries < constants.COMBO_THRESHOLD:
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
