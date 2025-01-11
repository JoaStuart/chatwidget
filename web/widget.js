const msgList = document.getElementById("messages");
const sock = new WebSocket("ws://localhost:{{WS_PORT}}/");

const activeCombos = {};

const bounce = (el) => {
  el.animate(
    [
      { transform: "scale(1)" },
      { transform: "scale(1.2)" },
      { transform: "scale(1)" },
    ],
    { duration: 200, easing: "ease-out" }
  );
};

const createCombo = (msg) => {
  const el = document.createElement("div");
  const text = document.createElement("span");
  const combo = document.createElement("span");

  text.innerText = msg.data.text;
  combo.innerText = `x${msg.data.combo}`;

  text.classList.add("text");
  combo.classList.add("combo");

  el.appendChild(text);
  el.appendChild(combo);
  msgList.appendChild(el);

  activeCombos[msg.data.text] = {
    comboEl: combo,
    rootEl: el,
  };

  bounce(el);
};

const updateCombo = (msg) => {
  activeCombos[msg.data.text].comboEl.innerText = `x${msg.data.combo}`;

  bounce(activeCombos[msg.data.text].rootEl);
};

const removeCombo = (msg) => {
  activeCombos[msg.data.text].rootEl.animate(
    { transform: "scale(0)" },
    { duration: 200, fill: "forwards", easing: "ease-in" }
  );

  setTimeout(() => {
    msgList.removeChild(activeCombos[msg.data.text].rootEl);
  }, 200);
};

sock.addEventListener("message", (event) => {
  const msg = JSON.parse(event.data);

  if (msg.event === "combo_create") createCombo(msg);
  else if (msg.event === "combo_update") updateCombo(msg);
  else if (msg.event === "combo_remove") removeCombo(msg);
});
