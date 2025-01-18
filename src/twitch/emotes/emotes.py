import abc
from typing import Any, Type

import constants


class Emote:
    def __init__(self, name: str, cdn: str, files: list[str]):
        self._name = name
        self._cdn = cdn
        self._files = files

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the emote
        """

        return self._name

    @property
    def cdn(self) -> str:
        """
        Returns:
            str: The CDN this emote resides on
        """

        return self._cdn

    @property
    def files(self) -> list[str]:
        """
        Returns:
            list[str]: The different types (sizes) this cdn offers
        """

        return self._files

    def url(self, size: int) -> str:
        """Creates a CDN url from the requested size

        Args:
            size (int): The size of the emote to request

        Raises:
            ValueError: When no emote with the given size could be found

        Returns:
            str: The url where to download the emote
        """

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
        """
        Returns:
            list[Type[EmotePlatform]]: A list of all platforms we can get emotes from
        """

        from twitch.emotes.seventv import SevenTVChannel, SevenTVGlobal
        from twitch.emotes.betterttv import BetterTTVChannel, BetterTTVGlobal
        from twitch.emotes.frankerfacez import FrankerFaceZChannel, FrankerFaceZGlobal

        return [
            # Global emotes
            SevenTVGlobal,
            BetterTTVGlobal,
            FrankerFaceZGlobal,
            # Channel emotes
            SevenTVChannel,
            BetterTTVChannel,
            FrankerFaceZChannel,
        ]

    def __init__(self, channel_id: str):
        self._channel_id = channel_id
        self._emotes = self._load_emotes()

    def _load_emotes(self) -> dict[str, Emote]:
        """Loads all emotes from all registered platforms

        Returns:
            dict[str, Emote]: The emotes loaded
        """

        emotes = {}

        for p in self.platforms():
            emotes |= p(self._channel_id).load_emotes()

        return emotes

    def _make_text_frag(
        self, emote_string: list[dict[str, str]], text_buffer: list[str]
    ) -> None:
        """Creates a text fragment from the contents of the text buffer and writes it into the emote string buffer

        Args:
            emote_string (list[dict[str, str]]): The emote string buffer to write to
            text_buffer (list[str]): The text buffer to read the text from
        """

        emote_string.append(
            {
                "type": "text",
                "value": " ".join(text_buffer),
            }
        )
        text_buffer.clear()

    def make_emote_string(
        self, fragments: list[dict[str, Any]]
    ) -> list[dict[str, str]]:
        """Generates an emote string from the fragments twitch provided us

        Args:
            fragments (list[dict[str, Any]]): The fragments from Twitch

        Returns:
            list[dict[str, str]]: The emote string to send to the widget
        """

        emote_string = []

        for f in fragments:
            if f["type"] != "emote":
                emote_string.append(self._emote_str_part(f["text"]))
                continue

            emote_id = f["emote"]["id"]

            link = (
                constants.TWITCH_EMOTE_CDN.replace("{{ID}}", emote_id)
                .replace("{{FORMAT}}", "default")
                .replace("{{SCHEME}}", "light")
                .replace("{{SIZE}}", "3.0")
            )
            emote_string.append(
                {
                    "type": "emote",
                    "text": f["text"],
                    "value": link,
                }
            )

        return emote_string

    def _emote_str_part(self, text: str) -> list[dict[str, str]]:
        """Generates an emote string from a text sequence

        Args:
            text (str): The text sequence potentially containing 3rd party emotes

        Returns:
            list[dict[str, str]]: The emote string constructed from the input text
        """

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
        """Loads all emotes from the current platform

        Returns:
            dict[str, Emote]: The loaded emotes
        """

        pass
