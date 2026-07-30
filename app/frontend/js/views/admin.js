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
            <div class="grow"><div class="mono" style="font-size:1.6rem">${ov.pending_users}</div><div style="font-size:.68rem;opacity:.85">awaiting approval</div></div>
            <div class="grow"><div class="mono" style="font-size:1.6rem">${ov.open_requests}</div><div style="font-size:.68rem;opacity:.85">to match</div></div>
            <div class="grow"><div class="mono" style="font-size:1.6rem">${ov.active_visits}</div><div style="font-size:.68rem;opacity:.85">active visits</div></div>
            <div class="grow"><div class="mono" style="font-size:1.6rem">${ov.completed}</div><div style="font-size:.68rem;opacity:.85">completed</div></div>
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
            <div class="row"><h3 class="grow">${UI.esc(u.name || u.email)}</h3><span class="pill gold">Pending</span></div>
            <p>${UI.esc(u.email)} · wants to join as <b>${UI.esc(u.role || "…not chosen yet")}</b></p>
            <div class="divider"></div>
            <div class="row">
              <button class="btn quiet" style="margin:0" onclick="AdminView.approve('${u.id}','caregiver')">Approve as caregiver</button>
              <button class="btn quiet" style="margin:0" onclick="AdminView.approve('${u.id}','kaki')">Approve as kaki</button>
            </div>
          </div>`).join("") : `<div class="card tint"><p>No one waiting — all clear.</p></div>`}
        <div class="eyebrow">Everyone (${all.length})</div>
        ${all.map(u => `<div class="li"><div class="face">${UI.initials(u.name || u.email)}</div>
          <div class="body"><b>${UI.esc(u.name || u.email)}</b>
          <span>${UI.esc(u.role || "no role")} · ${UI.esc(u.email)}${u.kaki ? " · " + (u.kaki.services || []).join(", ") : ""}</span></div>
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
      const kakis = await Api.get("/admin/kakis");
      window._kakis = kakis;
      const tierRank = { urgent: 0, soon: 1, planned: 2 };
      open.sort((a, b) => (tierRank[a.tier] ?? 3) - (tierRank[b.tier] ?? 3));
      UI.screen(`
        ${UI.appbar("Match requests", "Urgent first · pick the kaki with history where you can", "#/admin/home")}
        ${open.length ? open.map(v => `
          <div class="card${v.tier === "urgent" ? " warn" : ""}">
            <div class="row" style="flex-wrap:wrap"><h3 class="grow">${UI.esc(v.service)} · ${UI.esc(v.senior_name)}</h3>
              <span class="pill ${v.tier === "urgent" ? "clay" : v.tier === "soon" ? "gold" : "grey"}">${UI.esc(v.tier)}</span>
              ${v.trigger ? `<span class="pill gold">${UI.esc(v.trigger)}</span>` : ""}</div>
            <p>${UI.esc(v.date)} ${UI.esc(v.window || "")} · ${UI.esc(v.language)} · by ${UI.esc(v.caregiver?.name || v.caregiver?.email || "")}</p>
            ${v.notes ? `<p style="margin-top:6px"><b>Note:</b> ${UI.esc(v.notes)}</p>` : ""}
            <div class="divider"></div>
            ${kakis.length ? `<div class="chips">
              ${kakis.map(k => {
                const history = (k.done_with || {})[v.household_id];
                const langOk = (k.languages || []).includes(v.language);
                const svcOk = (k.services || []).includes(v.service);
                const hint = [history ? `${history}× with this senior` : null, langOk ? v.language + " ✓" : null,
                              svcOk ? null : "service not set", k.active ? `${k.active} active` : "free"].filter(Boolean).join(" · ");
                return `<button class="chip" onclick="AdminView.assign('${v.id}','${k.id}')">${UI.esc(k.name || k.email)}<small style="font-weight:400"> — ${hint}</small></button>`;
              }).join("")}</div>`
            : `<p>No approved kakis yet — approve one first.</p>`}
          </div>`).join("") : `<div class="card tint"><p>Nothing to match — all requests are assigned.</p></div>`}
        ${active.length ? `<div class="eyebrow">Active</div>` + active.map(v => `
          <div class="li"><div class="face">${UI.initials(v.kaki?.name)}</div>
          <div class="body"><b>${UI.esc(v.service)} · ${UI.esc(v.senior_name)}</b>
          <span>${UI.esc(v.kaki?.name || "")} · ${UI.esc(v.date)} ${UI.esc(v.window || "")}</span></div>
          <div class="end">${UI.statusPill(v.status)}</div></div>`).join("") : ""}`);
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

  return { home, approvals, approve, suspend, requests, assign, quality };
})();
