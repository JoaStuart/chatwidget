from typing import Any
import requests
import constants
from twitch.emotes.emotes import Emote, EmotePlatform


class FrankerFaceZChannel(EmotePlatform):
    def load_emotes(self):
        resp = requests.get(f"{constants.FRANKERFACEZ_ROOM}/{self._channel_id}")
        resp.raise_for_status()

        sets = resp.json()["sets"]

        emotes = {}
        for _, set in sets.items():
            emotes |= self._load_set(set)

        return emotes

    def _load_set(self, data: dict[str, Any]) -> dict[str, Emote]:
        emotes = {}
        for emote in data["emoticons"]:
            name = emote["name"]
            sizes = [s for s in emote["urls"].keys()]
            cdn = "/".join(emote["urls"][sizes[0]].split("/")[:-1])

            emotes[name] = Emote(name, cdn, sizes)

        return emotes
