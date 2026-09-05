/* M-HELP · floating help button, guide chips, chatbot. */
const HelpView = (() => {
  let history = [];
  const QUICK = ["help.q1", "help.q2", "help.q3", "help.q4"];

  function init() {
    const panel = UI.el("helpPanel");
    UI.el("helpBtn").onclick = () => { panel.classList.add("open"); renderQuick(); UI.el("chatInput").focus(); };
    UI.el("helpClose").onclick = () => panel.classList.remove("open");
    panel.onclick = e => { if (e.target === panel) panel.classList.remove("open"); };
    UI.el("chatSend").onclick = send;
    UI.el("chatInput").onkeydown = e => { if (e.key === "Enter") send(); };
    relabel();
  }

  /* v1.7: the panel's fixed copy follows the language switch. The greeting is
     re-drawn only while the conversation is still empty — a real exchange is
     never rewritten under the person. */
  function relabel() {
    UI.el("helpTitle").textContent = UI.t("help.title");
    UI.el("helpSub").textContent = UI.t("help.sub");
    UI.el("helpClose").textContent = UI.t("help.close");
    UI.el("chatInput").placeholder = UI.t("help.placeholder");
    UI.el("chatSend").textContent = UI.t("help.send");
    UI.el("helpPanel").setAttribute("aria-label", UI.t("help.btn"));
    if (history.length <= 1) {
      history = []; UI.el("chatLog").innerHTML = "";
      addMsg("bot", UI.t("help.greeting"));
    }
    if (UI.el("helpPanel").classList.contains("open")) renderQuick();
  }

  function renderQuick() {
    UI.el("helpQuick").innerHTML = QUICK.map(id => {
      const q = UI.t(id);
      return `<button class="chip" onclick="HelpView.ask('${q.replace(/'/g, "\\'")}')">${UI.esc(q)}</button>`;
    }).join("");
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
      addMsg("bot", UI.t("help.offline"));
    }
  }

  return { init, ask, relabel };
})();
