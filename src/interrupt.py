import os
import sys
import ctypes
from typing import NoReturn

from twitch.events import EventTypes
from twitch.twitch import TwitchConn
from widget.widget_comm import CommServer


def handle_interrupt(*args) -> NoReturn:
    # Shut down all services
    EventTypes.delete_all()
    TwitchConn().stop()
    CommServer.close_all()

    sys.exit(0)


def register_interrupt() -> None:
    if os.name == "nt":
        console_handler = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_uint)(
            handle_interrupt
        )

        ctypes.windll.kernel32.SetConsoleCtrlHandler(console_handler, True)
    else:
        signal.signal(signal.SIGINT, handle_interrupt)
