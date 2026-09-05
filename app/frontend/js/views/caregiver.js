/* M-CARE + caregiver side of M-VISITS.
   v1.7: every sentence is UI.t(...); every data value shown through UI.v(...)
   so what goes to the API is unchanged. Names, notes and reasons are never
   translated. */
const CareView = (() => {
  const t = (id, vars) => UI.t(id, vars);
  const v = (kind, val) => UI.v(kind, val);
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
        ${UI.appbar(t("cg.hello", { name: App.user.name || t("cg.there") }).replace(/[,，]\s*$/, ""), t("cg.caring", { name: household.senior_name }))}
        <button class="btn gold" style="min-height:60px;font-size:1.05rem" onclick="location.hash='#/care/book'">${t("cg.bookfor", { name: UI.esc(household.senior_name) })}</button>
        <div class="eyebrow">${t("cg.careplan")}</div>
        <button class="li" onclick="location.hash='#/care/plan'">
          <div class="face">📋</div>
          <div class="body"><b>${t("cg.plan.of", { name: UI.esc(household.senior_name) })}</b>
          <span>${UI.esc(plan?.meds || t("cg.plan.addmeds"))} · ${UI.esc(v("mobility", plan?.mobility) || t("cg.plan.mobility"))} — ${t("cg.plan.every")}</span></div>
          <span class="pill green">${t("common.edit")}</span>
        </button>
        ${open.length ? `<div class="eyebrow">${t("cg.current")}</div>` + open.map(vRow).join("") : ""}
        ${done.length ? `<div class="eyebrow">${t("cg.recent")}</div>` + done.map(vRow).join("") : ""}
        <button class="li" onclick="location.hash='#/care/profile'">
          <div class="face">${UI.initials(App.user.name)}</div>
          <div class="body"><b>${t("cg.profile")}</b><span>${UI.esc(App.user.name || "")} · ${UI.esc(UI.contact(App.user))}</span></div>
          <span class="pill grey">${t("common.edit")}</span>
        </button>
        <div class="helpline">${t("common.helpline.need")} <b>${t("common.iccp")}</b></div>`);
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  function vRow(v0) {
    const who = v0.kaki ? t("cg.with", { name: v0.kaki.name }) : t("cg.matching");
    return `<button class="li" onclick="location.hash='#/care/visit/${v0.id}'">
      <div class="face${v0.tier === "urgent" ? " gold" : ""}">${v0.kaki ? UI.initials(v0.kaki.name) : "…"}</div>
      <div class="body"><b>${UI.esc(v("service", v0.service))} · ${UI.esc(v0.date)} ${UI.esc(v("window", v0.window || ""))}</b>
      <span>${UI.esc(who)}</span></div>
      <div class="end">${UI.statusPill(v0.status)}</div></button>`;
  }

  function setup() {
    UI.screen(`
      ${UI.appbar(t("setup.title"), t("setup.sub"))}
      <label class="f-label">${t("setup.name")}</label>
      <input class="f-input" id="sn" placeholder="${UI.esc(t("setup.name.ph"))}">
      <label class="f-label">${t("setup.age")}</label>
      <input class="f-input" id="sa" inputmode="numeric" placeholder="${UI.esc(t("setup.age.ph"))}">
      <label class="f-label">${t("setup.addr")} <small>${t("setup.addr.small")}</small></label>
      <input class="f-input" id="ad" placeholder="${UI.esc(t("setup.addr.ph"))}">
      <button class="btn" id="saveHh">${t("setup.go")}</button>`);
    UI.el("saveHh").onclick = async () => {
      const name = UI.el("sn").value.trim();
      if (!name) return UI.toast(t("setup.needname"), true);
      try {
        await Api.put("/care/household", { senior_name: name,
          senior_age: parseInt(UI.el("sa").value) || null, address: UI.el("ad").value.trim() });
        UI.toast(t("setup.saved"));
        location.hash = "#/care/plan";
      } catch (e) { UI.toast(UI.terr(e), true); }
    };
  }

  async function planEdit() {
    UI.spin();
    try {
      const { household, plan } = await Api.get("/care/household");
      if (!household) return setup();
      UI.screen(`
        ${UI.appbar(t("cg.plan.of", { name: household.senior_name }), t("plan.sub"), "#/care/home")}
        <label class="f-label">${t("plan.meds")}</label>
        <textarea class="f-input" id="meds" placeholder="${UI.esc(t("plan.meds.ph"))}">${UI.esc(plan?.meds)}</textarea>
        <label class="f-label">${t("plan.mobility")}</label>
        ${UI.chipGroup("mobG", ["Independent", "Walks with a stick", "Walking frame", "Wheelchair", "Bedridden"], plan?.mobility || null, "mobility")}
        <label class="f-label">${t("plan.langs")}</label>
        ${UI.chipMulti("langG", App.config.languages, plan?.languages || [], "language")}
        <label class="f-label">${t("plan.contact")} <small>${t("plan.contact.small")}</small></label>
        <input class="f-input" id="cName" value="${UI.esc(plan?.contact_name)}" placeholder="${UI.esc(t("plan.contact.name"))}" aria-label="Contact name">
        <input class="f-input" id="cRel" value="${UI.esc(plan?.contact_relationship)}" placeholder="${UI.esc(t("plan.contact.rel"))}" aria-label="Contact relationship">
        <input class="f-input" id="cPhone" inputmode="tel" value="${UI.esc(plan?.contact_phone)}" placeholder="${UI.esc(t("plan.contact.phone"))}" aria-label="Contact mobile number">
        ${plan?.contacts ? `<textarea class="f-input" id="contacts" aria-label="${UI.esc(t("plan.other"))}">${UI.esc(plan.contacts)}</textarea>` : `<input type="hidden" id="contacts" value="">`}
        <label class="f-label">${t("plan.notes")}</label>
        <textarea class="f-input" id="notes" placeholder="${UI.esc(t("plan.notes.ph"))}">${UI.esc(plan?.notes)}</textarea>
        <button class="btn" id="savePlan">${t("plan.save")}</button>`);
      UI.el("savePlan").onclick = async () => {
        try {
          await Api.put("/care/plan", {
            meds: UI.el("meds").value, mobility: UI.chipValue("mobG") || "",
            languages: UI.chipValues("langG"), contacts: UI.el("contacts").value,
            contact_name: UI.el("cName").value, contact_relationship: UI.el("cRel").value,
            contact_phone: UI.el("cPhone").value, notes: UI.el("notes").value });
          UI.toast(t("plan.saved"));
          location.hash = "#/care/home";
        } catch (e) { UI.toast(UI.terr(e), true); }
      };
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  /* Caregivers could edit the care plan but not their own name or number (NCSS 2.1). */
  async function profile() {
    UI.spin();
    try {
      const p = await Api.get("/users/me/profile");
      UI.screen(`
        ${UI.appbar(t("cg.profile"), t("cgp.sub"), "#/care/home")}
        <label class="f-label" for="pname">${t("cgp.name")}</label>
        <input class="f-input" id="pname" value="${UI.esc(p.name)}" autocomplete="name">
        <label class="f-label" for="pphone">${t("cgp.phone")} <small>${t("cgp.phone.small")}</small></label>
        <input class="f-input" id="pphone" inputmode="tel" value="${UI.esc(p.phone)}" autocomplete="tel">
        <p class="f-hint">${t("cgp.signedin", { id: UI.esc(UI.contact(p)) })}</p>
        <button class="btn" id="saveP">${t("cgp.save")}</button>`);
      UI.el("saveP").onclick = async () => {
        try {
          const r = await Api.put("/users/me", { name: UI.el("pname").value.trim(), phone: UI.el("pphone").value.trim() });
          App.user.name = r.name;
          UI.toast(t("cgp.saved"));
        } catch (e) { UI.toast(UI.terr(e), true); }
      };
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  /* ---- booking flow: service → when → (what happened) → details ----
     Each step is its own hash route so back and refresh land on the step the
     person was on. */
  function book() {
    clearDraft();
    UI.screen(`
      ${UI.appbar(t("book.title"), t("book.sub"), "#/care/home")}
      <span class="stepper">${t("book.step", { a: 1, b: 3 })}</span>
      ${[["🚶", "Chaperone", "book.chap.d"],
         ["☕", "Companionship", "book.comp.d"],
         ["🩺", "Wellness check", "book.well.d"],
         ["🧺", "Household help", "book.house.d"]].map(([i, n, d]) =>
        `<button class="bigcard" data-service="${n}" onclick="CareView.pickService('${n}')">
          <span class="bc-ico">${i}</span><div><b>${UI.esc(v("service", n))}</b><span>${t(d)}</span></div></button>`).join("")}
      <div class="bigcard locked"><span class="bc-ico">💊</span>
        <div><b>${UI.esc(v("service", "Medicine administration"))}</b><span>${t("book.med.d")}</span></div></div>`);
  }

  function pickService(s) { bookDraft.service = s; saveDraft(); location.hash = "#/care/book/when"; }

  function when() {
    if (!bookDraft.service) return book();
    UI.screen(`
      ${UI.appbar(t("when.title"), v("service", bookDraft.service), "#/care/book")}
      <span class="stepper">${t("book.step", { a: 2, b: 3 })}</span>
      <button class="tier urgent" onclick="CareView.pickTier('urgent')">
        <div><b>${t("when.urgent")}</b><span>${t("when.urgent.d")}</span></div>
        <span class="t-eta">${t("when.urgent.eta")}</span></button>
      <button class="tier" onclick="CareView.pickTier('soon')">
        <div><b>${t("when.soon")}</b><span>${t("when.soon.d")}</span></div>
        <span class="t-eta">${t("when.soon.eta")}</span></button>
      <button class="tier" onclick="CareView.pickTier('planned')">
        <div><b>${t("when.planned")}</b><span>${t("when.planned.d")}</span></div>
        <span class="t-eta">${t("when.planned.eta")}</span></button>`);
  }

  function pickTier(tier) {
    bookDraft.tier = tier; bookDraft.trigger = ""; saveDraft();
    location.hash = tier === "planned" ? "#/care/book/details" : "#/care/book/trigger";
  }

  function triggers() {
    if (!bookDraft.tier) return when();
    UI.screen(`
      ${UI.appbar(t("trig.title"), t("trig.sub"), "#/care/book/when")}
      <span class="stepper">${t("book.step", { a: 3, b: 4 })} · ${v("urgency", bookDraft.tier)}</span>
      <div class="eyebrow">${t("trig.common")}</div>
      ${[["🧳", "Helper left suddenly", "trig.helper.d"],
         ["🏥", "Spouse hospitalised", "trig.spouse.d"],
         ["🆘", "My own emergency", "trig.own.d"],
         ["🛏️", "Discharge, no plan", "trig.discharge.d"],
         ["📉", "Sudden decline", "trig.decline.d"],
         ["🕊️", "Loss of a spouse", "trig.loss.d"]].map(([i, n, d]) =>
        `<button class="bigcard" data-trigger="${n}" onclick="CareView.pickTrigger('${n}')">
          <span class="bc-ico">${i}</span><div><b>${UI.esc(v("trigger", n))}</b><span>${t(d)}</span></div></button>`).join("")}
      <div class="card" style="padding:12px">
        <label class="f-label" for="otherTxt" style="margin-top:0">${t("trig.else")} <small>${t("common.optional")}</small></label>
        <input class="f-input" id="otherTxt" placeholder="${UI.esc(t("trig.else.ph"))}" maxlength="80">
        <button class="btn quiet" style="margin:0" onclick="CareView.pickOther()">${t("trig.other")}</button>
      </div>
      <button class="li" onclick="location.href='tel:+6560000000'">
        <div class="face gold">📞</div>
        <div class="body"><b>${t("trig.talk")}</b><span>${t("trig.talk.d")}</span></div></button>
      <button class="btn ghost" onclick="CareView.pickTrigger('')">${t("trig.skip")}</button>`);
  }

  function pickOther() {
    const txt = (UI.el("otherTxt").value || "").trim();
    if (!txt) return UI.toast(t("trig.other.empty"), true);
    pickTrigger("Other: " + txt);
  }

  function pickTrigger(tr) { bookDraft.trigger = tr; saveDraft(); location.hash = "#/care/book/details"; }

  /* Same-day arrival windows, only the ones still ahead of us. At 6pm the
     2–5pm window must not be offered — it was, on 21 Aug. Values are the
     English strings the API knows; the chip shows UI.v("window", value). */
  const DAY_WINDOWS = [["Today, 9am–12", 12], ["Today, 2–5pm", 17], ["Today, 6–9pm", 21]];
  function windowsFor(tier, now = new Date()) {
    const first = tier === "urgent" ? "Within the hour" : "Within 2 hours";
    const next = DAY_WINDOWS.find(([, end]) => now.getHours() < end);
    return [first, next ? next[0] : "Tomorrow, 9am–12"];
  }

  /* "Other: cataract op" — the prefix is ours, the rest is the person's. */
  const triggerLabel = tr => tr && tr.startsWith("Other: ") ? tr : v("trigger", tr);

  async function details() {
    if (!bookDraft.tier) return when();
    const planned = bookDraft.tier === "planned";
    // Start from the care plan's languages — NCSS: "why type it again?"
    let planLangs = [], pastKakis = [];
    try { const hh = await Api.get("/care/household"); planLangs = (hh.plan && hh.plan.languages) || []; } catch (e) {}
    try { pastKakis = await Api.get("/visits/past-kakis"); } catch (e) {}
    const startLangs = planLangs.length ? planLangs : ["English"];
    const today = UI.ymd();
    const horizon = App.config.max_advance_days || 30;
    const maxDate = UI.ymdIn(horizon);
    const back = planned ? "#/care/book/when" : "#/care/book/trigger";
    UI.screen(`
      ${UI.appbar(t("det.title"), `${v("service", bookDraft.service)} · ${UI.tierLabel(bookDraft.tier)}${bookDraft.trigger ? " · " + triggerLabel(bookDraft.trigger) : ""}`, back)}
      <span class="stepper">${planned ? t("book.step", { a: 3, b: 3 }) : t("book.step", { a: 4, b: 4 })}</span>
      ${planned ? `
        <label class="f-label">${t("det.date")} <small>${t("det.date.small", { n: horizon })}</small></label>
        <input class="f-input" id="date" type="date" min="${today}" max="${maxDate}" value="${today}">
        <label class="f-label">${t("det.time")} <small>${t("det.time.small")}</small></label>
        <div class="row" style="gap:10px;align-items:center">
          <select class="f-input" id="startT" aria-label="${UI.esc(t("det.from"))}" style="margin:0">${UI.timeOptions("14:00")}</select>
          <span>${t("common.to")}</span>
          <select class="f-input" id="endT" aria-label="${UI.esc(t("det.to"))}" style="margin:0">${UI.timeOptions("16:00")}</select>
        </div>
        <p class="f-hint" id="hoursHint" style="margin-top:6px">${t("det.hours", { h: UI.hrs(2) })}</p>`
      : `
        <label class="f-label">${t("det.window")} <small>${t("common.required")}</small></label>
        ${UI.chipGroup("winG", windowsFor(bookDraft.tier), windowsFor(bookDraft.tier)[0], "window")}`}
      <label class="f-label">${t("det.langs")} <small>${t("det.langs.small")}</small></label>
      ${UI.chipMulti("langG2", App.config.languages, startLangs, "language")}
      ${pastKakis.length ? `
      <label class="f-label">${t("det.known")} <small>${t("det.known.small")}</small></label>
      <div class="chips" id="prefK">
        <button type="button" class="chip sel" data-v="" onclick="UI.pick('prefK', this)">${t("det.anyone")}</button>
        ${pastKakis.map(k => `<button type="button" class="chip" data-v="${UI.esc(k.id)}" onclick="UI.pick('prefK', this)">${UI.esc(k.name)} · ${t("det.together", { n: UI.visitsN(k.times) })}</button>`).join("")}
      </div>` : ""}
      <label class="f-label">${t("det.kaki")} <small>${t("common.optional")}</small></label>
      ${UI.chipGroup("genderG", ["No preference", "Female", "Male"], "No preference", "gender")}
      <label class="f-label">${t("det.notes")} <small>${t("common.optional")}</small></label>
      <textarea class="f-input" id="notes" placeholder="${UI.esc(t("det.notes.ph"))}"></textarea>
      <button class="btn gold" id="submitV">${t("det.submit")}</button>`);
    const hint = () => {
      const h = UI.el("hoursHint"); if (!h) return;
      const n = UI.hoursBetween(UI.el("startT").value, UI.el("endT").value);
      h.textContent = n ? t("det.hours", { h: UI.hrs(n) }) : t("det.endafter");
    };
    if (planned) { UI.el("startT").onchange = hint; UI.el("endT").onchange = hint; hint(); }
    const genderPref = () => ({ Female: "female", Male: "male" })[UI.chipValue("genderG")] || "any";
    UI.el("submitV").onclick = async () => {
      try {
        const vv = await Api.post("/visits", planned ? {
          service: bookDraft.service, tier: bookDraft.tier, trigger: bookDraft.trigger || "",
          date: UI.el("date").value, start_time: UI.el("startT").value, end_time: UI.el("endT").value,
          languages: UI.chipValues("langG2"), notes: UI.el("notes").value, kaki_gender_pref: genderPref(), preferred_kaki_id: UI.chipValue("prefK") || "" } : {
          service: bookDraft.service, tier: bookDraft.tier, trigger: bookDraft.trigger || "",
          date: (UI.chipValue("winG") || "").startsWith("Tomorrow") ? "tomorrow" : "today",
          window: UI.chipValue("winG") || "", languages: UI.chipValues("langG2"),
          notes: UI.el("notes").value, kaki_gender_pref: genderPref(), preferred_kaki_id: UI.chipValue("prefK") || "" });
        clearDraft();
        UI.toast(t("det.sent"));
        location.hash = "#/care/visit/" + vv.id;
      } catch (e) { UI.toast(UI.terr(e), true); }
    };
  }

  /* What "matching in progress" means in time. The coordinator's targets,
     not a promise — but a blank was worse: caregivers refreshed to find out. */
  const matchEta = tier => ({ urgent: "cv.eta.urgent", soon: "cv.eta.soon", planned: "cv.eta.planned" })[tier] || "cv.eta.soon2";

  async function visit(id) {
    UI.spin();
    try {
      const vd = await Api.get("/visits/" + id);
      const kname = (vd.kaki && vd.kaki.name) || t("common.first");
      const steps = [
        [t("cv.step.requested"), true, ""],
        [t("cv.step.assigned"), !!vd.kaki, vd.kaki ? t("cv.verified", { name: vd.kaki.name }) : t("cv.matchingdots")],
        [t("cv.step.confirmed"), ["accepted", "in_progress", "completed"].includes(vd.status),
          vd.on_way_at && vd.status === "accepted" ? t("cv.onway", { name: kname, t: UI.hhmm(vd.on_way_at) }) : ""],
        [t("cv.step.door"), !!vd.kaki_verified_at || ["in_progress", "completed"].includes(vd.status), vd.kaki_verified_at ? t("cv.matched") : ""],
        [t("cv.step.visit"), vd.status === "completed", vd.status === "in_progress" ? t("cv.now") : ""],
      ];
      const est = vd.estimate;
      const active = ["assigned", "accepted", "in_progress"].includes(vd.status);
      const seniorUp = (vd.senior_name || "").toUpperCase();
      UI.screen(`
        ${UI.appbar(v("service", vd.service), `${vd.date} · ${v("window", vd.window || "")}${vd.hours ? ` · ${UI.hrs(vd.hours)}` : ""} · ${UI.esc(vd.senior_name)}`, "#/care/home")}
        <div class="row" style="flex-wrap:wrap">${UI.statusPill(vd.status)}<span class="pill grey">${UI.tierLabel(vd.tier)}</span>
        ${vd.trigger ? `<span class="pill gold">${UI.esc(triggerLabel(vd.trigger))}</span>` : ""}
        <span class="pill green">${UI.esc((vd.languages || [vd.language]).map(l => v("language", l)).join(", "))}</span>
        ${vd.kaki_gender_pref && vd.kaki_gender_pref !== "any" ? `<span class="pill grey">${vd.kaki_gender_pref === "female" ? t("cv.female") : t("cv.male")}</span>` : ""}
        ${vd.preferred_kaki ? `<span class="pill grey">${t("cv.asked", { name: UI.esc(vd.preferred_kaki.name) })}</span>` : ""}</div>
        ${vd.kaki ? `
          <div class="kakipass">
            <div class="kp-top">
              <div class="kp-face" style="overflow:hidden">${vd.kaki.photo ? `<img src="${UI.esc(vd.kaki.photo)}" alt="${UI.esc(kname)}" style="width:100%;height:100%;object-fit:cover">` : UI.initials(vd.kaki.name)}</div>
              <div><h3>${UI.esc(kname)}</h3>
                <div class="kp-sub">${UI.esc(v("service", vd.service))} · ${t("cv.pr")}</div>
                <div class="kp-meta"><span>${t("cv.tier", { n: vd.kaki.tier || 1 })}</span>
                ${(vd.kaki.languages || []).slice(0, 2).map(l => `<span>${t("cv.speaks", { l: UI.esc(v("language", l)) })}</span>`).join("")}</div>
              </div>
            </div>
            <div class="kp-consist">${vd.times_together > 0
              ? t("cv.knows", { senior: UI.esc(vd.senior_name), kaki: UI.esc((vd.kaki.name || "").split(" ")[0] || kname), n: UI.visitsN(vd.times_together) })
              : t("cv.firstvisit", { senior: UI.esc(vd.senior_name) })}</div>
            <div class="kp-id">${t("cv.passline", { senior: UI.esc(seniorUp) })}</div>
          </div>` : ""}
        ${active ? `
          <div class="row" style="margin:4px 0 10px">
            <button class="btn quiet" style="margin:0;min-height:48px" onclick="location.href='tel:+6560000000'">${t("cv.callcoord")}</button>
            ${vd.kaki && vd.kaki.phone ? `<button class="btn quiet" style="margin:0;min-height:48px" onclick="location.href='tel:${UI.esc(vd.kaki.phone)}'">${t("cv.callkaki", { name: UI.esc((vd.kaki.name || "Kaki").split(" ")[0]) })}</button>` : ""}
          </div>` : ""}
        <ul class="tl" style="margin-top:8px">
          ${steps.map(([b, done, s], i) => `<li class="${done ? "done" : (i === steps.findIndex(x => !x[1]) ? "now" : "")}">
            <div><b>${b}</b>${s ? `<span>${UI.esc(s)}</span>` : ""}</div></li>`).join("")}
        </ul>
        ${vd.status === "requested" && vd.last_cancellation && vd.last_cancellation.by === "kaki" ? `
          <div class="card warn"><p><b>${t("cv.cancelled.by", { name: UI.esc(vd.last_cancellation.by_name || t("common.first")), reason: UI.esc(vd.last_cancellation.reason) })}</b><br>${t("cv.finding")}</p></div>` : ""}
        ${vd.status === "requested" ? `
          <div class="card tint"><h3>${t("cv.eta", { eta: t(matchEta(vd.tier)) })}</h3>
          <p>${t("cv.eta.body")}</p></div>` : ""}
        ${["assigned", "accepted"].includes(vd.status) && !vd.kaki_verified_at ? `
          <div class="card warn"><h3>${t("cv.check")}</h3>
          <p>${t("cv.check.body", { name: UI.esc(kname) })}</p>
          <div class="otp-in">${[0,1,2,3].map(i => `<input id="k${i}" inputmode="numeric" maxlength="1" aria-label="${UI.esc(t("cv.digit", { n: i + 1 }))}">`).join("")}</div>
          <button class="btn" id="verifyK">${t("cv.confirm")}</button></div>` : ""}
        ${["assigned", "accepted"].includes(vd.status) && vd.otp_code ? `
          <div class="card warn"><h3>${t("cv.startcode")}</h3>
          <div class="codebox">${vd.otp_code.split("").map(d => `<span>${d}</span>`).join("")}</div>
          <p>${t("cv.startcode.body")}</p></div>` : ""}
        ${est && vd.status !== "cancelled" ? `
          <div class="eyebrow">${t("cv.cost")}</div>
          <div class="stack">
            <div class="s-row"><span>${t("cv.rate", { h: UI.hrs(est.hours), r: est.rate })}<span class="who">${t("cv.rate.who", { s: UI.esc(UI.lang === "zh" ? v("service", vd.service) : vd.service.toLowerCase()) })}</span></span><span class="amt">$${est.base.toFixed(2)}</span></div>
            <div class="s-row minus"><span>${t("cv.subsidy")}<span class="who">${t("cv.subsidy.who")}</span></span><span class="amt">− $${est.subsidy.toFixed(2)}</span></div>
            <div class="s-row minus"><span>${t("cv.topup")}<span class="who">${t("cv.topup.who")}</span></span><span class="amt">− $${est.foundation.toFixed(2)}</span></div>
            <div class="s-row total"><span>${t("cv.pays")}</span><span class="amt">$${est.family_pays.toFixed(2)}</span></div>
          </div>
          <p style="font-size:.74rem;color:var(--slate);margin:-6px 0 10px">${t("cv.billed")}</p>
          ${(App.config.paynow && App.config.paynow.configured) ? `
            <div class="card tint" style="padding:12px">
              <h3>${t("cv.paynow")}</h3>
              <p>${t("cv.paynow.body")}
              <b>${UI.esc(App.config.paynow.value)}</b>
              (${UI.esc(App.config.paynow.type === "uen" ? t("cv.paynow.uen") : t("cv.paynow.mobile"))})${
                App.config.paynow.name ? " · " + UI.esc(App.config.paynow.name) : ""}.</p>
              <p style="font-size:.72rem;opacity:.85">${t("cv.paynow.note")}</p>
            </div>` : ""}
          ${UI.moneyNote()}` : ""}
        ${vd.status === "completed" && vd.report ? `
          <div class="card"><h3>${t("cv.report")}</h3>
            <p>${UI.esc(vd.report.text || "")}</p><div class="divider"></div>
            <div class="row" style="flex-wrap:wrap">${(vd.report.chips || []).map(c => `<span class="pill green">${UI.esc(v("report", c))}</span>`).join("")}
            ${vd.report.meds_confirmed ? `<span class="pill green">${t("cv.meds")}</span>` : ""}</div></div>
          <div class="card tint"><h3>${t("cv.note")}</h3>
            <p>${t("cv.note.body")}</p>
            ${UI.chipMulti("noteChips", ["All fine", "Tired after visit", "Refused meds", "Fall concern", "New confusion"], [], "note")}
            <textarea class="f-input" id="noteTxt" style="margin-top:10px" placeholder="${UI.esc(t("cv.note.ph"))}"></textarea>
            <button class="btn quiet" id="sendNote">${t("cv.note.send")}</button></div>` : ""}
        ${["requested", "assigned", "accepted", "in_progress"].includes(vd.status) ? `<button class="btn danger" id="cancelV">${vd.status === "in_progress" ? t("cv.end") : t("cv.cancel")}</button>` : ""}
      `);
      [0,1,2,3].forEach(i => { const o = UI.el("k" + i); if (o) o.oninput = () => { if (o.value && i < 3) UI.el("k" + (i + 1)).focus(); }; });
      const vk = UI.el("verifyK");
      if (vk) vk.onclick = async () => {
        const code = [0,1,2,3].map(i => UI.el("k" + i).value).join("");
        try { await Api.post(`/visits/${id}/verify-kaki`, { code }); UI.toast(t("cv.itsthem")); visit(id); }
        catch (e) { UI.toast(UI.terr(e), true); }
      };
      const sn = UI.el("sendNote");
      if (sn) sn.onclick = async () => {
        try {
          await Api.post(`/visits/${id}/care-note`, { chips: UI.chipValues("noteChips"), text: UI.el("noteTxt").value });
          UI.toast(t("cv.note.sent")); sn.disabled = true;
        } catch (e) { UI.toast(UI.terr(e), true); }
      };
      const cv = UI.el("cancelV");
      if (cv) cv.onclick = async () => {
        const reason = prompt(vd.status === "in_progress" ? t("cv.end.ask") : t("cv.cancel.ask"));
        if (reason === null) return;
        try { await Api.post(`/visits/${id}/cancel`, { reason: reason.trim() }); UI.toast(t("cv.cancelled")); location.hash = "#/care/home"; }
        catch (e) { UI.toast(UI.terr(e), true); }
      };
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  async function visits(seg = "active") {
    UI.spin();
    try {
      const all = await Api.get("/visits");
      const act = all.filter(x => !["completed", "cancelled"].includes(x.status));
      const hist = all.filter(x => ["completed", "cancelled"].includes(x.status));
      const list = seg === "active" ? act : hist;
      UI.screen(`
        ${UI.appbar(t("cvs.title"), t("cvs.sub"))}
        <div class="seg">
          <button class="${seg === "active" ? "on" : ""}" onclick="CareView.visits('active')">${t("cvs.active", { n: act.length })}</button>
          <button class="${seg === "history" ? "on" : ""}" onclick="CareView.visits('history')">${t("cvs.history", { n: hist.length })}</button>
        </div>
        ${list.length ? list.map(vRow).join("")
          : `<div class="card tint"><p>${seg === "active" ? t("cvs.none") : t("cvs.nopast")}</p></div>`}`);
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  return { home, setup, planEdit, profile, book, pickService, when, pickTier, triggers, pickTrigger, pickOther, details, visit, visits, windowsFor };
})();
