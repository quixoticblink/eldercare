/* M-AUTH · login (email → code → role), pending screen. */
const AuthView = (() => {
  let pendingEmail = "";

  function login() {
    UI.screen(`
      ${UI.appbar("Welcome to Kakis", "Trusted respite when a need arises")}
      <div class="card tint"><p>Sign in with your email — we'll send you a 6-digit code. No password needed.</p></div>
      <label class="f-label" for="email">Your email</label>
      <input class="f-input" id="email" type="email" inputmode="email" autocomplete="email" placeholder="you@example.com">
      <button class="btn" id="sendBtn">Send my code</button>
      <div class="helpline">Stuck? Call <b>Pasir Ris ICCP · 6XXX XXXX</b></div>`);
    UI.el("sendBtn").onclick = async () => {
      const email = UI.el("email").value.trim();
      if (!email.includes("@")) return UI.toast("Enter a valid email", true);
      UI.el("sendBtn").disabled = true;
      try {
        const r = await Api.post("/auth/request-code", { email });
        pendingEmail = email;
        code(r.dev_code);
      } catch (e) { UI.toast(e.message, true); UI.el("sendBtn").disabled = false; }
    };
  }

  function code(devCode) {
    UI.screen(`
      ${UI.appbar("Check your email", `We sent a code to ${pendingEmail}`)}
      ${devCode ? `<div class="card warn"><h3>Dev mode</h3><p>Your code is <b class="mono">${devCode}</b> (email sending not configured yet).</p></div>` : ""}
      <label class="f-label" for="codeIn">6-digit code</label>
      <input class="f-input mono" id="codeIn" inputmode="numeric" maxlength="6" placeholder="••••••"
        style="text-align:center;font-size:1.5rem;letter-spacing:8px">
      <label class="f-label" for="nameIn">Your name <small>· first time only</small></label>
      <input class="f-input" id="nameIn" autocomplete="name" placeholder="e.g. Priya N.">
      <label class="f-label">I am…</label>
      ${UI.chipGroup("roleG", ["A caregiver booking for my family", "A kaki — I want to help"], null)}
      <button class="btn" id="verifyBtn">Sign in</button>
      <button class="btn ghost" onclick="AuthView.login()">Use a different email</button>`);
    UI.el("verifyBtn").onclick = async () => {
      const roleTxt = UI.chipValue("roleG") || "";
      const role = roleTxt.startsWith("A caregiver") ? "caregiver" : roleTxt.startsWith("A kaki") ? "kaki" : null;
      try {
        const r = await Api.post("/auth/verify", {
          email: pendingEmail, code: UI.el("codeIn").value.trim(),
          role, name: UI.el("nameIn").value.trim() || null,
        });
        Api.setToken(r.token);
        App.boot();
      } catch (e) { UI.toast(e.message, true); }
    };
  }

  function pending(user) {
    UI.screen(`
      ${UI.appbar("Almost there, " + (user.name || "friend"), "Your account is waiting for approval")}
      <div class="card tint">
        <h3>The coordinator is reviewing your account</h3>
        <p>New ${user.role === "kaki" ? "kakis" : "caregivers"} are approved by the Pasir Ris coordinator —
        usually within a day. You'll be able to ${user.role === "kaki" ? "see visits" : "book visits"} as soon as that's done.</p>
      </div>
      <button class="btn quiet" onclick="App.boot()">Check again</button>
      <button class="btn ghost" onclick="App.logout()">Sign out</button>
      <div class="helpline">Questions? Call <b>Pasir Ris ICCP · 6XXX XXXX</b></div>`);
  }

  return { login, code, pending };
})();
