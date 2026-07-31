/* M-CORE · app.js — session, role dispatch, hash router, bottom nav. */
const App = (() => {
  let user = null;
  let config = { services: [], languages: [], tiers: [] };

  const NAVS = {
    caregiver: [["#/care/home", "⌂", "Home"], ["#/care/book", "＋", "Book"], ["#/care/visits", "◷", "Visits"]],
    kaki:      [["#/kaki/home", "☰", "Visits"], ["#/kaki/impact", "✦", "Impact"], ["#/kaki/profile", "◉", "Profile"]],
    admin:     [["#/admin/home", "◎", "Today"], ["#/admin/approvals", "✓", "Approvals"], ["#/admin/requests", "⚙", "Matching"], ["#/admin/quality", "❋", "Quality"]],
  };

  const ROUTES = {
    "#/care/home": () => CareView.home(),
    "#/care/plan": () => CareView.planEdit(),
    "#/care/book": () => CareView.book(),
    "#/care/visits": () => CareView.visits(),
    "#/kaki/home": () => KakiView.home(),
    "#/kaki/impact": () => KakiView.impact(),
    "#/kaki/profile": () => KakiView.profile(),
    "#/admin/home": () => AdminView.home(),
    "#/admin/approvals": () => AdminView.approvals(),
    "#/admin/requests": () => AdminView.requests(),
    "#/admin/quality": () => AdminView.quality(),
    "#/admin/assumptions": () => AdminView.assumptions(),
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
        onclick="location.hash='${h}'"><span class="ico">${ico}</span>${label}</button>`).join("");
  }

  function route() {
    if (!user) return;
    if (user.status !== "approved") return AuthView.pending(user);
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
      config = { services: me.config.services, languages: me.config.languages, tiers: me.config.tiers };
      App.user = user; App.config = config;
      UI.el("brandRight").textContent = (user.name || user.email || "").toUpperCase().slice(0, 22) || "PASIR RIS PILOT";
      if (user.status !== "approved") return AuthView.pending(user);
      if (!location.hash || location.hash === "#/" || !location.hash.startsWith("#/")) location.hash = homeFor(user.role);
      route();
    } catch (e) {
      Api.setToken(null); user = null; AuthView.login();
    }
  }

  function logout() {
    Api.setToken(null); user = null; location.hash = "";
    UI.el("tabs").style.display = "none";
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
  document.addEventListener("DOMContentLoaded", () => { HelpView.init(); initUserMenu(); boot(); });

  return { boot, logout, route,
    get user() { return user; }, set user(u) { user = u; },
    get config() { return config; }, set config(c) { config = c; } };
})();
