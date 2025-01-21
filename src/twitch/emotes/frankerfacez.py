from typing import Any
import requests
import constants
from twitch.emotes.emotes import Emote, EmotePlatform


class FrankerFaceZChannel(EmotePlatform):
    def load_emotes(self):
        """Loads all emotes from FrankerFaceZ's user channel

        Returns:
            dict[str, Emote]: The emotes loaded
        """

        resp = requests.get(f"{constants.FRANKERFACEZ_ROOM}/{self._channel_id}")
        resp.raise_for_status()

        sets = resp.json()["sets"]

        emotes = {}
        for _, set in sets.items():
            emotes |= self._load_set(set)

        return emotes

    def _load_set(self, data: dict[str, Any]) -> dict[str, Emote]:
        """Loads an emote set provided by FrankerFaceZ

        Args:
            data (dict[str, Any]): The data given to us by FFZ

        Returns:
            dict[str, Emote]: The emotes loaded from the set
        """

        emotes = {}
        for emote in data["emoticons"]:
            name = emote["name"]
            sizes = [s for s in emote["urls"].keys()]
            cdn = "/".join(emote["urls"][sizes[0]].split("/")[:-1])

            emotes[name] = Emote(name, cdn, sizes)

        return emotes


class FrankerFaceZGlobal(FrankerFaceZChannel):
    def load_emotes(self):

        resp = requests.get(constants.FRANKERFACEZ_GLOBAL)
        resp.raise_for_status()

        sets = resp.json()["sets"]

        emotes = {}
        for _, set in sets.items():
            emotes |= self._load_set(set)

        return emotes
