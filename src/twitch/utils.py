import requests

import constants
from twitch.credentials import Credentials


class TwitchUtils:
    @staticmethod
    def get_broadcaster_id(name: str) -> str:
        """Get the broascaster ID of a user by name

        Args:
            name (str): The name of the user to search for

        Returns:
            str: The ID of the given user
        """

        resp = requests.get(
            f"{constants.TWITCH_USERS}?login={name}",
            headers={
                "Authorization": f"Bearer {Credentials().access_token}",
                "Client-Id": constants.CLIENT_ID,
            },
        )
        resp.raise_for_status()

        data = resp.json()
        return data["data"][0]["id"]
