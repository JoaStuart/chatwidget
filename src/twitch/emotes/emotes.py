import abc
from typing import Type


class Emote:
    def __init__(self, name: str, cdn: str, files: list[str]):
        self._name = name
        self._cdn = cdn
        self._files = files

    @property
    def name(self) -> str:
        return self._name

    @property
    def cdn(self) -> str:
        return self._cdn

    @property
    def files(self) -> list[str]:
        return self._files

    def url(self, size: int) -> str:
        f = None
        for file in self._files:
            if file.startswith(str(size)):
                f = file
                break
        else:
            raise ValueError(f"No {self.name} emote with size {size} found!")

        return f"{self.cdn}/{f}"


class EmoteManager(abc.ABC):
    @staticmethod
    def platforms() -> "list[Type[EmotePlatform]]":
        from twitch.emotes.seventv import SevenTVChannel, SevenTVGlobal
        from twitch.emotes.betterttv import BetterTTVGlobal
        from twitch.emotes.twitch import TwitchTVChannel, TwitchTVGlobal
        from twitch.emotes.frankerfacez import FrankerFaceZChannel

        return [
            # Global emotes
            SevenTVGlobal,
            BetterTTVGlobal,
            TwitchTVGlobal,
            # Channel emotes
            SevenTVChannel,
            FrankerFaceZChannel,
            TwitchTVChannel,
        ]

    def __init__(self, channel_id: str):
        self._channel_id = channel_id
        self._emotes = self._load_emotes()

    def _load_emotes(self) -> dict[str, Emote]:
        emotes = {}

        for p in self.platforms():
            emotes |= p(self._channel_id).load_emotes()

        return emotes

    def _make_text_frag(
        self, emote_string: list[dict[str, str]], text_buffer: list[str]
    ) -> None:
        emote_string.append(
            {
                "type": "text",
                "value": " ".join(text_buffer),
            }
        )
        text_buffer.clear()

    def make_emote_string(self, text: str) -> list[dict[str, str]]:
        emote_string = []

        text_buffer = []
        words = text.split(" ")

        for w in words:
            emote = self._emotes.get(w, None)

            if emote is None:
                text_buffer.append(w)
                continue

            if len(text_buffer) > 0:
                self._make_text_frag(emote_string, text_buffer)

            emote_string.append(
                {
                    "type": "emote",
                    "text": w,
                    "value": f"{emote.cdn}/{emote.files[-1]}",
                }
            )

        if len(text_buffer) > 0:
            self._make_text_frag(emote_string, text_buffer)

        return emote_string


class EmotePlatform(abc.ABC):
    def __init__(self, channel_id: str):
        self._channel_id = channel_id

    @abc.abstractmethod
    def load_emotes(self) -> dict[str, Emote]:
        pass
