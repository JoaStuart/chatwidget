import os
import sys
from threading import Thread
import time
from log import LOG
from twitch.credentials import Credentials
from twitch.events import EventTypes
from twitch.twitch import TwitchConn
from web.webserver import HTTPHandler
from widget.combo import ComboManager
from widget.widget_comm import CommServer


if __name__ != "__main__":
    print("Try executing this file directly!")
    exit(-1)

# Set console title
if os.name == "nt":
    import ctypes

    ctypes.windll.kernel32.SetConsoleTitleW("ChatWidget")
else:
    sys.stdout.write("\x1b]0;ChatWidget\x07")

# Start services in background threads
Thread(target=HTTPHandler.start_server, name="WebServer", daemon=True).start()
Thread(target=ComboManager().combo_thread, name="ComboManager", daemon=True).start()
Thread(target=CommServer.recv_thread, name="CommsServer", daemon=True).start()


# Wait until the user presses ^C or a shutdown occurs
try:
    while not Credentials().shutdown.is_set():
        # We cannot use `wait()` here, because it blocks ^C
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

LOG.info("Shutting down...")

# Shut down all services
EventTypes.delete_all()
TwitchConn().stop()
CommServer.close_all()

sys.exit(0)
