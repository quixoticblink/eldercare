/* M-AUTH · login (email or mobile → code → role on first visit only), pending screen. */
const AuthView = (() => {
  let session = { identifier: "", channel: "email", needsProfile: true };

  const channelLabel = ch => (ch === "phone" ? "SMS" : "email");

  function login() {
    UI.screen(`
      ${UI.appbar("Welcome to Kakis", "Trusted respite when a need arises")}
      <div class="card tint"><p>Sign in with your email or mobile number — we'll send you a
      6-digit code. No password needed.</p></div>
      <label class="f-label" for="ident">Email or mobile number</label>
      <input class="f-input" id="ident" type="text" inputmode="email" autocomplete="username"
        placeholder="you@example.com or 9123 4567">
      <button class="btn" id="sendBtn">Send my code</button>
      <div class="helpline">Stuck? Call <b>Pasir Ris ICCP · 6XXX XXXX</b></div>`);

    const submit = async () => {
      const identifier = UI.el("ident").value.trim();
      if (!identifier) return UI.toast("Enter your email or mobile number", true);
      UI.el("sendBtn").disabled = true;
      try {
        const r = await Api.post("/auth/request-code", { identifier });
        session = { identifier: r.identifier || identifier, channel: r.channel, needsProfile: r.needs_profile };
        code(r.dev_code);
      } catch (e) { UI.toast(e.message, true); UI.el("sendBtn").disabled = false; }
    };
    UI.el("sendBtn").onclick = submit;
    UI.el("ident").onkeydown = e => { if (e.key === "Enter") submit(); };
  }

  function code(devCode) {
    /* Returning users are only ever asked for the 6 digits. Name, role and the
       second contact channel appear on the first sign-in and never again. */
    const firstTime = session.needsProfile;
    const secondChannel = session.channel === "phone"
      ? `<label class="f-label" for="altIn">Your email <small>· optional</small></label>
         <input class="f-input" id="altIn" type="email" inputmode="email" placeholder="you@example.com">`
      : `<label class="f-label" for="altIn">Your mobile number <small>· optional</small></label>
         <input class="f-input" id="altIn" type="tel" inputmode="tel" placeholder="9123 4567">`;

    UI.screen(`
      ${UI.appbar(session.channel === "phone" ? "Check your phone" : "Check your email",
                  `We sent a code to ${session.identifier}`)}
      ${devCode ? `<div class="card warn"><h3>Dev mode</h3><p>Your code is
        <b class="mono">${UI.esc(devCode)}</b> (${channelLabel(session.channel)} sending not configured yet).</p></div>` : ""}
      <label class="f-label" for="codeIn">6-digit code</label>
      <input class="f-input mono" id="codeIn" inputmode="numeric" maxlength="6" placeholder="••••••"
        style="text-align:center;font-size:1.5rem;letter-spacing:8px">
      ${firstTime ? `
        <label class="f-label" for="nameIn">Your name</label>
        <input class="f-input" id="nameIn" autocomplete="name" placeholder="e.g. Priya N.">
        <label class="f-label">I am…</label>
        ${UI.chipGroup("roleG", ["A caregiver booking for my family", "A kaki — I want to help"], null)}
        ${secondChannel}
      ` : `<div class="card tint"><p>Welcome back — just the code and you're in.</p></div>`}
      <button class="btn" id="verifyBtn">Sign in</button>
      <button class="btn ghost" onclick="AuthView.login()">Use a different email or number</button>`);

    const submit = async () => {
      const payload = { identifier: session.identifier, code: UI.el("codeIn").value.trim() };
      if (firstTime) {
        const roleTxt = UI.chipValue("roleG") || "";
        payload.role = roleTxt.startsWith("A caregiver") ? "caregiver"
                     : roleTxt.startsWith("A kaki") ? "kaki" : null;
        payload.name = UI.el("nameIn").value.trim() || null;
        const alt = UI.el("altIn").value.trim();
        if (alt) {
          if (session.channel === "phone") payload.contact_email = alt;
          else payload.contact_phone = alt;
        }
      }
      try {
        const r = await Api.post("/auth/verify", payload);
        Api.setToken(r.token);
        App.boot();
      } catch (e) { UI.toast(e.message, true); }
    };
    UI.el("verifyBtn").onclick = submit;
    UI.el("codeIn").onkeydown = e => { if (e.key === "Enter") submit(); };
    UI.el("codeIn").focus();
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
