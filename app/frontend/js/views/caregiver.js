/* M-CARE + caregiver side of M-VISITS. */
const CareView = (() => {
  let bookDraft = {};

  async function home() {
    UI.spin();
    try {
      const { household, plan } = await Api.get("/care/household");
      if (!household) return setup();
      const visits = await Api.get("/visits");
      const open = visits.filter(v => !["completed", "cancelled"].includes(v.status));
      const done = visits.filter(v => v.status === "completed").slice(0, 3);
      UI.screen(`
        ${UI.appbar("Hello, " + (App.user.name || "there"), "Caring for " + household.senior_name)}
        <button class="btn gold" style="min-height:60px;font-size:1.05rem" onclick="location.hash='#/care/book'">Book a visit for ${UI.esc(household.senior_name)}</button>
        ${open.length ? `<div class="eyebrow">Current visits</div>` + open.map(vRow).join("") : ""}
        <div class="eyebrow">Care plan</div>
        <button class="li" onclick="location.hash='#/care/plan'">
          <div class="face">📋</div>
          <div class="body"><b>${UI.esc(household.senior_name)}'s care plan</b>
          <span>${UI.esc(plan?.meds || "Add medications")} · ${UI.esc(plan?.mobility || "mobility")} — every kaki sees this before a visit</span></div>
          <span class="pill green">Edit</span>
        </button>
        ${done.length ? `<div class="eyebrow">Recent</div>` + done.map(vRow).join("") : ""}
        <div class="helpline">Need help? Call <b>Pasir Ris ICCP · 6XXX XXXX</b></div>`);
    } catch (e) { UI.toast(e.message, true); }
  }

  function vRow(v) {
    const who = v.kaki ? `with ${v.kaki.name}` : "matching in progress";
    return `<button class="li" onclick="location.hash='#/care/visit/${v.id}'">
      <div class="face${v.tier === "urgent" ? " gold" : ""}">${v.kaki ? UI.initials(v.kaki.name) : "…"}</div>
      <div class="body"><b>${UI.esc(v.service)} · ${UI.esc(v.date)} ${UI.esc(v.window || "")}</b>
      <span>${UI.esc(who)}</span></div>
      <div class="end">${UI.statusPill(v.status)}</div></button>`;
  }

  function setup() {
    UI.screen(`
      ${UI.appbar("Set up your care circle", "Who are you caring for?")}
      <label class="f-label">Their name</label>
      <input class="f-input" id="sn" placeholder="e.g. Mr Nathan">
      <label class="f-label">Their age</label>
      <input class="f-input" id="sa" inputmode="numeric" placeholder="e.g. 78">
      <label class="f-label">Address <small>· Pasir Ris pilot area</small></label>
      <input class="f-input" id="ad" placeholder="Blk & street">
      <button class="btn" id="saveHh">Continue</button>`);
    UI.el("saveHh").onclick = async () => {
      const name = UI.el("sn").value.trim();
      if (!name) return UI.toast("Their name, please", true);
      try {
        await Api.put("/care/household", { senior_name: name,
          senior_age: parseInt(UI.el("sa").value) || null, address: UI.el("ad").value.trim() });
        UI.toast("Saved — now the care plan");
        location.hash = "#/care/plan";
      } catch (e) { UI.toast(e.message, true); }
    };
  }

  async function planEdit() {
    UI.spin();
    try {
      const { household, plan } = await Api.get("/care/household");
      if (!household) return setup();
      UI.screen(`
        ${UI.appbar(household.senior_name + "'s care plan", "Every kaki arrives briefed — keep this current", "#/care/home")}
        <label class="f-label">Medications & times</label>
        <textarea class="f-input" id="meds" placeholder="e.g. Metformin — 2:00pm daily, with food">${UI.esc(plan?.meds)}</textarea>
        <label class="f-label">Mobility</label>
        ${UI.chipGroup("mobG", ["Independent", "Walks with a stick", "Walking frame", "Wheelchair"], plan?.mobility || null)}
        <label class="f-label">Languages they speak</label>
        ${UI.chipMulti("langG", App.config.languages, plan?.languages || [])}
        <label class="f-label">Emergency contacts</label>
        <textarea class="f-input" id="contacts" placeholder="Name · relationship · phone">${UI.esc(plan?.contacts)}</textarea>
        <label class="f-label">Notes for any kaki</label>
        <textarea class="f-input" id="notes" placeholder="e.g. Gets anxious with new faces — introduce slowly">${UI.esc(plan?.notes)}</textarea>
        <button class="btn" id="savePlan">Save care plan</button>`);
      UI.el("savePlan").onclick = async () => {
        try {
          await Api.put("/care/plan", {
            meds: UI.el("meds").value, mobility: UI.chipValue("mobG") || "",
            languages: UI.chipValues("langG"), contacts: UI.el("contacts").value,
            notes: UI.el("notes").value });
          UI.toast("Care plan saved ✓");
          location.hash = "#/care/home";
        } catch (e) { UI.toast(e.message, true); }
      };
    } catch (e) { UI.toast(e.message, true); }
  }

  /* ---- booking flow: service → when → details ---- */
  function book() {
    bookDraft = {};
    UI.screen(`
      ${UI.appbar("What do they need?", "Pick a service — timing comes next", "#/care/home")}
      <span class="stepper">Step 1 of 3</span>
      ${[["🚶", "Chaperone", "Clinic, market, errands · usually 2–3 hrs"],
         ["☕", "Companionship", "Conversation, games, walks · 1–3 hrs"],
         ["🩺", "Wellness check", "Meals, meds, safety drop-in · ~1 hr"],
         ["🧺", "Household help", "Light chores · 1–2 hrs"]].map(([i, n, d]) =>
        `<button class="bigcard" onclick="CareView.pickService('${n}')">
          <span class="bc-ico">${i}</span><div><b>${n}</b><span>${d}</span></div></button>`).join("")}
      <div class="bigcard locked"><span class="bc-ico">💊</span>
        <div><b>Medicine administration</b><span>Tier 2 kakis only — ask the coordinator</span></div></div>`);
  }

  function pickService(s) { bookDraft.service = s; when(); }

  function when() {
    UI.screen(`
      ${UI.appbar("When?", bookDraft.service, "#/care/book")}
      <span class="stepper">Step 2 of 3</span>
      <button class="tier urgent" onclick="CareView.pickTier('urgent')">
        <div><b>Urgent — need someone now</b><span>A crisis or something sudden</span></div>
        <span class="t-eta">within<br>the hour</span></button>
      <button class="tier" onclick="CareView.pickTier('soon')">
        <div><b>Soon — something's come up</b><span>Within the next 2 hours</span></div>
        <span class="t-eta">~2 hrs</span></button>
      <button class="tier" onclick="CareView.pickTier('planned')">
        <div><b>Planned — book ahead</b><span>Pick a date and time</span></div>
        <span class="t-eta">this week<br>or later</span></button>`);
  }

  function pickTier(t) {
    bookDraft.tier = t; bookDraft.trigger = "";
    if (t === "planned") return details();
    triggers();
  }

  function triggers() {
    UI.screen(`
      ${UI.appbar("What happened?", "So the right help comes ready", "#/care/book")}
      <span class="stepper">Step 3 of 4 · ${bookDraft.tier}</span>
      <div class="eyebrow">Most common in Pasir Ris</div>
      ${[["🧳", "Helper left suddenly", "Bridging care while you find a replacement"],
         ["🏥", "Spouse hospitalised", "One parent in hospital, the other alone"],
         ["🆘", "My own emergency", "You're unwell or called away"],
         ["🛏️", "Discharge, no plan", "Coming home and nobody's ready"],
         ["📉", "Sudden decline", "A fall, surgery or illness"],
         ["🕊️", "Loss of a spouse", "Steady presence through hard months"]].map(([i, n, d]) =>
        `<button class="bigcard" onclick="CareView.pickTrigger('${n}')">
          <span class="bc-ico">${i}</span><div><b>${n}</b><span>${d}</span></div></button>`).join("")}
      <button class="li" onclick="location.href='tel:+6560000000'">
        <div class="face gold">📞</div>
        <div class="body"><b>Not sure — talk to someone</b><span>Call the Pasir Ris ICCP coordinator · 6XXX XXXX</span></div></button>
      <button class="btn ghost" onclick="CareView.pickTrigger('')">Skip — just need help</button>`);
  }

  function pickTrigger(t) { bookDraft.trigger = t; details(); }

  function details() {
    const planned = bookDraft.tier === "planned";
    const today = new Date().toISOString().slice(0, 10);
    UI.screen(`
      ${UI.appbar("The details", `${bookDraft.service} · ${UI.TIER_LABEL[bookDraft.tier]}${bookDraft.trigger ? " · " + bookDraft.trigger : ""}`, "#/care/book")}
      <span class="stepper">Step ${planned ? "3 of 3" : "4 of 4"}</span>
      ${planned ? `
        <label class="f-label">Date</label>
        <input class="f-input" id="date" type="date" min="${today}" value="${today}">
        <label class="f-label">Time window</label>
        ${UI.chipGroup("winG", ["Morning 9–12", "Afternoon 2–5", "Evening 5–8"], "Afternoon 2–5")}`
      : `
        <label class="f-label">Arrival window</label>
        ${UI.chipGroup("winG", bookDraft.tier === "urgent"
            ? ["Within the hour", "Today, 2–5pm"] : ["Within 2 hours", "Today, 2–5pm"],
          bookDraft.tier === "urgent" ? "Within the hour" : "Within 2 hours")}`}
      <label class="f-label">Language with them <small>· seniors settle faster in their own language</small></label>
      ${UI.chipGroup("langG2", App.config.languages, "English")}
      <label class="f-label">Anything the kaki should know?</label>
      <textarea class="f-input" id="notes" placeholder="e.g. Walks with a stick. Helper left suddenly."></textarea>
      <button class="btn gold" id="submitV">Request this visit</button>`);
    UI.el("submitV").onclick = async () => {
      try {
        const v = await Api.post("/visits", {
          service: bookDraft.service, tier: bookDraft.tier, trigger: bookDraft.trigger || "",
          date: planned ? UI.el("date").value : "today",
          window: UI.chipValue("winG") || "", language: UI.chipValue("langG2") || "English",
          notes: UI.el("notes").value });
        UI.toast("Request sent — the coordinator is matching a kaki");
        location.hash = "#/care/visit/" + v.id;
      } catch (e) { UI.toast(e.message, true); }
    };
  }

  async function visit(id) {
    UI.spin();
    try {
      const v = await Api.get("/visits/" + id);
      const steps = [
        ["Requested", true, ""],
        ["Kaki assigned", !!v.kaki, v.kaki ? `${v.kaki.name} — verified by the coordinator` : "The coordinator is matching…"],
        ["Confirmed", ["accepted", "in_progress", "completed"].includes(v.status), ""],
        ["Visit", v.status === "completed", v.status === "in_progress" ? "Happening now" : ""],
      ];
      const est = v.estimate;
      const active = ["assigned", "accepted", "in_progress"].includes(v.status);
      UI.screen(`
        ${UI.appbar(v.service, `${v.date} · ${v.window || ""} · ${UI.esc(v.senior_name)}`, "#/care/home")}
        <div class="row" style="flex-wrap:wrap">${UI.statusPill(v.status)}<span class="pill grey">${UI.TIER_LABEL[v.tier] || v.tier}</span>
        ${v.trigger ? `<span class="pill gold">${UI.esc(v.trigger)}</span>` : ""}</div>
        ${v.kaki ? `
          <div class="kakipass">
            <div class="kp-top">
              <div class="kp-face">${UI.initials(v.kaki.name)}</div>
              <div><h3>${UI.esc(v.kaki.name || "Your kaki")}</h3>
                <div class="kp-sub">${UI.esc(v.service)} · Pasir Ris</div>
                <div class="kp-meta"><span>Tier ${v.kaki.tier || 1} · verified</span>
                ${(v.kaki.languages || []).slice(0, 2).map(l => `<span>Speaks ${UI.esc(l)}</span>`).join("")}</div>
              </div>
            </div>
            <div class="kp-consist">${v.times_together > 0
              ? `${UI.esc(v.senior_name)} knows ${UI.esc((v.kaki.name || "them").split(" ")[0])} — <b>${v.times_together} visit${v.times_together === 1 ? "" : "s"} together</b>. No re-introduction needed.`
              : `A first visit — <b>the coordinator pairs first visits carefully</b>. Show this pass to ${UI.esc(v.senior_name)}.`}</div>
            <div class="kp-id">KAKI-PR04 · VERIFIED BY THE COORDINATOR · SHOW THIS PASS TO ${UI.esc((v.senior_name || "").toUpperCase())}</div>
          </div>` : ""}
        ${active ? `
          <div class="row" style="margin:4px 0 10px">
            <button class="btn quiet" style="margin:0;min-height:48px" onclick="location.href='tel:+6560000000'">📞 Coordinator</button>
            ${v.kaki && v.kaki.phone ? `<button class="btn quiet" style="margin:0;min-height:48px" onclick="location.href='tel:${UI.esc(v.kaki.phone)}'">💬 Call ${UI.esc((v.kaki.name || "kaki").split(" ")[0])}</button>` : ""}
          </div>` : ""}
        <ul class="tl" style="margin-top:8px">
          ${steps.map(([b, done, s], i) => `<li class="${done ? "done" : (i === steps.findIndex(x => !x[1]) ? "now" : "")}">
            <div><b>${b}</b>${s ? `<span>${UI.esc(s)}</span>` : ""}</div></li>`).join("")}
        </ul>
        ${["assigned", "accepted"].includes(v.status) && v.otp_code ? `
          <div class="card warn"><h3>Start code — read it to your kaki when they arrive</h3>
          <div class="codebox">${v.otp_code.split("").map(d => `<span>${d}</span>`).join("")}</div>
          <p>This is how we confirm the right person is really there.</p></div>` : ""}
        ${est && v.status !== "cancelled" ? `
          <div class="eyebrow">Estimated cost · pilot</div>
          <div class="stack">
            <div class="s-row"><span>Visit rate · ${est.hours} hr${est.hours > 1 ? "s" : ""} × $${est.rate}<span class="who">Standard ${UI.esc(v.service.toLowerCase())} rate</span></span><span class="amt">$${est.base.toFixed(2)}</span></div>
            <div class="s-row minus"><span>Community care subsidy<span class="who">Est. — confirmed by the coordinator</span></span><span class="amt">− $${est.subsidy.toFixed(2)}</span></div>
            <div class="s-row minus"><span>Foundation top-up<span class="who">Est. · means-tested</span></span><span class="amt">− $${est.foundation.toFixed(2)}</span></div>
            <div class="s-row total"><span>Family pays (est.)</span><span class="amt">$${est.family_pays.toFixed(2)}</span></div>
          </div>
          <p style="font-size:.74rem;color:var(--slate);margin:-6px 0 10px">Billed through your ICCP account during the pilot — nothing to pay in the app.</p>
          ${UI.moneyNote()}` : ""}
        ${v.status === "completed" && v.report ? `
          <div class="card"><h3>Visit report</h3>
            <p>${UI.esc(v.report.text || "")}</p><div class="divider"></div>
            <div class="row" style="flex-wrap:wrap">${(v.report.chips || []).map(c => `<span class="pill green">${UI.esc(c)}</span>`).join("")}
            ${v.report.meds_confirmed ? '<span class="pill green">Meds confirmed ✓</span>' : ""}</div></div>
          <div class="card tint"><h3>Private care note</h3>
            <p>Goes to the care team — never a public rating.</p>
            ${UI.chipMulti("noteChips", ["All fine", "Tired after visit", "Refused meds", "Fall concern", "New confusion"], [])}
            <textarea class="f-input" id="noteTxt" style="margin-top:10px" placeholder="Anything else…"></textarea>
            <button class="btn quiet" id="sendNote">Send care note</button></div>` : ""}
        ${["requested", "assigned", "accepted"].includes(v.status) ? `<button class="btn danger" id="cancelV">Cancel this visit</button>` : ""}
      `);
      const sn = UI.el("sendNote");
      if (sn) sn.onclick = async () => {
        try {
          await Api.post(`/visits/${id}/care-note`, { chips: UI.chipValues("noteChips"), text: UI.el("noteTxt").value });
          UI.toast("Care note sent to the care team ✓"); sn.disabled = true;
        } catch (e) { UI.toast(e.message, true); }
      };
      const cv = UI.el("cancelV");
      if (cv) cv.onclick = async () => {
        if (!confirm("Cancel this visit?")) return;
        try { await Api.post(`/visits/${id}/cancel`); UI.toast("Visit cancelled"); location.hash = "#/care/home"; }
        catch (e) { UI.toast(e.message, true); }
      };
    } catch (e) { UI.toast(e.message, true); }
  }

  async function visits(seg = "active") {
    UI.spin();
    try {
      const all = await Api.get("/visits");
      const act = all.filter(v => !["completed", "cancelled"].includes(v.status));
      const hist = all.filter(v => ["completed", "cancelled"].includes(v.status));
      const list = seg === "active" ? act : hist;
      UI.screen(`
        ${UI.appbar("Visits", "Everything booked for your family")}
        <div class="seg">
          <button class="${seg === "active" ? "on" : ""}" onclick="CareView.visits('active')">Active (${act.length})</button>
          <button class="${seg === "history" ? "on" : ""}" onclick="CareView.visits('history')">History (${hist.length})</button>
        </div>
        ${list.length ? list.map(vRow).join("")
          : `<div class="card tint"><p>${seg === "active" ? "Nothing active — book a visit from Home." : "No past visits yet."}</p></div>`}`);
    } catch (e) { UI.toast(e.message, true); }
  }

  return { home, setup, planEdit, book, pickService, when, pickTier, triggers, pickTrigger, details, visit, visits };
})();
