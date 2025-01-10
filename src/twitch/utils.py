import requests

import constants


class TwitchUtils:
    @staticmethod
    def get_broadcaster_id(name: str) -> str:
        resp = requests.get(
            f"{constants.TWITCH_USERS}?login={name}",
            headers={
                "Authorization": f"Bearer {constants.CREDENTIALS.access_token}",
                "Client-Id": constants.CLIENT_ID,
            },
        )
        resp.raise_for_status()

        data = resp.json()
        return data["data"][0]["id"]
