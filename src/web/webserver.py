from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import mimetypes
import os
from urllib.parse import quote

import constants
from log import LOG
from twitch.credentials import Credentials
from twitch.twitch import TwitchConn
from widget.widget_comm import CommServer


class HTTPHandler(BaseHTTPRequestHandler):
    @staticmethod
    def start_server() -> None:
        """Starts the HTTP server"""

        with ThreadingHTTPServer(
            ("localhost", constants.HTTP_PORT), HTTPHandler
        ) as httpd:
            LOG.info(f"Serving on http://localhost:{constants.HTTP_PORT}")
            httpd.serve_forever()

    def _parse_get_params(self, get_str: str) -> dict[str, str]:
        """Parses all get params given

        Args:
            get_str (str): The get parameters with the `?` stripped

        Returns:
            dict[str, str]: The arguments given
        """

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
        """Splits the path into path and get arguments

        Returns:
            tuple[str, dict[str, str]]: The path and get arguments
        """

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
        """Sends a static page with replaced variables

        Args:
            page_name (str): The name of the file inside the web folder
            replacements (dict[bytes  |  str, bytes  |  str], optional): The replacements to use. Defaults to {}.
        """

        path = os.path.join(constants.WEB_DIR, page_name)

        if not os.path.isfile(path):
            self.send_error(
                404,
                "Not Found",
                "The requested page could not be found! Make sure you cloned the repo correctly. ._.",
            )
            return

        with open(path, "rb") as rf:
            data = rf.read()

        for key, replace in replacements.items():
            if isinstance(key, str):
                key = key.encode()

            if isinstance(replace, str):
                replace = replace.encode()

            data = data.replace(key, replace)

        self.send_response(200, "OK")
        self.send_header(
            "Content-Type",
            mimetypes.guess_type(page_name)[0] or constants.FALLBACK_MIME,
        )
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()

        self.wfile.write(data)

    def _authorized(self, params: dict[str, str]) -> None:
        """The actions to be performed on an authorization callback

        Args:
            params (dict[str, str]): The get parameters given
        """

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

        Credentials().access_token = access_token

        TwitchConn().run()
        CommServer.broadcast(
            {
                "event": "connect",
                "data": {"connected": True},
            }
        )

        self._send_page("authorized.html")

    def do_GET(self):
        """Callback for GET requests"""

        path, params = self._split_path()

        PAGES: dict[str, tuple[str] | tuple[str, dict[str | bytes, str | bytes]]] = {
            "/": (
                "index.html",
                {
                    "{{CLIENT_ID}}": quote(constants.CLIENT_ID),
                    "{{REDIRECT_URI}}": quote(constants.AUTH_REDIR),
                    "{{SCOPE}}": quote(constants.SCOPE),
                },
            ),
            "/widget": ("widget.html",),
            "/widget.js": ("widget.js", {"{{WS_PORT}}": str(constants.HTTP_PORT + 1)}),
            "/widget.css": ("widget.css",),
            "/PasseroOne.ttf": ("passero_one/PasseroOne.ttf",),
            "/dashboard": (
                "dashboard.html",
                {
                    "{{CLIENT_ID}}": quote(constants.CLIENT_ID),
                    "{{REDIRECT_URI}}": quote(constants.AUTH_REDIR),
                    "{{SCOPE}}": quote(constants.SCOPE),
                },
            ),
            "/dashboard.js": (
                "dashboard.js",
                {"{{WS_PORT}}": str(constants.HTTP_PORT + 1)},
            ),
            "/dashboard.css": ("dashboard.css",),
        }

        match path:
            case "/authorized":
                self._authorized(params)

            case _:
                page = PAGES.get(path, None)

                if page is None:
                    self.send_error(
                        404, "Not Found", "This page could not be found! :("
                    )
                    return

                self._send_page(*page)
