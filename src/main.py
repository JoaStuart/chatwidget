import random
from threading import Thread
from time import sleep
from log import LOG
from twitch.events import EventTypes, TwitchEvent
from twitch.twitch import TwitchConn
from web.webserver import HTTPHandler
from widget.combo import ComboManager
from widget.widget_comm import CommServer


if __name__ != "__main__":
    print("Try executing this file directly!")
    exit(-1)

Thread(target=HTTPHandler.start_server, name="WebServer", daemon=True).start()
Thread(target=ComboManager().combo_thread, name="ComboManager", daemon=True).start()
Thread(target=CommServer.recv_thread, name="CommsManager", daemon=True).start()


MOCK_MESSAGES = [
    "Hi",
    "catJAM",
    "KEKW",
    "lul",
    "Kappa",
]

try:
    while True:
        sleep(0.5)
        ComboManager().read(random.choice(MOCK_MESSAGES))
except KeyboardInterrupt:
    LOG.info("Shutting down...")

EventTypes.delete_all()
TwitchConn().stop()
