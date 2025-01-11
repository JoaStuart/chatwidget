import json
import os
from typing import Any
import constants
from singleton import singleton


@singleton
class Config:
    FILE = os.path.join(constants.ROOT_DIR, "config.json")

    def __init__(self):
        self._config: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        with open(self.FILE, "r") as rf:
            return json.loads(rf.read())

    def _write(self) -> None:
        with open(self.FILE, "w") as wf:
            wf.write(json.dumps(self._config, indent=2))

    def __setitem__(self, key: str, val: Any) -> None:
        self._config[key]["current"] = val
        from widget.widget_comm import CommServer

        CommServer.broadcast(
            {
                "event": "config_change",
                "data": {"key": key, "value": val},
            }
        )

        self._write()

    def __getitem__(self, key: str) -> Any:
        return self._config[key]["current"]

    def dump(self) -> dict[str, Any]:
        return {k: v["current"] for k, v in self._config.items()}

    def reset(self, key: str) -> Any:
        c = self._config[key]
        c["current"] = c["default"]

        self._write()
        return c["current"]
