import os
import sys


# HTTP server
HTTP_PORT = 4150
FALLBACK_MIME = "application/octet-stream"

# Folders
if getattr(sys, "frozen", False):
    ROOT_DIR = sys._MEIPASS
    WEB_DIR = os.path.join(ROOT_DIR, "web")
else:
    _SRC_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.join(_SRC_DIR, "..")
    WEB_DIR = os.path.join(ROOT_DIR, "web")

# Twitch API endpoints
TWITCH_ENDPOINT = "wss://eventsub.wss.twitch.tv/ws"
TWITCH_EVENTSUB = "https://api.twitch.tv/helix/eventsub/subscriptions"
TWTICH_EMOTES = "https://api.twitch.tv/helix/chat/emotes"
TWITCH_USERS = "https://api.twitch.tv/helix/users"
TWITCH_EMOTE_CDN = (
    "https://static-cdn.jtvnw.net/emoticons/v2/{{ID}}/{{FORMAT}}/{{SCHEME}}/{{SIZE}}"
)

# Constants to replace inside the OAuth URL
AUTH_REDIR = f"http://localhost:{HTTP_PORT}/authorized"
CLIENT_ID = "r5bu82amizik5m2iiytwi3o49wdm0f"
SCOPE = "user:read:chat"

# SevenTV endpoint and GQL queries
SEVENTV_GQL = "https://7tv.io/v3/gql"
SEVENTV_EMOTE_FORMAT = "WEBP"
SEVENTV_QUERY = (
    """query {
  userByConnection(platform: "TWITCH", id: "{{ID}}") {
    emote_sets {
      emotes {
        name
        data {
          host {
            url
            files(formats: \""""
    + SEVENTV_EMOTE_FORMAT
    + """\") {
              name
              format
            }
          }
        }
      }
    }
  }
}"""
)
SEVENTV_GLOBAL = (
    """query {
  emoteSet(id: "01HKQT8EWR000ESSWF3625XCS4") {
    emotes {
      name
      data {
        host {
          url
          files(formats: \""""
    + SEVENTV_EMOTE_FORMAT
    + """\") {
            name
            format
          }
        }
      }
    }
  }
}"""
)

# BetterTTV endpoints
BETTERTTV_EMOTES = "https://api.betterttv.net/3/cached/emotes/global"
BETTERTTV_USER = "https://api.betterttv.net/3/cached/users/twitch"
BETTERTTV_CDN = "https://cdn.betterttv.net/emote"

# FFZ user endpoint
FRANKERFACEZ_ROOM = "https://api.frankerfacez.com/v1/room/id"
FRANKERFACEZ_GLOBAL = "https://api.frankerfacez.com/v1/set/global"
