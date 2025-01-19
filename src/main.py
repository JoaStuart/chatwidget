from threading import Thread
from interrupt import handle_interrupt, register_interrupt
from twitch.credentials import Credentials
from web.webserver import HTTPHandler
from widget.combo import ComboManager
from widget.widget_comm import CommServer


if __name__ != "__main__":
    print("Try executing this file directly!")
    exit(-1)

# Start services in background threads
Thread(target=HTTPHandler.start_server, name="WebServer", daemon=True).start()
Thread(target=ComboManager().combo_thread, name="ComboManager", daemon=True).start()
Thread(target=CommServer.recv_thread, name="CommsServer", daemon=True).start()


register_interrupt()

# Wait until the user presses ^C or a shutdown occurs
try:
    Credentials().shutdown.wait()
except KeyboardInterrupt:
    pass

handle_interrupt()
