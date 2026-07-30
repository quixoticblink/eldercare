/* M-HELP · floating help button, guide chips, chatbot. */
const HelpView = (() => {
  let history = [];
  const QUICK = ["How do I book a visit?", "What's the start code?", "When am I approved?", "How do payouts work?"];

  function init() {
    const panel = UI.el("helpPanel");
    UI.el("helpBtn").onclick = () => { panel.classList.add("open"); renderQuick(); UI.el("chatInput").focus(); };
    UI.el("helpClose").onclick = () => panel.classList.remove("open");
    panel.onclick = e => { if (e.target === panel) panel.classList.remove("open"); };
    UI.el("chatSend").onclick = send;
    UI.el("chatInput").onkeydown = e => { if (e.key === "Enter") send(); };
    if (!history.length) addMsg("bot", "Hello! I'm the Kakis helper. Ask me anything about booking, visits, the start code, or approvals.");
  }

  function renderQuick() {
    UI.el("helpQuick").innerHTML = QUICK.map(q =>
      `<button class="chip" onclick="HelpView.ask('${q.replace(/'/g, "\\'")}')">${q}</button>`).join("");
  }

  function addMsg(role, text) {
    history.push({ role: role === "user" ? "user" : "assistant", content: text });
    const log = UI.el("chatLog");
    const div = document.createElement("div");
    div.className = "msg " + (role === "user" ? "user" : "bot");
    div.textContent = text;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  async function ask(q) { UI.el("chatInput").value = q; send(); }

  async function send() {
    const input = UI.el("chatInput");
    const msg = input.value.trim();
    if (!msg) return;
    input.value = "";
    addMsg("user", msg);
    try {
      const r = await Api.post("/chat", { message: msg, history: history.slice(0, -1) });
      addMsg("bot", r.reply);
    } catch (e) {
      addMsg("bot", "I couldn't reach the helper just now — try again, or call the coordinator at 6XXX XXXX.");
    }
  }

  return { init, ask };
})();
