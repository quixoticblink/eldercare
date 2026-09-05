/* M-AUTH · login (email or mobile → code → role on first visit only), pending screen.
   Every sentence comes from i18n.js via UI.t (v1.7); role chips carry stable
   data-v ids so the label can be in either language. */
const AuthView = (() => {
  let session = { identifier: "", channel: "email", needsProfile: true };
  let current = "login";      // which screen is up, so a language switch can redraw it
  let lastDevCode = null;
  const t = (id, vars) => UI.t(id, vars);

  function login() {
    current = "login";
    UI.screen(`
      ${UI.appbar(t("login.title"), t("login.sub"))}
      <div class="card tint"><p>${t("login.intro")}</p></div>
      <label class="f-label" for="ident">${t("login.label")}</label>
      <div class="f-hint">${t("login.hint")}</div>
      <input class="f-input" id="ident" type="text" inputmode="email" autocomplete="username" placeholder="">
      <button class="btn" id="sendBtn">${t("login.send")}</button>
      <p class="initiative-link">${t("login.initiative")}
        <a href="https://eldercare-rho.vercel.app/#" target="_blank" rel="noopener noreferrer">eldercare-rho.vercel.app</a></p>
      <div class="helpline">${t("common.helpline")} <b>${t("common.iccp")}</b></div>`);

    const submit = async () => {
      const identifier = UI.el("ident").value.trim();
      if (!identifier) return UI.toast(t("login.empty"), true);
      UI.el("sendBtn").disabled = true;
      try {
        const r = await Api.post("/auth/request-code", { identifier });
        session = { identifier: r.identifier || identifier, channel: r.channel,
                    needsProfile: r.needs_profile, demo: !!r.demo };
        code(r.dev_code);
      } catch (e) { UI.toast(UI.terr(e), true); UI.el("sendBtn").disabled = false; }
    };
    UI.el("sendBtn").onclick = submit;
    UI.el("ident").onkeydown = e => { if (e.key === "Enter") submit(); };
  }

  function code(devCode) {
    /* Returning users are only ever asked for the 6 digits. Name, role and the
       second contact channel appear on the first sign-in and never again. */
    current = "code"; lastDevCode = devCode;
    const firstTime = session.needsProfile;
    const secondChannel = session.channel === "phone"
      ? `<label class="f-label" for="altIn">${t("code.alt.email")} <small>${t("common.optional")}</small></label>
         <input class="f-input" id="altIn" type="email" inputmode="email" placeholder="you@example.com">`
      : `<label class="f-label" for="altIn">${t("code.alt.phone")} <small>${t("common.optional")}</small></label>
         <input class="f-input" id="altIn" type="tel" inputmode="tel" placeholder="9123 4567">`;

    UI.screen(`
      ${UI.appbar(session.channel === "phone" ? t("code.title.phone") : t("code.title.email"),
                  t("code.sub", { id: session.identifier }))}
      ${devCode ? `<div class="card warn"><h3>${session.demo ? t("code.demo") : t("code.dev")}</h3><p>${t("code.yourcode")}
        <b class="mono">${UI.esc(devCode)}</b> —
        ${session.demo ? t("code.demo.why") : (session.channel === "phone" ? t("code.dev.why.sms") : t("code.dev.why.email"))}</p></div>` : ""}
      <label class="f-label" for="codeIn">${t("code.label")}</label>
      <input class="f-input mono" id="codeIn" inputmode="numeric" maxlength="6" placeholder="••••••"
        style="text-align:center;font-size:1.5rem;letter-spacing:8px">
      ${firstTime ? `
        <label class="f-label" for="nameIn">${t("code.name")}</label>
        <input class="f-input" id="nameIn" autocomplete="name" placeholder="${UI.esc(t("code.name.ph"))}">
        <label class="f-label">${t("code.iam")}</label>
        <div class="chips" id="roleG">
          <button type="button" class="chip" data-v="caregiver" onclick="UI.pick('roleG', this)">${t("code.role.cg")}</button>
          <button type="button" class="chip" data-v="kaki" onclick="UI.pick('roleG', this)">${t("code.role.kaki")}</button>
        </div>
        ${secondChannel}
      ` : `<div class="card tint"><p>${t("code.back")}</p></div>`}
      <button class="btn" id="verifyBtn">${t("code.signin")}</button>
      <button class="btn ghost" onclick="AuthView.login()">${t("code.other")}</button>`);

    const submit = async () => {
      const payload = { identifier: session.identifier, code: UI.el("codeIn").value.trim() };
      if (firstTime) {
        payload.role = UI.chipValue("roleG") || null;
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
      } catch (e) { UI.toast(UI.terr(e), true); }
    };
    UI.el("verifyBtn").onclick = submit;
    UI.el("codeIn").onkeydown = e => { if (e.key === "Enter") submit(); };
    UI.el("codeIn").focus();
  }

  function pending(user) {
    current = "pending";
    UI.screen(`
      ${UI.appbar(t("pending.title", { name: user.name || t("pending.friend") }), t("pending.sub"))}
      <div class="card tint">
        <h3>${t("pending.nothing")}</h3>
        <p>${t("pending.body", { what: user.role === "kaki" ? t("pending.see") : t("pending.book") })}</p>
      </div>
      ${user.role === "kaki" ? `<button class="btn" onclick="location.hash='#/kaki/profile'">${t("pending.certs")}</button>
      <p class="f-hint">${t("pending.certs.hint")}</p>` : ""}
      <button class="btn quiet" onclick="App.boot()">${t("pending.again")}</button>
      <button class="btn ghost" onclick="App.logout()">${t("menu.signout")}</button>
      <div class="helpline">${t("common.helpline.q")} <b>${t("common.iccp")}</b></div>`);
  }

  /* Redraw the signed-out screen in the new language, keeping what was typed. */
  function rerender() {
    if (current === "code") {
      const typed = (UI.el("codeIn") || {}).value || "";
      code(lastDevCode);
      if (typed) UI.el("codeIn").value = typed;
    } else if (current === "login") {
      const typed = (UI.el("ident") || {}).value || "";
      login();
      if (typed) UI.el("ident").value = typed;
    }
  }

  return { login, code, pending, rerender };
})();
