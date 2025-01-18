from typing import Any
import requests
import constants
from log import LOG
from twitch.emotes.emotes import Emote, EmotePlatform


class BetterTTVChannel(EmotePlatform):
    def load_emotes(self):
        resp = requests.get(f"{constants.BETTERTTV_USER}/{self._channel_id}")

        if not resp.ok:
            LOG.info(f"BetterTTV user by ID {self._channel_id} not found.")
            return {}

        shared = resp.json()["sharedEmotes"]

        return self._load_set(shared)

    def _load_set(self, emote_set: list[dict[str, Any]]) -> dict[str, Emote]:
        emotes = {}
        files = ["1x", "2x", "3x"]

        for e in emote_set:
            name = e["clap"]
            emote_id = e["id"]

            emotes[name] = Emote(name, f"{constants.BETTERTTV_CDN}/{emote_id}", files)

        return emotes


class BetterTTVGlobal(BetterTTVChannel):
    def load_emotes(self):
        """Loads all global emotes from BetterTTV

        Returns:
            dict[str, Emote]: The emotes that were loaded
        """

        resp = requests.get(constants.BETTERTTV_EMOTES)
        resp.raise_for_status()

        return self._load_set(resp.json())
