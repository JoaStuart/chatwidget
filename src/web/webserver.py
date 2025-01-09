from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
import os
from threading import Thread
from typing import Optional
from urllib.parse import urlencode

import constants
from log import LOG
from src.twitch.twitch import TwitchConn


class HTTPHandler(BaseHTTPRequestHandler):
    RUNNING_SERVER: Optional[HTTPServer] = None

    @staticmethod
    def start_server() -> None:
        if HTTPHandler.RUNNING_SERVER:
            raise ValueError("A server is already running!")

        with HTTPServer(("localhost", constants.HTTP_PORT), HTTPHandler) as httpd:
            LOG.info(f"Serving on http://localhost:{constants.HTTP_PORT}")
            httpd.serve_forever()

    @staticmethod
    def shutdown() -> None:
        if srv := HTTPHandler.RUNNING_SERVER:
            srv.shutdown()

    def _parse_get_params(self, get_str: str) -> dict[str, str]:
        params = {}

        for k in get_str.split("&"):
            if "=" in k:
                key, value = k.split("=", 1)
                params[key] = value
            else:
                params[k] = ""

        return params

    def _split_path(self) -> tuple[str, Optional[str], dict[str, str]]:
        path = self.path
        path = path.split("?", 1)
        if len(path) == 2:
            params = self._parse_get_params(path[1])
            path = path[0]
        else:
            params = {}
            path = path[0]

        path = path.split("#", 1)
        if len(path) == 2:
            path_hash = path[1]
            path = path[0]
        else:
            path_hash = None
            path = path[0]

        return path, path_hash, params

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

    def _authorized(self, path_hash: Optional[str], params: dict[str, str]) -> None:
        if path_hash is None or not path_hash.startswith("access_token="):
            LOG.info(
                f"Could not authorize: `{params.get("error_description", "No message")}`"
            )

            self.send_response(302, "Not authorized")
            self.send_header("Location", "/")

        constants.CREDENTIALS.access_token = path_hash.split("=", 1)[1]

        Thread(target=TwitchConn, daemon=True).start()
        # TODO: Send out event for control panel

        self._send_page("authorized.html")

    def do_GET(self):
        path, path_hash, params = self._split_path()

        match path:
            case "/":
                self._send_page(
                    "index.html",
                    {
                        "{{CLIENT_ID}}": urlencode(constants.CLIENT_ID),
                        "{{REDIRECT_URI}}": urlencode(constants.AUTH_REDIR),
                        "{{SCOPE}}": urlencode(constants.SCOPE),
                    },
                )
            case "/authorized":
                self._authorized(path_hash, params)

            case _:
                self.send_error(404, "Not Found", "This page could not be found! :(")
