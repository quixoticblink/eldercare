/* M-CORE · ui.js — DOM helpers and small components. No fetch, no routing. */
const UI = (() => {
  const el = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

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
      ${backHash ? `<button class="back" onclick="location.hash='${backHash}'" aria-label="Back">←</button>` : ""}
      <h1>${esc(title)}${sub ? `<span class="sub">${esc(sub)}</span>` : ""}</h1>
    </div>`;
  }

  /* single-select chip group; value read via UI.chipValue(groupId) */
  function chipGroup(id, options, selected) {
    return `<div class="chips" id="${id}">` + options.map(o =>
      `<button type="button" class="chip${o === selected ? " sel" : ""}" data-v="${esc(o)}"
        onclick="UI.pick('${id}', this)">${esc(o)}</button>`).join("") + `</div>`;
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
  function chipMulti(id, options, selected = []) {
    return `<div class="chips" id="${id}">` + options.map(o =>
      `<button type="button" class="chip${selected.includes(o) ? " sel" : ""}" data-v="${esc(o)}"
        onclick="this.classList.toggle('sel')">${esc(o)}</button>`).join("") + `</div>`;
  }
  function chipValues(groupId) {
    return [...document.querySelectorAll(`#${groupId} .chip.sel`)].map(c => c.dataset.v);
  }

  const STATUS_PILL = {
    requested: '<span class="pill grey">Finding a kaki</span>',
    assigned: '<span class="pill gold">Kaki assigned</span>',
    accepted: '<span class="pill green">Confirmed</span>',
    in_progress: '<span class="pill gold">Happening now</span>',
    completed: '<span class="pill green">Completed</span>',
    cancelled: '<span class="pill grey">Cancelled</span>',
  };
  const statusPill = s => STATUS_PILL[s] || `<span class="pill grey">${esc(s)}</span>`;

  const initials = name => (name || "?").split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();

  /* Best display handle for a user: they may have joined by email or by phone,
     so either field can be empty. Never render a bare "null". */
  const contact = u => (u && (u.email || u.phone)) || "no contact on file";

  /* Every screen showing a dollar figure must carry this. The numbers are pilot
     estimates from assumptions.json, not billed amounts — saying so once, in one
     component, means it can't be forgotten on a screen. */
  function moneyNote() {
    const d = (App.config && App.config.money_disclaimer) || {};
    return `<p class="money-note">${esc(d.short || "For illustration only")} —
      ${esc(d.long || "figures are pilot estimates, not billed amounts.")}</p>`;
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
      img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("Couldn't read that photo")); };
      img.src = url;
    });
  }

  /* "HH:MM" in the phone's local time from a server timestamp; "" if unparseable. */
  function hhmm(ts) {
    if (!ts) return "";
    const d = new Date(ts);
    if (isNaN(d)) return "";
    return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
  }

  const TIER_LABEL = { urgent: "Urgent · within the hour", soon: "Soon · within 2 hours", planned: "Planned" };

  return { el, esc, toast, screen, spin, appbar, chipGroup, pick, chipValue,
           chipMulti, chipValues, statusPill, initials, contact, moneyNote, hhmm, ymd, ymdIn,
           timeOptions, hoursBetween, shrinkImage, TIER_LABEL };
})();
