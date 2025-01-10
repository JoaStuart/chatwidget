from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
import os
from threading import Thread
from typing import Optional
from urllib.parse import quote

from itsdangerous import NoneAlgorithm

import constants
from log import LOG
from twitch.twitch import TwitchConn


class HTTPHandler(BaseHTTPRequestHandler):
    @staticmethod
    def start_server() -> None:
        with HTTPServer(("localhost", constants.HTTP_PORT), HTTPHandler) as httpd:
            LOG.info(f"Serving on http://localhost:{constants.HTTP_PORT}")
            httpd.serve_forever()

    def _parse_get_params(self, get_str: str) -> dict[str, str]:
        params = {}
        if get_str == None:
            return params

        for k in get_str.split("&"):
            if "=" in k:
                key, value = k.split("=", 1)
                params[key] = value
            else:
                params[k] = ""

        return params

    def _split_path(self) -> tuple[str, dict[str, str]]:
        path = self.path
        path = path.split("?", 1)
        if len(path) == 2:
            params = self._parse_get_params(path[1])
            path = path[0]
        else:
            params = {}
            path = path[0]

        return path, params

    def _send_page(
        self, page_name: str, replacements: dict[bytes | str, bytes | str] = {}
    ) -> None:
        path = os.path.join(constants.WEB_DIR, page_name)

        if not os.path.isfile(path):
            self.send_error(
                404,
                "Not Found",
                "The requested page could not be found! Make sure you cloned the repo correctly. ._.",
            )
            return

        self.send_response(200, "OK")
        self.send_header(
            "Content-Type",
            mimetypes.guess_type(page_name)[0] or constants.FALLBACK_MIME,
        )
        self.end_headers()

        with open(path, "rb") as rf:
            data = rf.read()

        for key, replace in replacements.items():
            if isinstance(key, str):
                key = key.encode()

            if isinstance(replace, str):
                replace = replace.encode()

            data = data.replace(key, replace)

        self.wfile.write(data)

    def _authorized(self, params: dict[str, str]) -> None:
        if len(params) == 0:
            self._send_page("authorize_frag.html")
            return

        access_token = params.get("access_token", None)

        if access_token is None:
            LOG.info(
                f"Could not authorize: `{params.get("error_description", "No message")}`"
            )

            self.send_response(302, "Not authorized")
            self.send_header("Location", "/")
            self.end_headers()
            return

        constants.CREDENTIALS.access_token = access_token

        Thread(target=TwitchConn, daemon=True).start()
        # TODO: Send out event for control panel

        self._send_page("authorized.html")

    def do_GET(self):
        path, params = self._split_path()

        match path:
            case "/":
                self._send_page(
                    "index.html",
                    {
                        "{{CLIENT_ID}}": quote(constants.CLIENT_ID),
                        "{{REDIRECT_URI}}": quote(constants.AUTH_REDIR),
                        "{{SCOPE}}": quote(constants.SCOPE),
                    },
                )
            case "/authorized":
                self._authorized(params)
            case "/widget":
                self._send_page("widget.html")
            case "/widget.js":
                self._send_page("widget.js")
            case "/widget.css":
                self._send_page("widget.css")
            case "/tiny5.ttf":
                self._send_page("tiny5/Tiny5.ttf")

            case _:
                self.send_error(404, "Not Found", "This page could not be found! :(")
