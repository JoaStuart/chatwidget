const form = document.getElementById("config");
const connect = document.getElementById("connect");
const diffUser = document.getElementById("different_user");
const diffUserInp = document.getElementById("user_id");
const descriptionBox = document.getElementById("description");
let descriptionShown = true;
const config = {};

/**
 * Sends a config change back to the server
 * @param {string} key
 * @param {*} val
 */
const sendChange = (key, val) => {
  sock.send(
    JSON.stringify({
      event: "config_set",
      data: {
        key: key,
        value: val,
      },
    })
  );
};

/**
 * The listener for any config value changing
 * @param {Event | null} ev
 */
const changelistener = (ev) => {
  if (ev) ev.preventDefault();
  document.activeElement.blur();

  for (const key of Object.keys(config)) {
    const el = document.getElementById(key);

    if (String(el.value) !== String(config[key])) {
      if (typeof config[key] === "boolean") {
        sendChange(key, el.checked);
        config[key] = el.checked;
      } else {
        sendChange(key, el.value);
        config[key] = el.value;
      }
    }
  }
};

form.addEventListener("submit", changelistener);

// Listener for switching a checkbox
diffUser.addEventListener("change", (ev) => {
  diffUserInp.disabled = !ev.target.checked;
  changelistener(null);
});

// Make descripted elements function
for (const descripted of document.getElementsByClassName("description")) {
  descripted.addEventListener("mouseover", () => {
    descriptionBox.innerText = descripted.dataset.desc;
  });
}

/**
 * Test for whether the backend server is up again
 */
const reloadTest = () => {
  fetch("/reconnect")
    .then(() => {
      sock = connectSock();
    })
    .catch(() => setTimeout(reloadTest, 1000));
};

/**
 * Connects a WebSocket to the backend
 * @returns The socket connected to the backend
 */
const connectSock = () => {
  const s = new WebSocket("ws://localhost:{{WS_PORT}}/");

  s.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);

    if (msg.event === "config") {
      // Config dump

      const conf = msg.data;

      for (const key of Object.keys(conf)) {
        const el = document.getElementById(key);
        config[key] = conf[key];

        if (typeof key === "boolean") el.checked = conf[key];
        else el.value = conf[key];
      }
    } else if (msg.event === "config_change") {
      const el = document.getElementById(msg.data.key);
      config[msg.data.key] = msg.data.value;

      if (typeof msg.data.key === "boolean") el.checked = conf[msg.data.key];
      else el.value = msg.data.value;
    } else if (msg.event === "connect") {
      const connected = msg.data.connected;
      connect.disabled = connected;
    }
  });

  s.addEventListener("close", () => {
    document.getElementById("reconnect").style.display = "flex";
    reloadTest();
  });

  document.getElementById("reconnect").style.display = "none";
  return s;
};

document.getElementById("reset").addEventListener("click", () => {
  sock.send(
    JSON.stringify({
      event: "config_reset",
      data: {},
    })
  );
});

document.getElementById("shutdown").addEventListener("click", () => {
  sock.send(
    JSON.stringify({
      event: "shutdown",
      data: {},
    })
  );
});

let sock = connectSock();
