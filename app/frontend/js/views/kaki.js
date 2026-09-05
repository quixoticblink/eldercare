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
        ${UI.appbar(v.service, `${v.date} · ${v.window || ""}${v.hours ? ` · ${v.hours} hr${v.hours === 1 ? "" : "s"}` : ""} · ${UI.esc(v.senior_name)}`, "#/kaki/home")}
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
          <h3>${v.minimised ? "What you need for this visit" : "Care plan — read before you go"}</h3>
          ${v.minimised ? `<p class="f-hint" style="margin:0 0 8px">Care plan not shared for household visits — the family will tell you what they'd like done. Ask them or the coordinator if you need more.</p>` : ""}
          <p>${plan.meds ? "💊 " + UI.esc(plan.meds) + "<br>" : ""}
             ${plan.mobility ? "🚶 " + UI.esc(plan.mobility) + "<br>" : ""}
             ${(plan.languages || []).length ? "🗣 " + plan.languages.map(UI.esc).join(", ") + "<br>" : ""}
             ${plan.notes ? "📝 " + UI.esc(plan.notes) : ""}</p>
          ${plan.contact_name || plan.contact_phone ? `<div class="divider"></div><p><b>Emergency:</b> ${UI.esc(plan.contact_name || "")}${plan.contact_relationship ? " (" + UI.esc(plan.contact_relationship) + ")" : ""} · ${UI.esc(plan.contact_phone || "")}<br><small>They're messaged when you start and finish.</small></p>` : ""}
          ${plan.contacts ? `<div class="divider"></div><p><b>Other contacts:</b> ${UI.esc(plan.contacts)}</p>` : ""}
        </div>
        ${["assigned", "accepted"].includes(v.status) && v.kaki_code ? `
          <div class="card tint"><h3>Your code for the family</h3>
          <div class="codebox kakicode">${v.kaki_code.split("").map(d => `<span>${d}</span>`).join("")}</div>
          <p>At the door, show this screen with your photo. The family enters this code — that's how they know it's you — and then reads you their start code.</p></div>` : ""}
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
        ${["accepted", "in_progress"].includes(v.status) ? `
          <button class="btn ghost" id="cancelK">I have to cancel</button>
          <div class="card" id="cancelBox" hidden>
            <label class="f-label" for="cancelWhy">Tell the family why <small>· required</small></label>
            <textarea class="f-input" id="cancelWhy" placeholder="e.g. Fever this morning" maxlength="300"></textarea>
            <p class="f-hint">${v.status === "in_progress" ? "The visit ends now and is marked cancelled." : "The visit goes back to the coordinator to re-match."} Whether anything is paid for a cancelled visit is decided by the coordinator, not the app.</p>
            <button class="btn danger" id="cancelGo">Cancel this visit</button>
          </div>` : ""}
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
      const ck = UI.el("cancelK");
      if (ck) ck.onclick = () => { UI.el("cancelBox").hidden = false; ck.hidden = true; UI.el("cancelWhy").focus(); };
      const cg = UI.el("cancelGo");
      if (cg) cg.onclick = async () => {
        const reason = UI.el("cancelWhy").value.trim();
        if (!reason) return UI.toast("A few words for the family, please", true);
        try { await Api.post(`/visits/${id}/cancel`, { reason }); UI.toast("Cancelled — the family and coordinator have been told"); location.hash = "#/kaki/home"; }
        catch (e) { UI.toast(e.message, true); }
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
      const [p, certs] = await Promise.all([Api.get("/users/me/profile"), Api.get("/users/me/certificates")]);
      const k = p.kaki || { services: [], languages: [] };
      UI.screen(`
        ${UI.appbar("My profile", p.status === "approved" ? "The coordinator matches you by this" : "Waiting for approval — add your certificates", p.status === "approved" ? undefined : "#/")}
        <div class="li"><div class="face" style="width:52px;height:52px;overflow:hidden">${p.photo ? `<img src="${UI.esc(p.photo)}" alt="Your photo" style="width:100%;height:100%;object-fit:cover">` : UI.initials(p.name)}</div>
          <div class="body"><b>${UI.esc(p.name || UI.contact(p))}</b><span>Tier ${k.tier || 1} · Good standing · ${UI.esc(UI.contact(p))}</span></div>
          <div class="end"><label class="chip" for="photoIn" style="cursor:pointer">${p.photo ? "Change photo" : "Add a photo"}</label>
            <input type="file" id="photoIn" accept="image/*" capture="user" style="display:none"></div></div>
        <p class="f-hint">Families see your photo on the visit page, next to your code — it's how they know it's you at the door.</p>
        <label class="f-label">Name</label>
        <input class="f-input" id="pname" value="${UI.esc(p.name)}">
        <label class="f-label">Phone</label>
        <input class="f-input" id="pphone" inputmode="tel" value="${UI.esc(p.phone)}" placeholder="+65 …">
        <label class="f-label">I am <small>· some families ask for a woman or a man</small></label>
        ${UI.chipGroup("genG", ["Female", "Male", "Prefer not to say"], k.gender === "female" ? "Female" : k.gender === "male" ? "Male" : "Prefer not to say")}
        <label class="f-label">Services I can help with</label>
        ${UI.chipMulti("svcG", App.config.services, k.services)}
        <label class="f-label">Languages I speak</label>
        ${UI.chipMulti("langG", App.config.languages, k.languages)}
        <button class="btn" id="saveP">Save profile</button>
        <button class="li" onclick="location.hash='#/kaki/availability'">
          <div class="face">◷</div><div class="body"><b>When I can work</b>
          <span>${(k.availability && k.availability.any_set)
            ? Object.entries(k.availability.weekly_hours || {}).filter(([, r]) => r)
                .map(([d, r]) => `${d} ${r.from}–${r.to}`).join(" · ")
            : "Not set yet — the coordinator can't tell when you're free"}</span></div>
          <div class="end"><span class="pill ${(k.availability && k.availability.any_set) ? "green" : "gold"}">
            ${(k.availability && k.availability.any_set) ? "Set" : "Add"}</span></div></button>
        <div class="eyebrow">Training & certificates · Tier ${k.tier || 1}</div>
        ${certs.length ? certs.map(c => `
          <div class="li cert-row"><div class="face">📄</div>
            <div class="body"><b>${UI.esc(c.name)}</b><span class="mono">${UI.esc(c.issuer || "")}${c.expires ? " · until " + UI.esc(c.expires) : ""}${c.file_name ? " · " + UI.esc(c.file_name) : ""}</span></div>
            <div class="end"><button class="chip" onclick="KakiView.dropCertificate('${c.id}')">Remove</button></div></div>`).join("")
        : `<div class="card tint"><p>No certificates yet. Add CPR + AED, mobility assistance, or anything Vanguard has trained you in — the coordinator checks these before approving and matching.</p></div>`}
        <div class="card">
          <h3>Add a certificate</h3>
          <label class="f-label" for="certName">What is it <small>· required</small></label>
          <input class="f-input" id="certName" placeholder="e.g. CPR + AED" maxlength="80">
          <label class="f-label" for="certIssuer">Who issued it <small>· optional</small></label>
          <input class="f-input" id="certIssuer" placeholder="e.g. St. Luke's Hospital" maxlength="80">
          <label class="f-label" for="certExpires">Valid until <small>· optional</small></label>
          <input class="f-input" id="certExpires" type="date">
          <label class="f-label" for="certFile">The certificate <small>· PDF or a photo of it, up to 1 MB</small></label>
          <input class="f-input" id="certFile" type="file" accept="application/pdf,image/*">
          <button class="btn quiet" id="addCert">Add certificate</button>
        </div>
        <div class="card tint"><h3>Tier 2 within reach</h3><p>Complete dementia basics to unlock dementia-care visits — ask the coordinator to book you in.</p></div>
        <button class="btn ghost" onclick="App.logout()">Sign out</button>`);
      UI.el("addCert").onclick = async () => {
        const file = UI.el("certFile").files[0];
        const name = UI.el("certName").value.trim();
        if (!name) return UI.toast("Name the certificate first", true);
        if (!file) return UI.toast("Choose the PDF or photo", true);
        try {
          let dataUrl;
          if (file.type.startsWith("image/")) dataUrl = await UI.shrinkImage(file, 1200);
          else {
            if (file.size > 1024 * 1024) return UI.toast("That file is over 1 MB — a photo of the certificate is fine", true);
            dataUrl = await UI.readDataUrl(file);
          }
          await Api.post("/users/me/certificates", { name, issuer: UI.el("certIssuer").value.trim(),
            expires: UI.el("certExpires").value, file_name: file.name, data_url: dataUrl });
          UI.toast("Certificate added ✓"); profile();
        } catch (e) { UI.toast(e.message, true); }
      };
      UI.el("photoIn").onchange = async () => {
        const file = UI.el("photoIn").files[0];
        if (!file) return;
        try {
          const dataUrl = await UI.shrinkImage(file, 320);
          await Api.put("/users/me/photo", { data_url: dataUrl });
          UI.toast("Photo saved ✓"); profile();
        } catch (e) { UI.toast(e.message || "Couldn't read that photo", true); }
      };
      UI.el("saveP").onclick = async () => {
        try {
          const g = UI.chipValue("genG");
          await Api.put("/users/me", { name: UI.el("pname").value.trim(), phone: UI.el("pphone").value.trim(),
            services: UI.chipValues("svcG"), languages: UI.chipValues("langG"),
            gender: g === "Female" ? "female" : g === "Male" ? "male" : "" });
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
      const hrs = a.weekly_hours || {};

      UI.screen(`
        ${UI.appbar("When I can work", "The coordinator matches visits to this", "#/kaki/profile")}
        <div class="card tint"><p>Tick the days you're usually free and the hours. You don't have to be
        available every week — mark days off below when something comes up.</p></div>

        <div class="eyebrow">My normal week</div>
        ${days.map(d => {
          const on = !!hrs[d];
          return `<div class="li avail-day" style="align-items:center">
            <input type="checkbox" id="day-${d}" ${on ? "checked" : ""} aria-label="${d}" style="width:22px;height:22px;accent-color:var(--pandan)">
            <label for="day-${d}" style="width:42px;font-weight:600">${UI.esc(d)}</label>
            <select class="f-input" id="from-${d}" aria-label="${d} from" style="margin:0" ${on ? "" : "disabled"}>${UI.timeOptions(on ? hrs[d].from : "09:00")}</select>
            <span style="padding:0 4px">to</span>
            <select class="f-input" id="to-${d}" aria-label="${d} to" style="margin:0" ${on ? "" : "disabled"}>${UI.timeOptions(on ? hrs[d].to : "13:00")}</select>
          </div>`; }).join("")}
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

      days.forEach(d => {
        const cb = UI.el("day-" + d);
        cb.onchange = () => { UI.el("from-" + d).disabled = !cb.checked; UI.el("to-" + d).disabled = !cb.checked; };
      });

      UI.el("saveAvail").onclick = async () => {
        const weekly = {};
        days.forEach(d => {
          if (UI.el("day-" + d).checked) weekly[d] = { from: UI.el("from-" + d).value, to: UI.el("to-" + d).value };
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

  async function dropCertificate(id) {
    if (!confirm("Remove this certificate?")) return;
    try { await Api.del(`/users/me/certificates/${id}`); UI.toast("Removed"); profile(); }
    catch (e) { UI.toast(e.message, true); }
  }

  async function dropException(id) {
    try { await Api.del(`/users/me/availability/exceptions/${id}`); UI.toast("Removed"); availability(); }
    catch (e) { UI.toast(e.message, true); }
  }

  return { home, visit, impact, profile, availability, dropException, dropCertificate };
})();
