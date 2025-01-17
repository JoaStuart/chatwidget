const msgList = document.getElementById("messages");
const notification = document.getElementById("notification");

const activeCombos = {};

/**
 * Plays a bounce animation on the element
 * @param {Element} el
 */
const bounce = (el) => {
  el.animate(
    [
      { transform: "scale(1)" },
      { transform: "scale(1.2)" },
      { transform: "scale(1)" },
    ],
    { duration: 200, easing: "ease" }
  );
};

/**
 * Converts an emote string into elements
 * @param {{}} emoteStr
 * @param {Element} emoteEl
 */
const createEmoteString = (emoteStr, emoteEl) => {
  for (const part of emoteStr) {
    if (part.type === "text") {
      const el = document.createElement("span");

      el.innerText = part.value;
      el.classList.add("textpart");

      emoteEl.appendChild(el);
    } else if (part.type === "emote") {
      const el = document.createElement("img");

      el.src = part.value;
      el.alt = part.text;
      el.classList.add("textpart");

      emoteEl.appendChild(el);
    }
  }
};

/**
 * Creates a combo for the given message
 * @param {string} msg The message
 */
const createCombo = (msg) => {
  const el = document.createElement("div");
  const text = document.createElement("div");
  const combo = document.createElement("span");

  createEmoteString(msg.data.emote, text);
  el.dataset["text"] = msg.data.text;
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

/**
 * Updates the count of a combo
 * @param {string} msg The message to update
 */
const updateCombo = (msg) => {
  const combo = activeCombos[msg.data.text];
  if (combo === undefined) return;

  combo.comboEl.innerText = `x${msg.data.combo}`;

  bounce(combo.rootEl);
};

/**
 * Removes a combo message
 * @param {string} msg The message to remove
 */
const removeCombo = (msg) => {
  const combo = activeCombos[msg.data.text];
  if (combo === undefined) return;

  combo.rootEl.animate(
    { transform: "scale(0)" },
    { duration: 200, fill: "forwards", easing: "ease-in" }
  );

  setTimeout(() => msgList.removeChild(combo.rootEl), 200);

  delete activeCombos[msg.data.text];
};

/**
 * Tests if the backend is up again
 */
const reloadTest = () => {
  fetch("/")
    .then(() => {
      sock = connect();
    })
    .catch(() => setTimeout(reloadTest, 1000));
};

/**
 * Establishes a WebSocket connection to the backend
 * @returns The connected WebSocket
 */
const connect = () => {
  const s = new WebSocket("ws://localhost:{{WS_PORT}}/");
  s.addEventListener("message", (event) => {
    const msg = JSON.parse(event.data);

    if (msg.event === "combo_create") createCombo(msg);
    else if (msg.event === "combo_update") updateCombo(msg);
    else if (msg.event === "combo_remove") removeCombo(msg);
  });

  s.addEventListener("close", () => {
    notification.animate(
      { transform: "translateX(0px)" },
      { duration: 400, fill: "forwards" }
    );
    reloadTest();
  });

  s.addEventListener("open", () => {
    notification.animate(
      { transform: "translateX(-50px)" },
      { duration: 400, fill: "forwards" }
    );
  });

  return s;
};

let sock = connect();
