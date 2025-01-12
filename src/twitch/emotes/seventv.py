from typing import Any
import requests
import constants
from twitch.emotes.emotes import Emote, EmotePlatform


class SevenTVChannel(EmotePlatform):
    def load_emotes(self):
        resp = requests.post(
            constants.SEVENTV_GQL,
            json={"query": constants.SEVENTV_QUERY.replace("{{ID}}", self._channel_id)},
        )
        resp.raise_for_status()

        data = resp.json()

        emote_sets = data["data"]["userByConnection"]["emote_sets"]

        emotes = {}

        for e in emote_sets:
            emotes |= self._load_emote_set(e)

        return emotes

    def _load_emote_set(self, emote_set: dict[str, Any]) -> dict[str, Emote]:
        emotes = {}

        for emote in emote_set["emotes"]:
            host = emote["data"]["host"]
            name = emote["name"]

            em_obj = Emote(name, host["url"], [f["name"] for f in host["files"]])
            emotes[name] = em_obj

        return emotes


class SevenTVGlobal(SevenTVChannel):
    def load_emotes(self):
        resp = requests.post(
            constants.SEVENTV_GQL, json={"query": constants.SEVENTV_GLOBAL}
        )
        resp.raise_for_status()

        data = resp.json()
        emote_set = data["data"]["emoteSet"]

        return self._load_emote_set(emote_set)
