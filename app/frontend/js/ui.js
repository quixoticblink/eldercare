/* M-CORE · ui.js — DOM helpers and small components. No fetch, no routing. */
const UI = (() => {
  const el = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

  /* ---- language (v1.7) ---------------------------------------------------
     One of "en" | "zh". Views never branch on it; they call t() and v().
     The choice is stored by app.js (localStorage + users.lang); this module
     only holds the current value. */
  const LANG_KEY = "kakis_lang";
  let lang = "en";
  const getLang = () => lang;
  function setLang(l, persist = true) {
    lang = l === "zh" ? "zh" : "en";
    if (persist) { try { localStorage.setItem(LANG_KEY, lang); } catch (e) {} }
    document.documentElement.lang = lang === "zh" ? "zh-Hans-SG" : "en";
    return lang;
  }
  /* Stored choice on this phone, or the phone's own language. */
  function storedLang() {
    try { const s = localStorage.getItem(LANG_KEY); if (s === "zh" || s === "en") return s; } catch (e) {}
    return (navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "";
  }
  /* t("id", {name: "Priya"}) — the sentence in the current language, English
     if zh has no entry, the id itself if neither does (so a gap is visible). */
  function t(id, vars) {
    const d = (typeof I18N !== "undefined") ? I18N : { en: {}, zh: {} };
    let s = (lang === "zh" && d.zh[id] != null) ? d.zh[id] : (d.en[id] != null ? d.en[id] : id);
    if (vars) s = s.replace(/\{(\w+)\}/g, (m, k) => (vars[k] != null ? vars[k] : m));
    return s;
  }
  /* v("service", "Chaperone") — display name of a data value; the value
     itself never changes. Unknown values (user-typed) come back untouched. */
  function v(kind, value) {
    if (lang !== "zh" || typeof I18N === "undefined") return value;
    const m = I18N.VALUES[kind] || {};
    return m[value] != null ? m[value] : value;
  }
  /* Error message for a toast: the backend's stable code in the person's
     language, else the English detail it sent. */
  const terr = e => (e && e.code && typeof I18N !== "undefined" && I18N.en["err." + e.code] != null) ? t("err." + e.code) : (e && e.message) || t("common.wrong");
  const hrs = n => t(n === 1 ? "common.hrs" : "common.hrs.pl", { n });
  const visitsN = n => t(n === 1 ? "common.visits1" : "common.visits", { n });

  function toast(msg, isErr = false) {
    const t = el("toast");
    t.textContent = msg;
    t.className = isErr ? "err show" : "show";
    clearTimeout(t._h);
    t._h = setTimeout(() => (t.className = ""), 3200);
  }

  function screen(html) { el("screen").innerHTML = html; window.scrollTo(0, 0); }
  function spin() { screen('<div class="center"><div class="spin"></div></div>'); }

  function appbar(title, sub, backHash) {
    return `<div class="appbar">
      ${backHash ? `<button class="back" onclick="location.hash='${backHash}'" aria-label="${esc(t("common.back"))}">←</button>` : ""}
      <h1>${esc(title)}${sub ? `<span class="sub">${esc(sub)}</span>` : ""}</h1>
    </div>`;
  }

  /* single-select chip group; value read via UI.chipValue(groupId).
     `kind` (optional) names a VALUES table so the label can be shown in the
     person's language while data-v stays the English value. */
  function chipGroup(id, options, selected, kind) {
    return `<div class="chips" id="${id}">` + options.map(o =>
      `<button type="button" class="chip${o === selected ? " sel" : ""}" data-v="${esc(o)}"
        onclick="UI.pick('${id}', this)">${esc(kind ? v(kind, o) : o)}</button>`).join("") + `</div>`;
  }
  function pick(groupId, btn) {
    document.querySelectorAll(`#${groupId} .chip`).forEach(c => c.classList.remove("sel"));
    btn.classList.add("sel");
  }
  function chipValue(groupId) {
    const s = document.querySelector(`#${groupId} .chip.sel`);
    return s ? s.dataset.v : null;
  }

  /* multi-select chips */
  function chipMulti(id, options, selected = [], kind) {
    return `<div class="chips" id="${id}">` + options.map(o =>
      `<button type="button" class="chip${selected.includes(o) ? " sel" : ""}" data-v="${esc(o)}"
        onclick="this.classList.toggle('sel')">${esc(kind ? v(kind, o) : o)}</button>`).join("") + `</div>`;
  }
  function chipValues(groupId) {
    return [...document.querySelectorAll(`#${groupId} .chip.sel`)].map(c => c.dataset.v);
  }

  const STATUS_TONE = { requested: "grey", assigned: "gold", accepted: "green", in_progress: "gold", completed: "green", cancelled: "grey" };
  const statusPill = s => STATUS_TONE[s]
    ? `<span class="pill ${STATUS_TONE[s]}">${esc(t("status." + s))}</span>`
    : `<span class="pill grey">${esc(s)}</span>`;

  const initials = name => (name || "?").split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();

  /* Best display handle for a user: they may have joined by email or by phone,
     so either field can be empty. Never render a bare "null". */
  const contact = u => (u && (u.email || u.phone)) || t("common.nocontact");

  /* Every screen showing a dollar figure must carry this. The numbers are pilot
     estimates from assumptions.json, not billed amounts — saying so once, in one
     component, means it can't be forgotten on a screen. The English wording is
     the coordinator's (assumptions.json); the Chinese one is ours. */
  function moneyNote() {
    const d = (App.config && App.config.money_disclaimer) || {};
    const short = lang === "zh" ? t("common.moneyshort") : (d.short || t("common.moneyshort"));
    const long = lang === "zh" ? t("common.moneylong") : (d.long || t("common.moneylong"));
    return `<p class="money-note">${esc(short)} — ${esc(long)}</p>`;
  }

  /* YYYY-MM-DD in the phone's local time — never toISOString(), which is UTC and
     is yesterday until 8am in Singapore. */
  function ymd(d = new Date()) {
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  function ymdIn(days) { const d = new Date(); d.setDate(d.getDate() + days); return ymd(d); }

  /* <option>s for a time <select>, 30-minute steps. */
  function timeOptions(selected, from = 7 * 60, to = 21 * 60) {
    const out = [];
    for (let m = from; m <= to; m += 30) {
      const v = String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0");
      out.push(`<option value="${v}"${v === selected ? " selected" : ""}>${v}</option>`);
    }
    return out.join("");
  }
  const minutesOf = hhmm => { const [h, m] = (hhmm || "0:0").split(":").map(Number); return h * 60 + m; };
  /* Same rule as the server: round UP to the half hour, floor 1 hour. */
  function hoursBetween(a, b) {
    const raw = (minutesOf(b) - minutesOf(a)) / 60;
    if (!(raw > 0)) return 0;
    return Math.max(1, Math.ceil(raw * 2) / 2);
  }

  /* Resize an image file to max `px` on the long side and return a JPEG data
     URL. Keeps uploads small enough to live in the database. */
  function shrinkImage(file, px = 320) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const url = URL.createObjectURL(file);
      img.onload = () => {
        const scale = Math.min(1, px / Math.max(img.width, img.height));
        const c = document.createElement("canvas");
        c.width = Math.max(1, Math.round(img.width * scale));
        c.height = Math.max(1, Math.round(img.height * scale));
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        resolve(c.toDataURL("image/jpeg", 0.8));
      };
      img.onerror = () => { URL.revokeObjectURL(url); reject(new Error(t("common.readphoto"))); };
      img.src = url;
    });
  }

  /* A file as a data URL (for PDFs and small images that go to the server as-is). */
  const readDataUrl = file => new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result); r.onerror = () => reject(new Error(t("common.readfile")));
    r.readAsDataURL(file);
  });

  /* "HH:MM" in the phone's local time from a server timestamp; "" if unparseable. */
  function hhmm(ts) {
    if (!ts) return "";
    const d = new Date(ts);
    if (isNaN(d)) return "";
    return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
  }

  const tierLabel = tier => ["urgent", "soon", "planned"].includes(tier) ? t("tier." + tier) : tier;

  return { el, esc, toast, screen, spin, appbar, chipGroup, pick, chipValue,
           chipMulti, chipValues, statusPill, initials, contact, moneyNote, hhmm, ymd, ymdIn,
           timeOptions, hoursBetween, shrinkImage, readDataUrl, tierLabel,
           t, v, terr, hrs, visitsN, setLang, storedLang, get lang() { return getLang(); },
           /* v1.6 callers read UI.TIER_LABEL[tier]; keep that shape, in the current language. */
           get TIER_LABEL() { return { urgent: t("tier.urgent"), soon: t("tier.soon"), planned: t("tier.planned") }; } };
})();
