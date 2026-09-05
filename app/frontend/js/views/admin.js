/* M-ADMIN · approvals, manual matching, quality. */
const AdminView = (() => {

  async function home() {
    UI.spin();
    try {
      const ov = await Api.get("/admin/overview");
      UI.screen(`
        ${UI.appbar("Today · Pasir Ris", "Coordinator console")}
        <div class="card" style="background:linear-gradient(150deg,var(--pandan),var(--pandan-deep));color:#fff;border:0">
          <div class="row" style="text-align:center">
            ${[[ov.pending_users, "awaiting approval", "#/admin/approvals"],
               [ov.open_requests, "to match", "#/admin/requests"],
               [ov.active_visits, "active visits", "#/admin/requests"],
               [ov.completed, "completed", "#/admin/quality"]].map(([n, label, hash]) =>
              `<button class="grow stat" onclick="location.hash='${hash}'" aria-label="${n} ${label}">
                 <div class="mono" style="font-size:1.6rem">${n}</div><div style="font-size:.68rem;opacity:.85">${label}</div></button>`).join("")}
          </div>
        </div>
        <button class="li" onclick="location.hash='#/admin/approvals'">
          <div class="face">✓</div><div class="body"><b>Approvals</b><span>New caregivers and kakis waiting for you</span></div>
          <div class="end">${ov.pending_users ? `<span class="pill clay">${ov.pending_users}</span>` : '<span class="pill green">Clear</span>'}</div></button>
        <button class="li" onclick="location.hash='#/admin/requests'">
          <div class="face">⚙</div><div class="body"><b>Match requests</b><span>Assign a kaki to each open request — manual in v1</span></div>
          <div class="end">${ov.open_requests ? `<span class="pill gold">${ov.open_requests}</span>` : '<span class="pill green">Clear</span>'}</div></button>
        <button class="li" onclick="location.hash='#/admin/quality'">
          <div class="face">❋</div><div class="body"><b>Quality</b><span>Visit reports and private care notes — never public ratings</span></div>
          <div class="end">${ov.care_notes ? `<span class="pill grey">${ov.care_notes}</span>` : ""}</div></button>
        <button class="li" onclick="location.hash='#/admin/settings'">
          <div class="face">⚙</div><div class="body"><b>Settings</b>
          <span>Auto-approval, auto-matching, service pricing and PayNow details</span></div></button>
        <button class="li" onclick="location.hash='#/admin/assumptions'">
          <div class="face">≈</div><div class="body"><b>Assumptions</b>
          <span>Every rate, hour and subsidy % behind the figures — and where each came from</span></div>
          <div class="end"><span class="pill grey">Illustrative</span></div></button>
        <div class="card tint"><h3>Hard rules</h3>
        <p>No public ratings of care staff (MOH) · certification gates tasks · urgent requests first · concerns go to a human.</p></div>`);
    } catch (e) { UI.toast(e.message, true); }
  }

  async function approvals() {
    UI.spin();
    try {
      const pend = await Api.get("/admin/pending-users");
      const all = await Api.get("/admin/users");
      UI.screen(`
        ${UI.appbar("Approvals", "You decide who's on the platform", "#/admin/home")}
        ${pend.length ? pend.map(u => `
          <div class="card warn" id="u-${u.id}">
            <div class="row"><h3 class="grow">${UI.esc(u.name || UI.contact(u))}</h3><span class="pill gold">Pending</span></div>
            <p>${UI.esc(UI.contact(u))} · wants to join as <b>${UI.esc(u.role || "…not chosen yet")}</b></p>
            <div class="divider"></div>
            <div class="row">
              <button class="btn quiet" style="margin:0" onclick="AdminView.approve('${u.id}','caregiver')">Approve as caregiver</button>
              <button class="btn quiet" style="margin:0" onclick="AdminView.approve('${u.id}','kaki')">Approve as kaki</button>
            </div>
          </div>`).join("") : `<div class="card tint"><p>No one waiting — all clear.</p></div>`}
        <div class="eyebrow">Everyone (${all.length})</div>
        ${all.map(u => `<div class="li"><div class="face">${UI.initials(u.name || UI.contact(u))}</div>
          <div class="body"><b>${UI.esc(u.name || UI.contact(u))}</b>
          <span>${UI.esc(u.role || "no role")} · ${UI.esc(UI.contact(u))}${u.kaki ? " · " + (u.kaki.services || []).join(", ") : ""}</span></div>
          <div class="end"><span class="pill ${u.status === "approved" ? "green" : u.status === "pending" ? "gold" : "clay"}">${u.status}</span>
          ${u.status === "approved" && u.role !== "admin" ? `<br><button class="chip" style="margin-top:6px;min-height:40px;padding:8px 12px;font-size:.78rem" onclick="AdminView.suspend('${u.id}')">Suspend</button>` : ""}
          ${u.status === "suspended" ? `<br><button class="chip" style="margin-top:6px;min-height:40px;padding:8px 12px;font-size:.78rem" onclick="AdminView.approve('${u.id}','${u.role || "caregiver"}')">Reinstate</button>` : ""}</div></div>`).join("")}`);
    } catch (e) { UI.toast(e.message, true); }
  }

  async function approve(uid, role) {
    try {
      await Api.post(`/admin/users/${uid}/approve`, { role });
      UI.toast(`Approved as ${role} ✓`);
      approvals();
    } catch (e) { UI.toast(e.message, true); }
  }

  async function suspend(uid) {
    if (!confirm("Suspend this user? They won't be able to book or serve visits until reinstated.")) return;
    try {
      await Api.post(`/admin/users/${uid}/suspend`);
      UI.toast("Suspended");
      approvals();
    } catch (e) { UI.toast(e.message, true); }
  }

  async function requests() {
    UI.spin();
    try {
      const visits = await Api.get("/visits");
      const open = visits.filter(v => v.status === "requested");
      const active = visits.filter(v => ["assigned", "accepted", "in_progress"].includes(v.status));
      const tierRank = { urgent: 0, soon: 1, planned: 2 };
      open.sort((a, b) => (tierRank[a.tier] ?? 3) - (tierRank[b.tier] ?? 3));

      /* Availability is scored per visit (date + window), so each open request
         gets its own ranked list rather than one shared roster. */
      const rosters = {};
      for (const v of open) rosters[v.id] = await Api.get(`/admin/kakis?visit_id=${encodeURIComponent(v.id)}`);

      UI.screen(`
        ${UI.appbar("Match requests", "Urgent first · choose a kaki, then confirm", "#/admin/home")}
        ${open.length ? open.map(v => {
          const roster = rosters[v.id] || [];
          return `
          <div class="card${v.tier === "urgent" ? " warn" : ""}">
            <div class="row" style="flex-wrap:wrap"><h3 class="grow">${UI.esc(v.service)} · ${UI.esc(v.senior_name)}</h3>
              <span class="pill ${v.tier === "urgent" ? "clay" : v.tier === "soon" ? "gold" : "grey"}">${UI.esc(v.tier)}</span>
              ${v.trigger ? `<span class="pill gold">${UI.esc(v.trigger)}</span>` : ""}
              ${v.kaki_gender_pref && v.kaki_gender_pref !== "any" ? `<span class="pill grey">${UI.esc(v.kaki_gender_pref)} kaki requested</span>` : ""}
              ${v.preferred_kaki ? `<span class="pill gold">asked for ${UI.esc(v.preferred_kaki.name)}</span>` : ""}</div>
            <p>${UI.esc(v.date)} ${UI.esc(v.window || "")} · ${UI.esc((v.languages || [v.language]).join(", "))} · by ${UI.esc(v.caregiver?.name || UI.contact(v.caregiver))}</p>
            ${v.notes ? `<p style="margin-top:6px"><b>Note:</b> ${UI.esc(v.notes)}</p>` : ""}
            <div class="divider"></div>
            ${roster.length ? `
              <div class="eyebrow" style="margin-top:0">Choose one kaki</div>
              ${roster.map(k => {
                const history = (k.done_with || {})[v.household_id];
                const langOk = k.language_ok !== undefined ? k.language_ok : (k.languages || []).includes(v.language);
                const svcOk = (k.services || []).includes(v.service);
                const fit = k.fit || { state: "unknown", why: "" };
                const pref = v.kaki_gender_pref && v.kaki_gender_pref !== "any" ? v.kaki_gender_pref : null;
                const meta = [
                  k.preferred ? "requested by the family" : null,
                  pref ? (k.gender_ok ? `${k.gender} · as requested` : `${k.gender || "gender not stated"} · does not match the family's preference`) : null,
                  history ? `${history}× with this senior` : null,
                  langOk ? `speaks ${UI.esc((v.languages || [v.language]).join("/"))}` : `no ${UI.esc((v.languages || [v.language]).join("/"))} on profile`,
                  svcOk ? null : "service not on profile",
                  k.active ? `${k.active} active visit${k.active === 1 ? "" : "s"}` : "no active visits",
                ].filter(Boolean).join(" · ");
                return `
                <label class="pick-row" onclick="AdminView.markPicked('${v.id}', this)">
                  <input type="radio" name="pick-${v.id}" value="${k.id}" data-name="${UI.esc(k.name || UI.contact(k))}">
                  <span class="grow">
                    <span class="who">${UI.esc(k.name || UI.contact(k))}</span>
                    <span class="fit ${fit.state}" style="margin-left:6px">${fit.state}${fit.why ? " · " + UI.esc(fit.why) : ""}</span>
                    <span class="meta">${meta}</span>
                  </span>
                </label>`;
              }).join("")}
              <button class="btn" onclick="AdminView.confirmAssign('${v.id}')">Assign selected kaki</button>`
            : `<p>No approved kakis yet — approve one first.</p>`}
          </div>`; }).join("") : `<div class="card tint"><p>Nothing to match — all requests are assigned.</p></div>`}
        ${active.length ? `<div class="eyebrow">Active</div>` + active.map(v => `
          <div class="li"><div class="face">${UI.initials(v.kaki?.name)}</div>
          <div class="body"><b>${UI.esc(v.service)} · ${UI.esc(v.senior_name)}</b>
          <span>assigned to <b>${UI.esc(v.kaki?.name || UI.contact(v.kaki))}</b> · ${UI.esc(v.date)} ${UI.esc(v.window || "")}</span></div>
          <div class="end">${UI.statusPill(v.status)}</div></div>`).join("") : ""}`);
    } catch (e) { UI.toast(e.message, true); }
  }

  /* Highlight the chosen row so the selection is visible before committing. */
  function markPicked(vid, row) {
    document.querySelectorAll(`.pick-row`).forEach(r => {
      const input = r.querySelector(`input[name="pick-${vid}"]`);
      if (input) r.classList.remove("sel");
    });
    row.classList.add("sel");
  }

  /* Explicit confirm naming the kaki. One-tap assignment used to send visits to
     whoever was tapped with no confirmation and no name in the toast, which is
     indistinguishable from the feature being broken when it goes to the wrong
     person. */
  async function confirmAssign(vid) {
    const picked = document.querySelector(`input[name="pick-${vid}"]:checked`);
    if (!picked) return UI.toast("Pick a kaki first", true);
    const who = picked.dataset.name;
    if (!confirm(`Assign this visit to ${who}?\n\nThey'll see it on their Visits screen straight away.`)) return;
    try {
      const r = await Api.post(`/admin/visits/${vid}/assign`, { kaki_id: picked.value });
      UI.toast(`Assigned to ${r.assigned_to?.name || who} ✓`);
      requests();
    } catch (e) { UI.toast(e.message, true); }
  }

  async function assign(vid, kid) {
    try {
      await Api.post(`/admin/visits/${vid}/assign`, { kaki_id: kid });
      UI.toast("Assigned ✓ — the kaki sees it now");
      requests();
    } catch (e) { UI.toast(e.message, true); }
  }

  async function quality() {
    UI.spin();
    try {
      const q = await Api.get("/admin/quality");
      UI.screen(`
        ${UI.appbar("Quality", "Reports + private notes — reviewed by a human", "#/admin/home")}
        <div class="eyebrow">Care notes (private)</div>
        ${q.notes.length ? q.notes.map(n => `
          <div class="li"><div class="face gold">⚑</div>
          <div class="body"><b>${(n.chips || []).map(UI.esc).join(" · ") || "Note"}</b>
          <span>${UI.esc(n.text || "")}</span></div></div>`).join("")
        : `<div class="card tint"><p>No care notes yet.</p></div>`}
        <div class="eyebrow">Visit reports</div>
        ${q.reports.length ? q.reports.map(r => `
          <div class="li"><div class="face">📝</div>
          <div class="body"><b>${UI.esc(r.service)} · ${UI.esc(r.date)}${r.meds_confirmed ? " · meds ✓" : ""}</b>
          <span>${(r.chips || []).map(UI.esc).join(" · ")}${r.text ? " — " + UI.esc(r.text) : ""}</span></div></div>`).join("")
        : `<div class="card tint"><p>No reports yet.</p></div>`}`);
    } catch (e) { UI.toast(e.message, true); }
  }

  /* The money and time figures behind every estimate, so the coordinator can
     see and challenge them without reading the code. */
  async function assumptions() {
    UI.spin();
    try {
      const a = await Api.get("/admin/assumptions");
      const row = (label, value, source, note) => `
        <div class="li"><div class="body">
          <b>${UI.esc(label)}</b>
          <span>${UI.esc(String(value))}${note ? " · " + UI.esc(note) : ""}</span>
          ${source ? `<span class="mono" style="font-size:.62rem;opacity:.75">${UI.esc(source)}</span>` : ""}
        </div></div>`;
      const svc = Object.entries(a.services || {}).map(([name, m]) => row(
        name,
        `${m.hours} hrs · family $${m.family_rate_per_hour}/hr · kaki $${m.kaki_rate_per_hour}/hr`,
        m.source, m.note)).join("");
      const sub = Object.entries(a.subsidies || {}).map(([k, m]) => row(
        k.replace(/_/g, " "), `${Math.round((m.value || 0) * 100)}%`, m.source, m.note)).join("");
      const pay = Object.entries(a.kaki_payment || {}).map(([k, m]) => row(
        k.replace(/_/g, " "), m.value, m.source, m.note)).join("");
      const time = Object.entries(a.time || {}).filter(([, m]) => m && typeof m === "object" && "value" in m)
        .map(([k, m]) => row(k.replace(/_/g, " "), m.value, m.source, m.note)).join("");

      UI.screen(`
        ${UI.appbar("Assumptions", "What every number in the app is built on", "#/admin/home")}
        <div class="card warn"><h3>${UI.esc((a.disclaimer || {}).short || "For illustration only")}</h3>
          <p>${UI.esc((a.disclaimer || {}).long || "")}</p>
          <p style="margin-top:6px" class="mono" style="font-size:.65rem">version ${UI.esc(a.version || "?")} · ${UI.esc(a.currency || "SGD")}</p></div>
        <div class="eyebrow">Services — hours and rates</div>${svc}
        <div class="eyebrow">Subsidies</div>${sub}
        <div class="eyebrow">Kaki payment</div>${pay}
        <div class="eyebrow">Time</div>${time}
        <div class="card tint"><h3>Changing these</h3>
          <p>Every figure lives in <span class="mono">app/assumptions.json</span> on the server.
          Edit that file and restart — no code change, no deploy. Anything marked
          <b>PLACEHOLDER</b> has not been confirmed with Vanguard or MOH.</p></div>`);
    } catch (e) { UI.toast(e.message, true); }
  }

  /* Settings: automation switches, the price stack, and PayNow details. */
  async function settings() {
    UI.spin();
    try {
      const [s, a] = await Promise.all([Api.get("/admin/settings"), Api.get("/admin/assumptions")]);
      const toggle = (key, on, title, sub) => `
        <label class="li" style="cursor:pointer">
          <div class="face">${on ? "●" : "○"}</div>
          <div class="body"><b>${UI.esc(title)}</b><span>${sub}</span></div>
          <div class="end"><input type="checkbox" id="${key}" ${on ? "checked" : ""}
            style="width:22px;height:22px;accent-color:var(--pandan)"></div>
        </label>`;

      const rateRows = Object.entries(a.services || {}).map(([name, m]) => `
        <div class="card" style="padding:12px">
          <b>${UI.esc(name)}</b>
          <div class="avail-grid" style="grid-template-columns:1fr 1fr 1fr">
            <span class="hdr">Hours</span><span class="hdr">Family $/hr</span><span class="hdr">Kaki $/hr</span>
            <input class="f-input" style="margin:0" type="number" min="0" step="0.5"
              data-svc="${UI.esc(name)}" data-f="hours" value="${m.hours}">
            <input class="f-input" style="margin:0" type="number" min="0" step="0.5"
              data-svc="${UI.esc(name)}" data-f="family_rate_per_hour" value="${m.family_rate_per_hour}">
            <input class="f-input" style="margin:0" type="number" min="0" step="0.5"
              data-svc="${UI.esc(name)}" data-f="kaki_rate_per_hour" value="${m.kaki_rate_per_hour}">
          </div>
          <span class="mono" style="font-size:.62rem;opacity:.7">${UI.esc(m.source || "")}</span>
        </div>`).join("");

      UI.screen(`
        ${UI.appbar("Settings", "Automation, pricing and payment", "#/admin/home")}

        <div class="eyebrow">Automation</div>
        <div class="card warn" style="padding:12px">
          <p style="font-size:.76rem">Each of these removes a human from a decision about who enters
          a vulnerable person's home. They are off unless you turn them on.</p>
        </div>
        ${toggle("auto_approve_caregiver", s.auto_approve_caregiver, "Auto-approve caregivers",
                 "New caregivers skip the approval queue and can book immediately")}
        ${toggle("auto_approve_kaki", s.auto_approve_kaki, "Auto-approve kakis",
                 "New kakis become bookable without a coordinator reviewing them first")}
        ${toggle("auto_match", s.auto_match, "Auto-match visits on booking",
                 "Assigns the best available kaki the moment a visit is booked. Never picks someone whose availability doesn't cover it — those stay for you")}
        <label class="f-label" for="maxAdv">Bookings open up to <small>· days ahead</small></label>
        <input class="f-input" id="maxAdv" type="number" min="1" max="365" value="${s.max_advance_days || 30}">
        <button class="btn" id="saveToggles">Save automation settings</button>
        <button class="btn quiet" id="sweepNow">Auto-match all open requests now</button>
        <p class="hint" style="font-size:.7rem;opacity:.8">The sweep runs on demand whether or not
        the toggle above is on — urgent requests first.</p>

        <div class="eyebrow">Pricing</div>
        ${rateRows}
        <button class="btn" id="saveRates">Save pricing</button>
        ${UI.moneyNote()}

        <div class="eyebrow">PayNow</div>
        <label class="f-label">Account type</label>
        ${UI.chipGroup("pnType", ["uen", "mobile"], s.paynow_type || "uen")}
        <label class="f-label" for="pnValue">${"UEN or mobile number"}</label>
        <input class="f-input" id="pnValue" value="${UI.esc(s.paynow_value || "")}"
          placeholder="e.g. 202512345K or +6598553704">
        <label class="f-label" for="pnName">Account name shown to families</label>
        <input class="f-input" id="pnName" value="${UI.esc(s.paynow_name || "")}"
          placeholder="e.g. Vanguard Healthcare Pte Ltd">
        <button class="btn" id="savePaynow">Save PayNow details</button>
        <p class="hint" style="font-size:.7rem;opacity:.8">Shown to caregivers on their visit cost
        screen. During the pilot billing still runs through the ICCP account — check with the
        coordinator before asking a family to transfer anything.</p>`);

      UI.el("saveToggles").onclick = async () => {
        try {
          await Api.put("/admin/settings", {
            auto_approve_caregiver: UI.el("auto_approve_caregiver").checked,
            auto_approve_kaki: UI.el("auto_approve_kaki").checked,
            auto_match: UI.el("auto_match").checked,
            max_advance_days: parseInt(UI.el("maxAdv").value) || 30 });
          UI.toast("Automation settings saved ✓"); settings();
        } catch (e) { UI.toast(e.message, true); }
      };

      UI.el("sweepNow").onclick = async () => {
        try {
          const r = await Api.post("/admin/auto-match");
          UI.toast(`Matched ${r.counts.matched}, left ${r.counts.unmatched} for you`);
        } catch (e) { UI.toast(e.message, true); }
      };

      UI.el("saveRates").onclick = async () => {
        const services = {};
        document.querySelectorAll("[data-svc]").forEach(i => {
          (services[i.dataset.svc] = services[i.dataset.svc] || {})[i.dataset.f] = parseFloat(i.value);
        });
        try {
          await Api.put("/admin/assumptions/services", { services });
          UI.toast("Pricing saved ✓"); settings();
        } catch (e) { UI.toast(e.message, true); }
      };

      UI.el("savePaynow").onclick = async () => {
        try {
          await Api.put("/admin/settings", {
            paynow_type: UI.chipValue("pnType") || "uen",
            paynow_value: UI.el("pnValue").value.trim(),
            paynow_name: UI.el("pnName").value.trim() });
          UI.toast("PayNow details saved ✓");
        } catch (e) { UI.toast(e.message, true); }
      };
    } catch (e) { UI.toast(e.message, true); }
  }

  return { home, approvals, approve, suspend, requests, assign, markPicked,
           confirmAssign, assumptions, settings, quality };
})();
