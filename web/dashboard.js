const sock = new WebSocket("ws://localhost:{{WS_PORT}}/");
const form = document.getElementById("config");
const connect = document.getElementById("connect");
const diffUser = document.getElementById("different_user");
const diffUserInp = document.getElementById("user_id");
const descriptionBox = document.getElementById("description");
let descriptionShown = true;
const config = {};

sock.addEventListener("message", (ev) => {
  const msg = JSON.parse(ev.data);

  if (msg.event === "config") {
    // Config dump

    const conf = msg.data;

    for (const key of Object.keys(conf)) {
      document.getElementById(key).value = conf[key];
      config[key] = conf[key];
    }
  } else if (msg.event === "config_change") {
    document.getElementById(msg.data.key).value = msg.data.value;
    config[msg.data.key] = msg.data.value;
  } else if (msg.event === "connect") {
    const connected = msg.data.connected;
    connect.disabled = connected;
  }
});

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

form.addEventListener("submit", (ev) => {
  ev.preventDefault();

  for (const key of Object.keys(config)) {
    const el = document.getElementById(key);

    if (el.value !== config[key]) {
      sendChange(key, el.value);
      config[key] = el.value;
    }
  }
});

diffUser.addEventListener("change", (ev) => {
  diffUserInp.disabled = !ev.target.checked;
});

for (const descripted of document.getElementsByClassName("description")) {
  descripted.addEventListener("mouseover", () => {
    descriptionBox.innerText = descripted.dataset.desc;
  });
}
