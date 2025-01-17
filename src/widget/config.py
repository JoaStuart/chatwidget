import json
import os
from typing import Any, Callable

import constants
from log import LOG
from singleton import singleton


@singleton
class Config:
    FILE = os.path.join(constants.ROOT_DIR, "config.json")

    def __init__(self):
        self._config: dict[str, Any] = self._load()
        self._callbacks: dict[str, Callable[[], None]] = {}

    def _load(self) -> dict[str, Any]:
        """Loads the config from file

        Returns:
            dict[str, Any]: The config data loaded
        """

        with open(self.FILE, "r") as rf:
            return json.loads(rf.read())

    def _write(self) -> None:
        """Writes the config data to file"""

        with open(self.FILE, "w") as wf:
            wf.write(json.dumps(self._config, indent=2))

    def __setitem__(self, key: str, val: Any) -> None:
        """Python setter for changing config values

        Args:
            key (str): The key to change the value of
            val (Any): The new value to change to
        """

        default = self._config[key]["default"]
        if isinstance(default, float):
            val = float(val)
        elif isinstance(default, int):
            val = int(val)

        self._config[key]["current"] = val
        from widget.widget_comm import CommServer

        CommServer.broadcast(
            {
                "event": "config_change",
                "data": {"key": key, "value": val},
            }
        )

        self._write()

        callback = self._callbacks.get(key, None)
        if callback:
            callback()

    def __getitem__(self, key: str) -> Any:
        """Python getter for getting the current value of a key

        Args:
            key (str): The key to get the value of

        Returns:
            Any: The value of the current key
        """

        return self._config[key]["current"]

    def dump(self) -> dict[str, Any]:
        """Dumps all current values of the config

        Returns:
            dict[str, Any]: The dumped values
        """

        return {k: v["current"] for k, v in self._config.items()}

    def reset(self, key: str) -> Any:
        """Resets a value to its default

        Args:
            key (str): The key of the value to reset

        Returns:
            Any: The default value being reset to
        """

        c = self._config[key]
        c["current"] = c["default"]

        self._write()
        return c["current"]

    def add_change_callback(self, key: str, callback: Callable[[], None]) -> None:
        """Adds a callback which gets called when the value of key changes

        Args:
            key (str): The key to add the callback to
            callback (Callable[[], None]): The callback to be called upon change
        """

        self._callbacks[key] = callback
