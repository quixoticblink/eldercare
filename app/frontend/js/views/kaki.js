/* Kaki side of M-VISITS + M-USERS profile. */
const KakiView = (() => {

  async function home() {
    UI.spin();
    try {
      const visits = await Api.get("/visits");
      const open = visits.filter(v => !["completed", "cancelled"].includes(v.status));
      const done = visits.filter(v => v.status === "completed");
      const hours = done.reduce((a, v) => a + (v.estimate?.hours || 2), 0);
      const earned = done.reduce((a, v) => a + (v.estimate ? v.estimate.kaki_fee + v.estimate.transport : 0), 0);
      UI.screen(`
        ${UI.appbar("Your visits", (App.user.name || "Kaki") + " · Pasir Ris · Tier 1")}
        ${open.length ? open.map(vRow).join("")
          : `<div class="card tint"><h3>No visits assigned yet</h3>
             <p>The coordinator matches visits to you based on your services and languages.
             Keep your profile current — and you'll hear as soon as a family needs you.</p></div>`}
        <p class="f-hint" style="margin:6px 4px 10px">You don't need to keep the app open — we message you when a visit is assigned or anything changes.</p>
        <div class="card tint" style="margin-top:10px">
          <div class="row"><div class="grow"><h3>Your impact</h3>
          <p>${done.length} visit${done.length === 1 ? "" : "s"} · ${hours} hrs · ~$${earned.toFixed(2)} earned</p></div>
          <button class="chip" onclick="location.hash='#/kaki/impact'">Impact →</button></div>
        </div>
        ${UI.moneyNote()}`);
    } catch (e) { UI.toast(e.message, true); }
  }

  function vRow(v) {
    return `<button class="li" onclick="location.hash='#/kaki/visit/${v.id}'">
      <div class="face${v.tier === "urgent" ? " gold" : ""}">${v.tier === "urgent" ? "⚡" : UI.initials(v.senior_name)}</div>
      <div class="body"><b>${UI.esc(v.service)} · ${UI.esc(v.date)} ${UI.esc(v.window || "")}${v.estimate ? " · $" + v.estimate.kaki_fee : ""}</b>
      <span>${UI.esc(v.senior_name)}${v.senior_age ? ", " + v.senior_age : ""} · ${UI.esc(v.address || "Pasir Ris")} · ${UI.esc(v.language)}${v.times_together ? ` · <b style="color:var(--pandan)">you've visited ${v.times_together}×</b>` : ""}</span></div>
      <div class="end">${UI.statusPill(v.status)}</div></button>`;
  }

  async function visit(id) {
    UI.spin();
    try {
      const v = await Api.get("/visits/" + id);
      const plan = v.care_plan || {};
      UI.screen(`
        ${UI.appbar(v.service, `${v.date} · ${v.window || ""} · ${UI.esc(v.senior_name)}`, "#/kaki/home")}
        <div class="row">${UI.statusPill(v.status)}<span class="pill grey">${UI.TIER_LABEL[v.tier] || v.tier}</span>
        <span class="pill green">${UI.esc((v.languages || [v.language]).join(", "))}</span></div>
        <div class="card" style="margin-top:12px">
          <h3>${UI.esc(v.senior_name)}${v.senior_age ? ", " + v.senior_age : ""}${v.times_together ? ` — you've visited ${v.times_together}×` : " — first visit"}</h3>
          <p>${UI.esc(v.address || "Pasir Ris")}</p>
          ${v.trigger ? `<p style="margin-top:4px"><b>Why:</b> ${UI.esc(v.trigger)}</p>` : ""}
          ${v.notes ? `<div class="divider"></div><p><b>From the family:</b> ${UI.esc(v.notes)}</p>` : ""}
          ${v.estimate ? `<div class="divider"></div><div class="row"><span class="pill gold">You receive ~$${(v.estimate.kaki_fee + v.estimate.transport).toFixed(2)}</span><span class="pill green">Cashless · weekly via Vanguard</span></div>${UI.moneyNote()}` : ""}
        </div>
        <div class="card tint">
          <h3>Care plan — read before you go</h3>
          <p>${plan.meds ? "💊 " + UI.esc(plan.meds) + "<br>" : ""}
             ${plan.mobility ? "🚶 " + UI.esc(plan.mobility) + "<br>" : ""}
             ${(plan.languages || []).length ? "🗣 " + plan.languages.map(UI.esc).join(", ") + "<br>" : ""}
             ${plan.notes ? "📝 " + UI.esc(plan.notes) : ""}</p>
          ${plan.contacts ? `<div class="divider"></div><p><b>Emergency:</b> ${UI.esc(plan.contacts)}</p>` : ""}
        </div>
        ${v.status === "assigned" ? `
          <button class="btn gold" id="acceptV">Accept this visit</button>
          <button class="btn ghost" id="declineV">I can't make it</button>` : ""}
        ${v.status === "accepted" ? `
          ${v.on_way_at
            ? `<div class="card tint"><p>On the way since <b>${UI.hhmm(v.on_way_at)}</b> — the family has been told.</p></div>`
            : `<button class="btn gold" id="onWayV">I'm on my way</button>
               <p class="f-hint" style="margin:-4px 4px 10px">Tap when you leave — the family gets a message so they're ready with the start code.</p>`}
          <div class="card warn"><h3>Start the visit</h3>
          <p>Ask the family to read you their 4-digit start code and enter it here. You will never
          see it in your own app — that is how we prove you were let in.</p>
          <div class="otp-in">${[0,1,2,3].map(i => `<input id="o${i}" inputmode="numeric" maxlength="1">`).join("")}</div>
          <button class="btn" id="startV">Start visit</button></div>` : ""}
        ${v.status === "in_progress" ? `
          <div class="card"><h3>End the visit</h3>
          <p>Tick what applies and add a short note — the family reads this.</p>
          ${UI.chipMulti("repChips", ["Went well", "Meal eaten", "Good spirits", "Seemed tired", "Meds issue"], ["Went well"])}
          <label class="f-label">Your note to the family</label>
          <textarea class="f-input" id="repTxt" placeholder="e.g. Went to the market, meds taken at 2pm, left them with tea."></textarea>
          ${plan.meds ? `<div class="chips" id="medsG" style="margin-top:10px">
            <button type="button" class="chip sel" onclick="this.classList.toggle('sel')" data-v="meds">Meds confirmed ✓</button></div>` : ""}
          <button class="btn" id="endV">Complete visit</button></div>` : ""}
        ${v.status === "completed" && v.report ? `
          <div class="card tint"><h3>Your report</h3><p>${UI.esc(v.report.text || "")}</p></div>
          <button class="li" id="flagC"><div class="face gold">⚑</div>
            <div class="body"><b>Flag a concern</b><span>About the senior's wellbeing — or how you were treated. Goes privately to the care team.</span></div></button>` : ""}
      `);
      const ow = UI.el("onWayV");
      if (ow) ow.onclick = async () => { try { await Api.post(`/visits/${id}/on-the-way`); UI.toast("The family has been told you're on the way"); visit(id); } catch (e) { UI.toast(e.message, true); } };
      const a = UI.el("acceptV");
      if (a) a.onclick = async () => { try { await Api.post(`/visits/${id}/accept`); UI.toast("Confirmed — see you there"); visit(id); } catch (e) { UI.toast(e.message, true); } };
      const d = UI.el("declineV");
      if (d) d.onclick = async () => { try { await Api.post(`/visits/${id}/decline`); UI.toast("Passed back to the coordinator"); location.hash = "#/kaki/home"; } catch (e) { UI.toast(e.message, true); } };
      [0,1,2,3].forEach(i => { const o = UI.el("o" + i); if (o) o.oninput = () => { if (o.value && i < 3) UI.el("o" + (i + 1)).focus(); }; });
      const s = UI.el("startV");
      if (s) s.onclick = async () => {
        const otp = [0,1,2,3].map(i => UI.el("o" + i).value).join("");
        try { await Api.post(`/visits/${id}/start`, { otp }); UI.toast("Visit started ✓"); visit(id); }
        catch (e) { UI.toast(e.message, true); }
      };
      const en = UI.el("endV");
      if (en) en.onclick = async () => {
        try {
          await Api.post(`/visits/${id}/complete`, {
            chips: UI.chipValues("repChips"), text: UI.el("repTxt").value,
            meds_confirmed: UI.el("medsG") ? UI.chipValues("medsG").includes("meds") : false });
          UI.toast("Visit completed — thank you 🌱"); visit(id);
        } catch (e) { UI.toast(e.message, true); }
      };
      const f = UI.el("flagC");
      if (f) f.onclick = async () => {
        const text = prompt("What should the care team know? (kept private)");
        if (!text) return;
        try { await Api.post(`/visits/${id}/care-note`, { chips: ["Kaki concern"], text }); UI.toast("Sent privately to the care team ✓"); }
        catch (e) { UI.toast(e.message, true); }
      };
    } catch (e) { UI.toast(e.message, true); }
  }

  async function impact() {
    UI.spin();
    try {
      const visits = await Api.get("/visits");
      const done = visits.filter(v => v.status === "completed");
      const byHousehold = {};
      done.forEach(v => { byHousehold[v.senior_name] = (byHousehold[v.senior_name] || 0) + 1; });
      const repeats = Object.values(byHousehold).filter(c => c > 1).reduce((a, c) => a + c, 0);
      const hours = done.reduce((a, v) => a + (v.estimate?.hours || 2), 0);
      const earned = done.reduce((a, v) => a + (v.estimate ? v.estimate.kaki_fee + v.estimate.transport : 0), 0);
      UI.screen(`
        ${UI.appbar("My impact", "What your visits meant")}
        <div class="card" style="background:linear-gradient(150deg,var(--pandan),var(--pandan-deep));color:#fff;border:0">
          <div class="row" style="text-align:center">
            <div class="grow"><div class="mono" style="font-size:1.6rem">$${earned.toFixed(0)}</div><div style="font-size:.7rem;opacity:.85">earned (est.)</div></div>
            <div class="grow"><div class="mono" style="font-size:1.6rem">${hours}</div><div style="font-size:.7rem;opacity:.85">hours</div></div>
            <div class="grow"><div class="mono" style="font-size:1.6rem">${Object.keys(byHousehold).length}</div><div style="font-size:.7rem;opacity:.85">seniors</div></div>
          </div>
        </div>
        ${repeats ? `<div class="li"><div class="face">🔁</div><div class="body"><b>Consistency streak: ${repeats} repeat visits</b>
          <span>Seniors do best with faces they know — you're one of them</span></div></div>` : ""}
        ${Object.entries(byHousehold).map(([n, c]) => `<div class="li"><div class="face">${UI.initials(n)}</div>
          <div class="body"><b>${UI.esc(n)}</b><span>${c} visit${c === 1 ? "" : "s"} together</span></div></div>`).join("")}
        <div class="card tint"><h3>Payouts</h3><p>During the pilot, payouts run weekly via Vanguard to your PayNow. Questions — call the coordinator.</p></div>
        ${UI.moneyNote()}`);
    } catch (e) { UI.toast(e.message, true); }
  }

  async function profile() {
    UI.spin();
    try {
      const p = await Api.get("/users/me/profile");
      const k = p.kaki || { services: [], languages: [] };
      UI.screen(`
        ${UI.appbar("My profile", "The coordinator matches you by this")}
        <div class="li"><div class="face" style="width:52px;height:52px">${UI.initials(p.name)}</div>
          <div class="body"><b>${UI.esc(p.name || p.email)}</b><span>Tier ${k.tier || 1} · Good standing · ${UI.esc(p.email)}</span></div></div>
        <label class="f-label">Name</label>
        <input class="f-input" id="pname" value="${UI.esc(p.name)}">
        <label class="f-label">Phone</label>
        <input class="f-input" id="pphone" inputmode="tel" value="${UI.esc(p.phone)}" placeholder="+65 …">
        <label class="f-label">Services I can help with</label>
        ${UI.chipMulti("svcG", App.config.services, k.services)}
        <label class="f-label">Languages I speak</label>
        ${UI.chipMulti("langG", App.config.languages, k.languages)}
        <button class="btn" id="saveP">Save profile</button>
        <button class="li" onclick="location.hash='#/kaki/availability'">
          <div class="face">◷</div><div class="body"><b>When I can work</b>
          <span>${(k.availability && k.availability.any_set)
            ? Object.entries(k.availability.weekly).filter(([, s]) => s.length)
                .map(([d, s]) => d + " " + s.map(x => x[0].toUpperCase()).join("")).join(" · ")
            : "Not set yet — the coordinator can't tell when you're free"}</span></div>
          <div class="end"><span class="pill ${(k.availability && k.availability.any_set) ? "green" : "gold"}">
            ${(k.availability && k.availability.any_set) ? "Set" : "Add"}</span></div></button>
        <div class="eyebrow">Training & certificates · Tier ${k.tier || 1}</div>
        <div class="li"><div class="body"><b>CPR + AED</b><span class="mono">External cert · St. Luke's Hospital</span></div><span class="pill green">Valid</span></div>
        <div class="li"><div class="body"><b>Mobility assistance</b><span class="mono">Half-day · Vanguard in-house</span></div><span class="pill green">Valid</span></div>
        <div class="li"><div class="body"><b>Working with seniors + SOPs</b><span class="mono">Vanguard in-house</span></div><span class="pill green">Valid</span></div>
        <div class="card tint"><h3>Tier 2 within reach</h3><p>Complete dementia basics to unlock dementia-care visits — ask the coordinator to book you in.</p></div>
        <button class="btn ghost" onclick="App.logout()">Sign out</button>`);
      UI.el("saveP").onclick = async () => {
        try {
          await Api.put("/users/me", { name: UI.el("pname").value.trim(), phone: UI.el("pphone").value.trim(),
            services: UI.chipValues("svcG"), languages: UI.chipValues("langG") });
          App.user.name = UI.el("pname").value.trim();
          UI.toast("Profile saved ✓");
        } catch (e) { UI.toast(e.message, true); }
      };
    } catch (e) { UI.toast(e.message, true); }
  }

  /* Availability: a normal week plus dated exceptions. Most kakis work
     elsewhere, so "Tue and Sat mornings, but I'm away on the 12th" is the
     shape that actually matches their lives. */
  async function availability() {
    UI.spin();
    try {
      const a = await Api.get("/users/me/availability");
      const days = App.config.weekdays || ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
      const halves = App.config.half_days || ["morning", "afternoon"];
      const win = a.half_day_windows || {};
      const on = (d, h) => ((a.weekly || {})[d] || []).includes(h);

      UI.screen(`
        ${UI.appbar("When I can work", "The coordinator matches visits to this", "#/kaki/profile")}
        <div class="card tint"><p>Tick the half-days you're usually free. You don't have to be
        available every week — mark days off below when something comes up.</p></div>

        <div class="eyebrow">My normal week</div>
        <div class="avail-grid">
          <span></span>
          <span class="hdr">Morning<br><small>${UI.esc(win.morning || "")}</small></span>
          <span class="hdr">Afternoon<br><small>${UI.esc(win.afternoon || "")}</small></span>
          ${days.map(d => `
            <span class="day">${UI.esc(d)}</span>
            ${halves.map(h => `<div class="slot${on(d, h) ? " sel" : ""}" data-d="${d}" data-h="${h}"
              onclick="this.classList.toggle('sel')">${on(d, h) ? "✓" : ""}</div>`).join("")}
          `).join("")}
        </div>
        <label class="f-label" for="availNote">Anything the coordinator should know</label>
        <input class="f-input" id="availNote" value="${UI.esc(a.note || "")}"
          placeholder="e.g. I can do urgent visits at short notice on weekends">
        <button class="btn" id="saveAvail">Save my week</button>

        <div class="eyebrow">Days off and extra days</div>
        ${(a.exceptions || []).length ? (a.exceptions || []).map(e => `
          <div class="li"><div class="face">${e.available ? "＋" : "✕"}</div>
            <div class="body"><b>${UI.esc(e.date)} · ${UI.esc(e.half_day)}</b>
            <span>${e.available ? "Extra availability" : "Not available"}${e.note ? " · " + UI.esc(e.note) : ""}</span></div>
            <div class="end"><button class="chip" onclick="KakiView.dropException('${e.id}')">Remove</button></div>
          </div>`).join("")
        : `<div class="card tint"><p>None yet — your normal week applies every week.</p></div>`}

        <div class="card">
          <h3>Add a date</h3>
          <label class="f-label" for="exDate">Date</label>
          <input class="f-input" id="exDate" type="date">
          <label class="f-label">Which part of the day</label>
          ${UI.chipGroup("exHalf", ["all", "morning", "afternoon"], "all")}
          <label class="f-label">Am I working?</label>
          ${UI.chipGroup("exAvail", ["Not available", "Extra availability"], "Not available")}
          <label class="f-label" for="exNote">Reason <small>· optional</small></label>
          <input class="f-input" id="exNote" placeholder="e.g. Away in JB">
          <button class="btn quiet" id="addEx">Add this date</button>
        </div>`);

      UI.el("saveAvail").onclick = async () => {
        const weekly = {};
        document.querySelectorAll(".avail-grid .slot.sel").forEach(s => {
          (weekly[s.dataset.d] = weekly[s.dataset.d] || []).push(s.dataset.h);
        });
        try {
          await Api.put("/users/me/availability", { weekly, note: UI.el("availNote").value.trim() });
          UI.toast("Availability saved ✓");
          availability();
        } catch (e) { UI.toast(e.message, true); }
      };

      UI.el("addEx").onclick = async () => {
        const date = UI.el("exDate").value;
        if (!date) return UI.toast("Pick a date", true);
        try {
          await Api.post("/users/me/availability/exceptions", {
            date, half_day: UI.chipValue("exHalf") || "all",
            available: UI.chipValue("exAvail") === "Extra availability",
            note: UI.el("exNote").value.trim() });
          UI.toast("Saved ✓");
          availability();
        } catch (e) { UI.toast(e.message, true); }
      };
    } catch (e) { UI.toast(e.message, true); }
  }

  async function dropException(id) {
    try { await Api.del(`/users/me/availability/exceptions/${id}`); UI.toast("Removed"); availability(); }
    catch (e) { UI.toast(e.message, true); }
  }

  return { home, visit, impact, profile, availability, dropException };
})();
