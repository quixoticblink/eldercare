/* M-CORE · app.js — session, role dispatch, hash router, bottom nav. */
const App = (() => {
  let user = null;
  let config = { services: [], languages: [], tiers: [] };

  /* Nav labels: caregiver and kaki tabs are dictionary ids (v1.7); the
     coordinator's stay literal English — the console is English by design. */
  const NAVS = {
    caregiver: [["#/care/home", "⌂", "nav.home"], ["#/care/book", "＋", "nav.book"], ["#/care/visits", "◷", "nav.visits"]],
    kaki:      [["#/kaki/home", "☰", "nav.visits"], ["#/kaki/impact", "✦", "nav.impact"], ["#/kaki/profile", "◉", "nav.profile"]],
    admin:     [["#/admin/home", "◎", "Today"], ["#/admin/approvals", "✓", "Approvals"], ["#/admin/requests", "⚙", "Matching"], ["#/admin/quality", "❋", "Quality"]],
  };

  const ROUTES = {
    "#/care/home": () => CareView.home(),
    "#/care/plan": () => CareView.planEdit(),
    "#/care/profile": () => CareView.profile(),
    "#/care/book": () => CareView.book(),
    "#/care/book/when": () => CareView.when(),
    "#/care/book/trigger": () => CareView.triggers(),
    "#/care/book/details": () => CareView.details(),
    "#/care/visits": () => CareView.visits(),
    "#/kaki/home": () => KakiView.home(),
    "#/kaki/impact": () => KakiView.impact(),
    "#/kaki/profile": () => KakiView.profile(),
    "#/admin/home": () => AdminView.home(),
    "#/admin/approvals": () => AdminView.approvals(),
    "#/admin/requests": () => AdminView.requests(),
    "#/admin/quality": () => AdminView.quality(),
    "#/admin/assumptions": () => AdminView.assumptions(),
    "#/admin/settings": () => AdminView.settings(),
    "#/kaki/availability": () => KakiView.availability(),
  };

  function homeFor(role) {
    return { caregiver: "#/care/home", kaki: "#/kaki/home", admin: "#/admin/home" }[role] || "#/care/home";
  }

  function renderNav() {
    const tabs = UI.el("tabs");
    const items = user && user.status === "approved" ? NAVS[user.role] : null;
    if (!items) { tabs.style.display = "none"; return; }
    tabs.style.display = "flex";
    tabs.innerHTML = items.map(([h, ico, label]) =>
      `<button class="${location.hash.startsWith(h.split("/").slice(0, 3).join("/")) ? "on" : ""}"
        onclick="location.hash='${h}'"><span class="ico">${ico}</span>${label.startsWith("nav.") ? UI.t(label) : label}</button>`).join("");
  }

  /* ---- language (v1.7) ----------------------------------------------------
     Caregivers and kakis may switch between English and Chinese; the button
     sits in the brand bar on every one of their screens, sign-in included.
     The coordinator never sees it and always gets English. Order of truth on
     boot: this phone's stored choice → users.lang → the phone's language. */
  function applyLang() {
    const btn = UI.el("langBtn");
    const isAdmin = user && user.role === "admin";
    if (isAdmin) UI.setLang("en", false);   // not persisted: a shared phone keeps its choice
    btn.hidden = !!isAdmin;
    btn.textContent = UI.t("lang.switch");
    btn.setAttribute("aria-label", UI.t("lang.switch.aria"));
    UI.el("umSignout").textContent = UI.t("menu.signout");
    if (!Api.getToken()) UI.el("umWho").textContent = UI.t("menu.notsigned");
    UI.el("helpBtn").setAttribute("aria-label", UI.t("help.btn"));
    HelpView.relabel();   // English again for the coordinator, whatever the phone was set to
  }
  function initLang() {
    UI.setLang(UI.storedLang() || "en", false);
    applyLang();
    UI.el("langBtn").onclick = async () => {
      UI.setLang(UI.lang === "zh" ? "en" : "zh");
      applyLang();
      if (user && user.role !== "admin") {
        user.lang = UI.lang;
        try { await Api.put("/users/me", { lang: UI.lang }); } catch (e) { /* the phone remembers; the server catches up next time */ }
      }
      if (user) { route(); renderNav(); } else { AuthView.rerender(); }
    };
  }

  function route() {
    if (!user) return;
    // A pending kaki may still add certificates — that is what the coordinator
    // looks at before approving (v1.6). Everything else waits.
    if (user.status !== "approved") {
      if (user.role === "kaki" && location.hash === "#/kaki/profile") return KakiView.profile();
      return AuthView.pending(user);
    }
    const h = location.hash;
    // dynamic routes
    let m;
    if ((m = h.match(/^#\/care\/visit\/(\w+)/))) { CareView.visit(m[1]); renderNav(); return; }
    if ((m = h.match(/^#\/kaki\/visit\/(\w+)/)))  { KakiView.visit(m[1]); renderNav(); return; }
    const fn = ROUTES[h];
    if (fn) { fn(); } else { location.hash = homeFor(user.role); return; }
    renderNav();
  }

  async function boot() {
    if (!Api.getToken()) { user = null; UI.el("tabs").style.display = "none"; return AuthView.login(); }
    try {
      const me = await Api.get("/auth/me");
      user = me.user;
      config = { ...me.config };
      App.user = user; App.config = config;
      // A choice made on another phone follows the person; one made on this
      // phone before signing in is kept and written back.
      if (user.role !== "admin") {
        let stored = ""; try { stored = localStorage.getItem("kakis_lang") || ""; } catch (e) {}
        const want = stored || user.lang || UI.storedLang() || "en";
        UI.setLang(want);
        if (want !== (user.lang || "")) { user.lang = want; Api.put("/users/me", { lang: want }).catch(() => {}); }
      }
      applyLang();
      UI.el("brandRight").textContent = (user.name || user.email || "").toUpperCase().slice(0, 22) || "PASIR RIS PILOT";
      if (user.status !== "approved") {
        if (user.role === "kaki" && location.hash === "#/kaki/profile") return KakiView.profile();
        return AuthView.pending(user);
      }
      if (!location.hash || location.hash === "#/" || !location.hash.startsWith("#/")) location.hash = homeFor(user.role);
      route();
    } catch (e) {
      Api.setToken(null); user = null; applyLang(); AuthView.login();
    }
  }

  function logout() {
    Api.setToken(null); user = null; location.hash = "";
    UI.el("tabs").style.display = "none";
    UI.setLang(UI.storedLang() || "en", false);   // an admin's English lock ends with their session
    applyLang();
    AuthView.login();
  }

  /* global user menu — logout for every role */
  function initUserMenu() {
    const btn = UI.el("brandRight"), menu = UI.el("userMenu");
    btn.onclick = e => {
      e.stopPropagation();
      if (!Api.getToken()) return;
      UI.el("umWho").textContent = user ? `${user.name || ""} · ${user.email}` : "";
      const open = menu.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    };
    document.addEventListener("click", () => menu.classList.remove("open"));
    UI.el("umSignout").onclick = () => { menu.classList.remove("open"); logout(); };
  }

  window.addEventListener("hashchange", route);
  document.addEventListener("DOMContentLoaded", () => { HelpView.init(); initUserMenu(); initLang(); boot(); });

  return { boot, logout, route,
    get user() { return user; }, set user(u) { user = u; },
    get config() { return config; }, set config(c) { config = c; } };
})();
