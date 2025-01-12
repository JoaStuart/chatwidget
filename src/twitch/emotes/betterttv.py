import requests
import constants
from twitch.emotes.emotes import Emote, EmotePlatform


class BetterTTVGlobal(EmotePlatform):
    def load_emotes(self):
        resp = requests.get(constants.BETTERTTV_EMOTES)
        resp.raise_for_status()

        emotes = {}

        for e in resp.json():
            name = e["code"]
            emote_id = e["id"]

            files = ["1x", "2x", "3x"]

            emotes[name] = Emote(
                name, f"https://cdn.betterttv.net/emote/{emote_id}", files
            )

        return emotes
