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

  const TIER_LABEL = { urgent: "Urgent · within the hour", soon: "Soon · within 2 hours", planned: "Planned" };

  return { el, esc, toast, screen, spin, appbar, chipGroup, pick, chipValue,
           chipMulti, chipValues, statusPill, initials, contact, TIER_LABEL };
})();
