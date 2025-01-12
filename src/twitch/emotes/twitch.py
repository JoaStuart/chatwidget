from typing import Any
import requests
import constants
from twitch.credentials import Credentials
from twitch.emotes.emotes import Emote, EmotePlatform


class TwitchTVChannel(EmotePlatform):
    def load_emotes(self):
        resp = requests.get(
            f"{constants.TWTICH_EMOTES}?broadcaster_id={self._channel_id}",
            headers={
                "Authorization": f"Bearer {Credentials().access_token}",
                "Client-Id": constants.CLIENT_ID,
            },
        )
        resp.raise_for_status()

        root = resp.json()

        return self._load_emoteset(root)

    def _load_emoteset(self, root: dict[str, Any]) -> dict[str, Emote]:
        data = root["data"]

        emotes = {}

        for e in data:
            name = e["name"]
            emote_id = e["id"]
            emote_format = "default"

            files = e["scale"]
            cdn = "/".join(root["template"].split("/")[:-1])

            emotes[name] = Emote(
                name,
                cdn.replace("{{id}}", emote_id)
                .replace("{{format}}", emote_format)
                .replace("{{theme_mode}}", "light"),
                files,
            )

        return emotes


class TwitchTVGlobal(TwitchTVChannel):
    def load_emotes(self):
        resp = requests.get(
            f"{constants.TWTICH_EMOTES}/global",
            headers={
                "Authorization": f"Bearer {Credentials().access_token}",
                "Client-Id": constants.CLIENT_ID,
            },
        )
        resp.raise_for_status()

        root = resp.json()

        return self._load_emoteset(root)
