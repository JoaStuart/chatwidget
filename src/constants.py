import os
from twitch.credentials import Credentials


HTTP_PORT = 4150
FALLBACK_MIME = "application/octet-stream"

SRC_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(SRC_DIR, "..")
WEB_DIR = os.path.join(ROOT_DIR, "web")

TWITCH_ENDPOINT = "wss://eventsub.wss.twitch.tv/ws"
TWITCH_EVENTSUB = "https://api.twitch.tv/helix/eventsub/subscriptions"
AUTH_REDIR = f"http://localhost:{HTTP_PORT}/authorized"
CLIENT_ID = "r5bu82amizik5m2iiytwi3o49wdm0f"
SCOPE = "user:read:chat"

CREDENTIALS = Credentials()

BROADCASTER_ID = "SomeID"  # TODO put into config
