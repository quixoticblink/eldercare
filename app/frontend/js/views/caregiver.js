/* M-CARE + caregiver side of M-VISITS. */
const CareView = (() => {
  /* The booking draft survives a refresh. Seniors reload pages; losing three
     steps of input to a reload is what happened on 21 Aug. */
  const DRAFT_KEY = "kakis_book";
  let bookDraft = loadDraft();
  function loadDraft() { try { return JSON.parse(sessionStorage.getItem(DRAFT_KEY) || "{}") || {}; } catch (e) { return {}; } }
  function saveDraft() { try { sessionStorage.setItem(DRAFT_KEY, JSON.stringify(bookDraft)); } catch (e) {} }
  function clearDraft() { bookDraft = {}; try { sessionStorage.removeItem(DRAFT_KEY); } catch (e) {} }

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
        <div class="eyebrow">Care plan</div>
        <button class="li" onclick="location.hash='#/care/plan'">
          <div class="face">📋</div>
          <div class="body"><b>${UI.esc(household.senior_name)}'s care plan</b>
          <span>${UI.esc(plan?.meds || "Add medications")} · ${UI.esc(plan?.mobility || "mobility")} — every kaki sees this before a visit</span></div>
          <span class="pill green">Edit</span>
        </button>
        ${open.length ? `<div class="eyebrow">Current visits</div>` + open.map(vRow).join("") : ""}
        ${done.length ? `<div class="eyebrow">Recent</div>` + done.map(vRow).join("") : ""}
        <button class="li" onclick="location.hash='#/care/profile'">
          <div class="face">${UI.initials(App.user.name)}</div>
          <div class="body"><b>Your profile</b><span>${UI.esc(App.user.name || "")} · ${UI.esc(UI.contact(App.user))}</span></div>
          <span class="pill grey">Edit</span>
        </button>
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
        ${UI.chipGroup("mobG", ["Independent", "Walks with a stick", "Walking frame", "Wheelchair", "Bedridden"], plan?.mobility || null)}
        <label class="f-label">Languages they speak</label>
        ${UI.chipMulti("langG", App.config.languages, plan?.languages || [])}
        <label class="f-label">Emergency contact <small>· gets a message when a visit starts and ends</small></label>
        <input class="f-input" id="cName" value="${UI.esc(plan?.contact_name)}" placeholder="Name" aria-label="Contact name">
        <input class="f-input" id="cRel" value="${UI.esc(plan?.contact_relationship)}" placeholder="Relationship, e.g. son" aria-label="Contact relationship">
        <input class="f-input" id="cPhone" inputmode="tel" value="${UI.esc(plan?.contact_phone)}" placeholder="Mobile number" aria-label="Contact mobile number">
        ${plan?.contacts ? `<textarea class="f-input" id="contacts" aria-label="Other contacts">${UI.esc(plan.contacts)}</textarea>` : `<input type="hidden" id="contacts" value="">`}
        <label class="f-label">Notes for any kaki</label>
        <textarea class="f-input" id="notes" placeholder="e.g. Gets anxious with new faces — introduce slowly">${UI.esc(plan?.notes)}</textarea>
        <button class="btn" id="savePlan">Save care plan</button>`);
      UI.el("savePlan").onclick = async () => {
        try {
          await Api.put("/care/plan", {
            meds: UI.el("meds").value, mobility: UI.chipValue("mobG") || "",
            languages: UI.chipValues("langG"), contacts: UI.el("contacts").value,
            contact_name: UI.el("cName").value, contact_relationship: UI.el("cRel").value,
            contact_phone: UI.el("cPhone").value, notes: UI.el("notes").value });
          UI.toast("Care plan saved ✓");
          location.hash = "#/care/home";
        } catch (e) { UI.toast(e.message, true); }
      };
    } catch (e) { UI.toast(e.message, true); }
  }

  /* Caregivers could edit the care plan but not their own name or number (NCSS 2.1). */
  async function profile() {
    UI.spin();
    try {
      const p = await Api.get("/users/me/profile");
      UI.screen(`
        ${UI.appbar("Your profile", "How the coordinator and your kaki reach you", "#/care/home")}
        <label class="f-label" for="pname">Your name</label>
        <input class="f-input" id="pname" value="${UI.esc(p.name)}" autocomplete="name">
        <label class="f-label" for="pphone">Mobile number <small>· for visit messages</small></label>
        <input class="f-input" id="pphone" inputmode="tel" value="${UI.esc(p.phone)}" autocomplete="tel">
        <p class="f-hint">Signed in as ${UI.esc(UI.contact(p))}. To change that, call the coordinator.</p>
        <button class="btn" id="saveP">Save profile</button>`);
      UI.el("saveP").onclick = async () => {
        try {
          const r = await Api.put("/users/me", { name: UI.el("pname").value.trim(), phone: UI.el("pphone").value.trim() });
          App.user.name = r.name;
          UI.toast("Profile saved ✓");
        } catch (e) { UI.toast(e.message, true); }
      };
    } catch (e) { UI.toast(e.message, true); }
  }

  /* ---- booking flow: service → when → (what happened) → details ----
     Each step is its own hash route so back and refresh land on the step the
     person was on. */
  function book() {
    clearDraft();
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

  function pickService(s) { bookDraft.service = s; saveDraft(); location.hash = "#/care/book/when"; }

  function when() {
    if (!bookDraft.service) return book();
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
    bookDraft.tier = t; bookDraft.trigger = ""; saveDraft();
    location.hash = t === "planned" ? "#/care/book/details" : "#/care/book/trigger";
  }

  function triggers() {
    if (!bookDraft.tier) return when();
    UI.screen(`
      ${UI.appbar("What happened?", "So the right help comes ready", "#/care/book/when")}
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
      <div class="card" style="padding:12px">
        <label class="f-label" for="otherTxt" style="margin-top:0">Something else? <small>· optional</small></label>
        <input class="f-input" id="otherTxt" placeholder="A few words, e.g. cataract op" maxlength="80">
        <button class="btn quiet" style="margin:0" onclick="CareView.pickOther()">Other — tell us</button>
      </div>
      <button class="li" onclick="location.href='tel:+6560000000'">
        <div class="face gold">📞</div>
        <div class="body"><b>Not sure — talk to someone</b><span>Call the Pasir Ris ICCP coordinator · 6XXX XXXX</span></div></button>
      <button class="btn ghost" onclick="CareView.pickTrigger('')">Skip — just need help</button>`);
  }

  function pickOther() {
    const t = (UI.el("otherTxt").value || "").trim();
    if (!t) return UI.toast("A few words, so the right help comes", true);
    pickTrigger("Other: " + t);
  }

  function pickTrigger(t) { bookDraft.trigger = t; saveDraft(); location.hash = "#/care/book/details"; }

  /* Same-day arrival windows, only the ones still ahead of us. At 6pm the
     2–5pm window must not be offered — it was, on 21 Aug. */
  const DAY_WINDOWS = [["Today, 9am–12", 12], ["Today, 2–5pm", 17], ["Today, 6–9pm", 21]];
  function windowsFor(tier, now = new Date()) {
    const first = tier === "urgent" ? "Within the hour" : "Within 2 hours";
    const next = DAY_WINDOWS.find(([, end]) => now.getHours() < end);
    return [first, next ? next[0] : "Tomorrow, 9am–12"];
  }

  async function details() {
    if (!bookDraft.tier) return when();
    const planned = bookDraft.tier === "planned";
    // Start from the care plan's languages — NCSS: "why type it again?"
    let planLangs = [];
    try { const hh = await Api.get("/care/household"); planLangs = (hh.plan && hh.plan.languages) || []; } catch (e) {}
    const startLangs = planLangs.length ? planLangs : ["English"];
    const today = UI.ymd();
    const horizon = App.config.max_advance_days || 30;
    const maxDate = UI.ymdIn(horizon);
    const back = planned ? "#/care/book/when" : "#/care/book/trigger";
    UI.screen(`
      ${UI.appbar("The details", `${bookDraft.service} · ${UI.TIER_LABEL[bookDraft.tier]}${bookDraft.trigger ? " · " + bookDraft.trigger : ""}`, back)}
      <span class="stepper">Step ${planned ? "3 of 3" : "4 of 4"}</span>
      ${planned ? `
        <label class="f-label">Date <small>· required — up to ${horizon} days ahead</small></label>
        <input class="f-input" id="date" type="date" min="${today}" max="${maxDate}" value="${today}">
        <label class="f-label">Time <small>· required — in 30-minute steps</small></label>
        <div class="row" style="gap:10px;align-items:center">
          <select class="f-input" id="startT" aria-label="From" style="margin:0">${UI.timeOptions("14:00")}</select>
          <span>to</span>
          <select class="f-input" id="endT" aria-label="To" style="margin:0">${UI.timeOptions("16:00")}</select>
        </div>
        <p class="f-hint" id="hoursHint" style="margin-top:6px">2 hrs — charged by the half hour, minimum 1 hour</p>`
      : `
        <label class="f-label">Arrival window <small>· required</small></label>
        ${UI.chipGroup("winG", windowsFor(bookDraft.tier), windowsFor(bookDraft.tier)[0])}`}
      <label class="f-label">Languages with them <small>· required — from the care plan; tap to change</small></label>
      ${UI.chipMulti("langG2", App.config.languages, startLangs)}
      <label class="f-label">Anything the kaki should know? <small>· optional</small></label>
      <textarea class="f-input" id="notes" placeholder="e.g. Walks with a stick. Helper left suddenly."></textarea>
      <button class="btn gold" id="submitV">Request this visit</button>`);
    const hint = () => {
      const h = UI.el("hoursHint"); if (!h) return;
      const n = UI.hoursBetween(UI.el("startT").value, UI.el("endT").value);
      h.textContent = n ? `${n} hr${n === 1 ? "" : "s"} — charged by the half hour, minimum 1 hour` : "The end time must be after the start";
    };
    if (planned) { UI.el("startT").onchange = hint; UI.el("endT").onchange = hint; hint(); }
    UI.el("submitV").onclick = async () => {
      try {
        const v = await Api.post("/visits", planned ? {
          service: bookDraft.service, tier: bookDraft.tier, trigger: bookDraft.trigger || "",
          date: UI.el("date").value, start_time: UI.el("startT").value, end_time: UI.el("endT").value,
          languages: UI.chipValues("langG2"), notes: UI.el("notes").value } : {
          service: bookDraft.service, tier: bookDraft.tier, trigger: bookDraft.trigger || "",
          date: (UI.chipValue("winG") || "").startsWith("Tomorrow") ? "tomorrow" : "today",
          window: UI.chipValue("winG") || "", languages: UI.chipValues("langG2"),
          notes: UI.el("notes").value });
        clearDraft();
        UI.toast("Request sent — the coordinator is matching a kaki");
        location.hash = "#/care/visit/" + v.id;
      } catch (e) { UI.toast(e.message, true); }
    };
  }

  /* What "matching in progress" means in time. The coordinator's targets,
     not a promise — but a blank was worse: caregivers refreshed to find out. */
  const MATCH_ETA = { urgent: "within the hour", soon: "within 2 hours", planned: "within a day" };

  async function visit(id) {
    UI.spin();
    try {
      const v = await Api.get("/visits/" + id);
      const steps = [
        ["Requested", true, ""],
        ["Kaki assigned", !!v.kaki, v.kaki ? `${v.kaki.name} — verified by the coordinator` : "The coordinator is matching…"],
        ["Confirmed", ["accepted", "in_progress", "completed"].includes(v.status),
          v.on_way_at && v.status === "accepted" ? `${(v.kaki && v.kaki.name) || "Your kaki"} is on the way — since ${UI.hhmm(v.on_way_at)}` : ""],
        ["Kaki checked at the door", !!v.kaki_verified_at || ["in_progress", "completed"].includes(v.status), v.kaki_verified_at ? "Photo and code matched" : ""],
        ["Visit", v.status === "completed", v.status === "in_progress" ? "Happening now" : ""],
      ];
      const est = v.estimate;
      const active = ["assigned", "accepted", "in_progress"].includes(v.status);
      UI.screen(`
        ${UI.appbar(v.service, `${v.date} · ${v.window || ""}${v.hours ? ` · ${v.hours} hr${v.hours === 1 ? "" : "s"}` : ""} · ${UI.esc(v.senior_name)}`, "#/care/home")}
        <div class="row" style="flex-wrap:wrap">${UI.statusPill(v.status)}<span class="pill grey">${UI.TIER_LABEL[v.tier] || v.tier}</span>
        ${v.trigger ? `<span class="pill gold">${UI.esc(v.trigger)}</span>` : ""}
        <span class="pill green">${UI.esc((v.languages || [v.language]).join(", "))}</span></div>
        ${v.kaki ? `
          <div class="kakipass">
            <div class="kp-top">
              <div class="kp-face" style="overflow:hidden">${v.kaki.photo ? `<img src="${v.kaki.photo}" alt="${UI.esc(v.kaki.name || "Your kaki")}" style="width:100%;height:100%;object-fit:cover">` : UI.initials(v.kaki.name)}</div>
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
        ${v.status === "requested" ? `
          <div class="card tint"><h3>Usually matched ${MATCH_ETA[v.tier] || "soon"}</h3>
          <p>We'll message you the moment a kaki is confirmed — you don't need to keep checking.</p></div>` : ""}
        ${["assigned", "accepted"].includes(v.status) && !v.kaki_verified_at ? `
          <div class="card warn"><h3>Check it's them</h3>
          <p>When ${UI.esc((v.kaki && v.kaki.name) || "your kaki")} arrives, compare the photo above, then ask for the 4-digit code on their screen and enter it here. Your start code appears once it matches.</p>
          <div class="otp-in">${[0,1,2,3].map(i => `<input id="k${i}" inputmode="numeric" maxlength="1" aria-label="Kaki code digit ${i + 1}">`).join("")}</div>
          <button class="btn" id="verifyK">Confirm it's them</button></div>` : ""}
        ${["assigned", "accepted"].includes(v.status) && v.otp_code ? `
          <div class="card warn"><h3>Start code — read it to your kaki when they arrive</h3>
          <div class="codebox">${v.otp_code.split("").map(d => `<span>${d}</span>`).join("")}</div>
          <p>Only you can see this code. Read it to your kaki once you have checked it's them —
          they type it in to start the visit. That's how we know someone was really let in.</p></div>` : ""}
        ${est && v.status !== "cancelled" ? `
          <div class="eyebrow">Estimated cost · pilot</div>
          <div class="stack">
            <div class="s-row"><span>Visit rate · ${est.hours} hr${est.hours > 1 ? "s" : ""} × $${est.rate}<span class="who">Standard ${UI.esc(v.service.toLowerCase())} rate</span></span><span class="amt">$${est.base.toFixed(2)}</span></div>
            <div class="s-row minus"><span>Community care subsidy<span class="who">Est. — confirmed by the coordinator</span></span><span class="amt">− $${est.subsidy.toFixed(2)}</span></div>
            <div class="s-row minus"><span>Foundation top-up<span class="who">Est. · means-tested</span></span><span class="amt">− $${est.foundation.toFixed(2)}</span></div>
            <div class="s-row total"><span>Family pays (est.)</span><span class="amt">$${est.family_pays.toFixed(2)}</span></div>
          </div>
          <p style="font-size:.74rem;color:var(--slate);margin:-6px 0 10px">Billed through your ICCP account during the pilot — nothing to pay in the app.</p>
          ${(App.config.paynow && App.config.paynow.configured) ? `
            <div class="card tint" style="padding:12px">
              <h3>PayNow</h3>
              <p>If the coordinator asks you to transfer directly, pay to
              <b>${UI.esc(App.config.paynow.value)}</b>
              (${UI.esc(App.config.paynow.type === "uen" ? "UEN" : "mobile")})${
                App.config.paynow.name ? " · " + UI.esc(App.config.paynow.name) : ""}.</p>
              <p style="font-size:.72rem;opacity:.85">Always confirm with the coordinator first —
              during the pilot most visits are billed through ICCP, not paid in the app.</p>
            </div>` : ""}
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
      [0,1,2,3].forEach(i => { const o = UI.el("k" + i); if (o) o.oninput = () => { if (o.value && i < 3) UI.el("k" + (i + 1)).focus(); }; });
      const vk = UI.el("verifyK");
      if (vk) vk.onclick = async () => {
        const code = [0,1,2,3].map(i => UI.el("k" + i).value).join("");
        try { await Api.post(`/visits/${id}/verify-kaki`, { code }); UI.toast("It's them ✓ — here's your start code"); visit(id); }
        catch (e) { UI.toast(e.message, true); }
      };
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

  return { home, setup, planEdit, profile, book, pickService, when, pickTier, triggers, pickTrigger, pickOther, details, visit, visits, windowsFor };
})();
