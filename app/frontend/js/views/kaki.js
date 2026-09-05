/* Kaki side of M-VISITS + M-USERS profile.
   v1.7: every sentence is UI.t(...); data values are shown through UI.v(...)
   and sent unchanged. What the family or the kaki typed is never translated. */
const KakiView = (() => {
  const t = (id, vars) => UI.t(id, vars);
  const v = (kind, val) => UI.v(kind, val);

  async function home() {
    UI.spin();
    try {
      const visits = await Api.get("/visits");
      const open = visits.filter(x => !["completed", "cancelled"].includes(x.status));
      const done = visits.filter(x => x.status === "completed");
      const hours = done.reduce((a, x) => a + (x.estimate?.hours || 2), 0);
      const earned = done.reduce((a, x) => a + (x.estimate ? x.estimate.kaki_fee + x.estimate.transport : 0), 0);
      UI.screen(`
        ${UI.appbar(t("k.title"), t("k.sub", { name: App.user.name || t("k.kaki") }))}
        ${open.length ? open.map(vRow).join("")
          : `<div class="card tint"><h3>${t("k.none")}</h3>
             <p>${t("k.none.body")}</p></div>`}
        <p class="f-hint" style="margin:6px 4px 10px">${t("k.noopen")}</p>
        <div class="card tint" style="margin-top:10px">
          <div class="row"><div class="grow"><h3>${t("k.impact")}</h3>
          <p>${t("k.impact.line", { v: UI.visitsN(done.length), h: UI.hrs(hours), e: earned.toFixed(2) })}</p></div>
          <button class="chip" onclick="location.hash='#/kaki/impact'">${t("k.impact.go")}</button></div>
        </div>
        ${UI.moneyNote()}`);
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  function vRow(x) {
    return `<button class="li" onclick="location.hash='#/kaki/visit/${x.id}'">
      <div class="face${x.tier === "urgent" ? " gold" : ""}">${x.tier === "urgent" ? "⚡" : UI.initials(x.senior_name)}</div>
      <div class="body"><b>${UI.esc(v("service", x.service))} · ${UI.esc(x.date)} ${UI.esc(v("window", x.window || ""))}${x.estimate ? " · $" + x.estimate.kaki_fee : ""}</b>
      <span>${UI.esc(x.senior_name)}${x.senior_age ? ", " + x.senior_age : ""} · ${UI.esc(x.address || t("cv.pr"))} · ${UI.esc(v("language", x.language))}${x.times_together ? ` · <b style="color:var(--pandan)">${t("k.visited", { n: x.times_together })}</b>` : ""}</span></div>
      <div class="end">${UI.statusPill(x.status)}</div></button>`;
  }

  async function visit(id) {
    UI.spin();
    try {
      const x = await Api.get("/visits/" + id);
      const plan = x.care_plan || {};
      UI.screen(`
        ${UI.appbar(v("service", x.service), `${x.date} · ${v("window", x.window || "")}${x.hours ? ` · ${UI.hrs(x.hours)}` : ""} · ${UI.esc(x.senior_name)}`, "#/kaki/home")}
        <div class="row">${UI.statusPill(x.status)}<span class="pill grey">${UI.tierLabel(x.tier)}</span>
        <span class="pill green">${UI.esc((x.languages || [x.language]).map(l => v("language", l)).join(", "))}</span></div>
        <div class="card" style="margin-top:12px">
          <h3>${UI.esc(x.senior_name)}${x.senior_age ? ", " + x.senior_age : ""}${x.times_together ? t("kv.together", { n: x.times_together }) : t("kv.first")}</h3>
          <p>${UI.esc(x.address || t("cv.pr"))}</p>
          ${x.trigger ? `<p style="margin-top:4px"><b>${t("kv.why")}</b> ${UI.esc(x.trigger.startsWith("Other: ") ? x.trigger : v("trigger", x.trigger))}</p>` : ""}
          ${x.notes ? `<div class="divider"></div><p><b>${t("kv.family")}</b> ${UI.esc(x.notes)}</p>` : ""}
          ${x.estimate ? `<div class="divider"></div><div class="row"><span class="pill gold">${t("kv.receive", { n: (x.estimate.kaki_fee + x.estimate.transport).toFixed(2) })}</span><span class="pill green">${t("kv.cashless")}</span></div>${UI.moneyNote()}` : ""}
        </div>
        <div class="card tint">
          <h3>${x.minimised ? t("kv.need") : t("kv.plan")}</h3>
          ${x.minimised ? `<p class="f-hint" style="margin:0 0 8px">${t("kv.minimised")}</p>` : ""}
          <p>${plan.meds ? "💊 " + UI.esc(plan.meds) + "<br>" : ""}
             ${plan.mobility ? "🚶 " + UI.esc(v("mobility", plan.mobility)) + "<br>" : ""}
             ${(plan.languages || []).length ? "🗣 " + plan.languages.map(l => UI.esc(v("language", l))).join(", ") + "<br>" : ""}
             ${plan.notes ? "📝 " + UI.esc(plan.notes) : ""}</p>
          ${plan.contact_name || plan.contact_phone ? `<div class="divider"></div><p><b>${t("kv.emergency")}</b> ${UI.esc(plan.contact_name || "")}${plan.contact_relationship ? " (" + UI.esc(plan.contact_relationship) + ")" : ""} · ${UI.esc(plan.contact_phone || "")}<br><small>${t("kv.emergency.note")}</small></p>` : ""}
          ${plan.contacts ? `<div class="divider"></div><p><b>${t("kv.othercontacts")}</b> ${UI.esc(plan.contacts)}</p>` : ""}
        </div>
        ${["assigned", "accepted"].includes(x.status) && x.kaki_code ? `
          <div class="card tint"><h3>${t("kv.yourcode")}</h3>
          <div class="codebox kakicode">${x.kaki_code.split("").map(d => `<span>${d}</span>`).join("")}</div>
          <p>${t("kv.yourcode.body")}</p></div>` : ""}
        ${x.status === "assigned" ? `
          <button class="btn gold" id="acceptV">${t("kv.accept")}</button>
          <button class="btn ghost" id="declineV">${t("kv.decline")}</button>` : ""}
        ${x.status === "accepted" ? `
          ${x.on_way_at
            ? `<div class="card tint"><p>${t("kv.onway.since", { t: UI.hhmm(x.on_way_at) })}</p></div>`
            : `<button class="btn gold" id="onWayV">${t("kv.onway")}</button>
               <p class="f-hint" style="margin:-4px 4px 10px">${t("kv.onway.hint")}</p>`}
          <div class="card warn"><h3>${t("kv.start")}</h3>
          <p>${t("kv.start.body")}</p>
          <div class="otp-in">${[0,1,2,3].map(i => `<input id="o${i}" inputmode="numeric" maxlength="1">`).join("")}</div>
          <button class="btn" id="startV">${t("kv.start.btn")}</button></div>` : ""}
        ${x.status === "in_progress" ? `
          <div class="card"><h3>${t("kv.end")}</h3>
          <p>${t("kv.end.body")}</p>
          ${UI.chipMulti("repChips", ["Went well", "Meal eaten", "Good spirits", "Seemed tired", "Meds issue"], ["Went well"], "report")}
          <label class="f-label">${t("kv.note")}</label>
          <textarea class="f-input" id="repTxt" placeholder="${UI.esc(t("kv.note.ph"))}"></textarea>
          ${plan.meds ? `<div class="chips" id="medsG" style="margin-top:10px">
            <button type="button" class="chip sel" onclick="this.classList.toggle('sel')" data-v="meds">${t("kv.meds")}</button></div>` : ""}
          <button class="btn" id="endV">${t("kv.complete")}</button></div>` : ""}
        ${["accepted", "in_progress"].includes(x.status) ? `
          <button class="btn ghost" id="cancelK">${t("kv.cancel")}</button>
          <div class="card" id="cancelBox" hidden>
            <label class="f-label" for="cancelWhy">${t("kv.why")} <small>${t("common.required")}</small></label>
            <textarea class="f-input" id="cancelWhy" placeholder="${UI.esc(t("kv.why.ph"))}" maxlength="300"></textarea>
            <p class="f-hint">${x.status === "in_progress" ? t("kv.ends") : t("kv.rematch")} ${t("kv.paid")}</p>
            <button class="btn danger" id="cancelGo">${t("kv.cancel.go")}</button>
          </div>` : ""}
        ${x.status === "completed" && x.report ? `
          <div class="card tint"><h3>${t("kv.report")}</h3><p>${UI.esc(x.report.text || "")}</p></div>
          <button class="li" id="flagC"><div class="face gold">⚑</div>
            <div class="body"><b>${t("kv.flag")}</b><span>${t("kv.flag.d")}</span></div></button>` : ""}
      `);
      const ow = UI.el("onWayV");
      if (ow) ow.onclick = async () => { try { await Api.post(`/visits/${id}/on-the-way`); UI.toast(t("kv.t.onway")); visit(id); } catch (e) { UI.toast(UI.terr(e), true); } };
      const a = UI.el("acceptV");
      if (a) a.onclick = async () => { try { await Api.post(`/visits/${id}/accept`); UI.toast(t("kv.t.accepted")); visit(id); } catch (e) { UI.toast(UI.terr(e), true); } };
      const d = UI.el("declineV");
      if (d) d.onclick = async () => { try { await Api.post(`/visits/${id}/decline`); UI.toast(t("kv.t.declined")); location.hash = "#/kaki/home"; } catch (e) { UI.toast(UI.terr(e), true); } };
      [0,1,2,3].forEach(i => { const o = UI.el("o" + i); if (o) o.oninput = () => { if (o.value && i < 3) UI.el("o" + (i + 1)).focus(); }; });
      const s = UI.el("startV");
      if (s) s.onclick = async () => {
        const otp = [0,1,2,3].map(i => UI.el("o" + i).value).join("");
        try { await Api.post(`/visits/${id}/start`, { otp }); UI.toast(t("kv.t.started")); visit(id); }
        catch (e) { UI.toast(UI.terr(e), true); }
      };
      const en = UI.el("endV");
      if (en) en.onclick = async () => {
        try {
          await Api.post(`/visits/${id}/complete`, {
            chips: UI.chipValues("repChips"), text: UI.el("repTxt").value,
            meds_confirmed: UI.el("medsG") ? UI.chipValues("medsG").includes("meds") : false });
          UI.toast(t("kv.t.completed")); visit(id);
        } catch (e) { UI.toast(UI.terr(e), true); }
      };
      const ck = UI.el("cancelK");
      if (ck) ck.onclick = () => { UI.el("cancelBox").hidden = false; ck.hidden = true; UI.el("cancelWhy").focus(); };
      const cg = UI.el("cancelGo");
      if (cg) cg.onclick = async () => {
        const reason = UI.el("cancelWhy").value.trim();
        if (!reason) return UI.toast(t("kv.t.words"), true);
        try { await Api.post(`/visits/${id}/cancel`, { reason }); UI.toast(t("kv.t.cancelled")); location.hash = "#/kaki/home"; }
        catch (e) { UI.toast(UI.terr(e), true); }
      };
      const f = UI.el("flagC");
      if (f) f.onclick = async () => {
        const text = prompt(t("kv.flag.ask"));
        if (!text) return;
        try { await Api.post(`/visits/${id}/care-note`, { chips: ["Kaki concern"], text }); UI.toast(t("kv.flag.sent")); }
        catch (e) { UI.toast(UI.terr(e), true); }
      };
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  async function impact() {
    UI.spin();
    try {
      const visits = await Api.get("/visits");
      const done = visits.filter(x => x.status === "completed");
      const byHousehold = {};
      done.forEach(x => { byHousehold[x.senior_name] = (byHousehold[x.senior_name] || 0) + 1; });
      const repeats = Object.values(byHousehold).filter(c => c > 1).reduce((a, c) => a + c, 0);
      const hours = done.reduce((a, x) => a + (x.estimate?.hours || 2), 0);
      const earned = done.reduce((a, x) => a + (x.estimate ? x.estimate.kaki_fee + x.estimate.transport : 0), 0);
      UI.screen(`
        ${UI.appbar(t("ki.title"), t("ki.sub"))}
        <div class="card" style="background:linear-gradient(150deg,var(--pandan),var(--pandan-deep));color:#fff;border:0">
          <div class="row" style="text-align:center">
            <div class="grow"><div class="mono" style="font-size:1.6rem">$${earned.toFixed(0)}</div><div style="font-size:.7rem;opacity:.85">${t("ki.earned")}</div></div>
            <div class="grow"><div class="mono" style="font-size:1.6rem">${hours}</div><div style="font-size:.7rem;opacity:.85">${t("ki.hours")}</div></div>
            <div class="grow"><div class="mono" style="font-size:1.6rem">${Object.keys(byHousehold).length}</div><div style="font-size:.7rem;opacity:.85">${t("ki.seniors")}</div></div>
          </div>
        </div>
        ${repeats ? `<div class="li"><div class="face">🔁</div><div class="body"><b>${t("ki.streak", { n: repeats })}</b>
          <span>${t("ki.streak.d")}</span></div></div>` : ""}
        ${Object.entries(byHousehold).map(([n, c]) => `<div class="li"><div class="face">${UI.initials(n)}</div>
          <div class="body"><b>${UI.esc(n)}</b><span>${t("ki.together", { n: UI.visitsN(c) })}</span></div></div>`).join("")}
        <div class="card tint"><h3>${t("ki.payouts")}</h3><p>${t("ki.payouts.body")}</p></div>
        ${UI.moneyNote()}`);
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  async function profile() {
    UI.spin();
    try {
      const [p, certs] = await Promise.all([Api.get("/users/me/profile"), Api.get("/users/me/certificates")]);
      const k = p.kaki || { services: [], languages: [] };
      const genderLabel = k.gender === "female" ? "Female" : k.gender === "male" ? "Male" : "Prefer not to say";
      UI.screen(`
        ${UI.appbar(t("kp.title"), p.status === "approved" ? t("kp.sub") : t("kp.sub.pending"), p.status === "approved" ? undefined : "#/")}
        <div class="li"><div class="face" style="width:52px;height:52px;overflow:hidden">${p.photo ? `<img src="${UI.esc(p.photo)}" alt="${UI.esc(t("kp.photo.alt"))}" style="width:100%;height:100%;object-fit:cover">` : UI.initials(p.name)}</div>
          <div class="body"><b>${UI.esc(p.name || UI.contact(p))}</b><span>${t("kp.standing", { t: k.tier || 1, c: UI.esc(UI.contact(p)) })}</span></div>
          <div class="end"><label class="chip" for="photoIn" style="cursor:pointer">${p.photo ? t("kp.photo.change") : t("kp.photo.add")}</label>
            <input type="file" id="photoIn" accept="image/*" capture="user" style="display:none"></div></div>
        <p class="f-hint">${t("kp.photo.hint")}</p>
        <label class="f-label">${t("kp.name")}</label>
        <input class="f-input" id="pname" value="${UI.esc(p.name)}">
        <label class="f-label">${t("kp.phone")}</label>
        <input class="f-input" id="pphone" inputmode="tel" value="${UI.esc(p.phone)}" placeholder="+65 …">
        <label class="f-label">${t("kp.iam")} <small>${t("kp.iam.small")}</small></label>
        ${UI.chipGroup("genG", ["Female", "Male", "Prefer not to say"], genderLabel, "gender")}
        <label class="f-label">${t("kp.services")}</label>
        ${UI.chipMulti("svcG", App.config.services, k.services, "service")}
        <label class="f-label">${t("kp.langs")}</label>
        ${UI.chipMulti("langG", App.config.languages, k.languages, "language")}
        <button class="btn" id="saveP">${t("kp.save")}</button>
        <button class="li" onclick="location.hash='#/kaki/availability'">
          <div class="face">◷</div><div class="body"><b>${t("kp.when")}</b>
          <span>${(k.availability && k.availability.any_set)
            ? Object.entries(k.availability.weekly_hours || {}).filter(([, r]) => r)
                .map(([d, r]) => `${v("weekday", d)} ${r.from}–${r.to}`).join(" · ")
            : t("kp.when.none")}</span></div>
          <div class="end"><span class="pill ${(k.availability && k.availability.any_set) ? "green" : "gold"}">
            ${(k.availability && k.availability.any_set) ? t("kp.set") : t("kp.add")}</span></div></button>
        <div class="eyebrow">${t("kp.certs", { t: k.tier || 1 })}</div>
        ${certs.length ? certs.map(c => `
          <div class="li cert-row"><div class="face">📄</div>
            <div class="body"><b>${UI.esc(c.name)}</b><span class="mono">${UI.esc(c.issuer || "")}${c.expires ? " · " + t("kp.until", { d: UI.esc(c.expires) }) : ""}${c.file_name ? " · " + UI.esc(c.file_name) : ""}</span></div>
            <div class="end"><button class="chip" onclick="KakiView.dropCertificate('${c.id}')">${t("common.remove")}</button></div></div>`).join("")
        : `<div class="card tint"><p>${t("kp.certs.none")}</p></div>`}
        <div class="card">
          <h3>${t("kp.cert.add")}</h3>
          <label class="f-label" for="certName">${t("kp.cert.what")} <small>${t("common.required")}</small></label>
          <input class="f-input" id="certName" placeholder="${UI.esc(t("kp.cert.what.ph"))}" maxlength="80">
          <label class="f-label" for="certIssuer">${t("kp.cert.who")} <small>${t("common.optional")}</small></label>
          <input class="f-input" id="certIssuer" placeholder="${UI.esc(t("kp.cert.who.ph"))}" maxlength="80">
          <label class="f-label" for="certExpires">${t("kp.cert.until")} <small>${t("common.optional")}</small></label>
          <input class="f-input" id="certExpires" type="date">
          <label class="f-label" for="certFile">${t("kp.cert.file")} <small>${t("kp.cert.file.small")}</small></label>
          <input class="f-input" id="certFile" type="file" accept="application/pdf,image/*">
          <button class="btn quiet" id="addCert">${t("kp.cert.btn")}</button>
        </div>
        <div class="card tint"><h3>${t("kp.tier2")}</h3><p>${t("kp.tier2.body")}</p></div>
        <button class="btn ghost" onclick="App.logout()">${t("menu.signout")}</button>`);
      UI.el("addCert").onclick = async () => {
        const file = UI.el("certFile").files[0];
        const name = UI.el("certName").value.trim();
        if (!name) return UI.toast(t("kp.cert.name"), true);
        if (!file) return UI.toast(t("kp.cert.choose"), true);
        try {
          let dataUrl;
          if (file.type.startsWith("image/")) dataUrl = await UI.shrinkImage(file, 1200);
          else {
            if (file.size > 1024 * 1024) return UI.toast(t("kp.cert.big"), true);
            dataUrl = await UI.readDataUrl(file);
          }
          await Api.post("/users/me/certificates", { name, issuer: UI.el("certIssuer").value.trim(),
            expires: UI.el("certExpires").value, file_name: file.name, data_url: dataUrl });
          UI.toast(t("kp.cert.added")); profile();
        } catch (e) { UI.toast(UI.terr(e), true); }
      };
      UI.el("photoIn").onchange = async () => {
        const file = UI.el("photoIn").files[0];
        if (!file) return;
        try {
          const dataUrl = await UI.shrinkImage(file, 320);
          await Api.put("/users/me/photo", { data_url: dataUrl });
          UI.toast(t("kp.photo.saved")); profile();
        } catch (e) { UI.toast(UI.terr(e) || t("common.readphoto"), true); }
      };
      UI.el("saveP").onclick = async () => {
        try {
          const g = UI.chipValue("genG");
          await Api.put("/users/me", { name: UI.el("pname").value.trim(), phone: UI.el("pphone").value.trim(),
            services: UI.chipValues("svcG"), languages: UI.chipValues("langG"),
            gender: g === "Female" ? "female" : g === "Male" ? "male" : "" });
          App.user.name = UI.el("pname").value.trim();
          UI.toast(t("kp.saved"));
        } catch (e) { UI.toast(UI.terr(e), true); }
      };
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  /* Availability: a normal week plus dated exceptions. Most kakis work
     elsewhere, so "Tue and Sat mornings, but I'm away on the 12th" is the
     shape that actually matches their lives. Day ids stay English (day-Mon);
     only the label changes. */
  async function availability() {
    UI.spin();
    try {
      const a = await Api.get("/users/me/availability");
      const days = App.config.weekdays || ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
      const hrs = a.weekly_hours || {};

      UI.screen(`
        ${UI.appbar(t("ka.title"), t("ka.sub"), "#/kaki/profile")}
        <div class="card tint"><p>${t("ka.intro")}</p></div>

        <div class="eyebrow">${t("ka.week")}</div>
        ${days.map(d => {
          const on = !!hrs[d];
          return `<div class="li avail-day" style="align-items:center">
            <input type="checkbox" id="day-${d}" ${on ? "checked" : ""} aria-label="${UI.esc(v("weekday", d))}" style="width:22px;height:22px;accent-color:var(--pandan)">
            <label for="day-${d}" style="width:42px;font-weight:600">${UI.esc(v("weekday", d))}</label>
            <select class="f-input" id="from-${d}" aria-label="${UI.esc(t("ka.from", { d: v("weekday", d) }))}" style="margin:0" ${on ? "" : "disabled"}>${UI.timeOptions(on ? hrs[d].from : "09:00")}</select>
            <span style="padding:0 4px">${t("common.to")}</span>
            <select class="f-input" id="to-${d}" aria-label="${UI.esc(t("ka.to", { d: v("weekday", d) }))}" style="margin:0" ${on ? "" : "disabled"}>${UI.timeOptions(on ? hrs[d].to : "13:00")}</select>
          </div>`; }).join("")}
        <label class="f-label" for="availNote">${t("ka.note")}</label>
        <input class="f-input" id="availNote" value="${UI.esc(a.note || "")}"
          placeholder="${UI.esc(t("ka.note.ph"))}">
        <button class="btn" id="saveAvail">${t("ka.save")}</button>

        <div class="eyebrow">${t("ka.exceptions")}</div>
        ${(a.exceptions || []).length ? (a.exceptions || []).map(e => `
          <div class="li"><div class="face">${e.available ? "＋" : "✕"}</div>
            <div class="body"><b>${UI.esc(e.date)} · ${UI.esc(v("half", e.half_day))}</b>
            <span>${e.available ? t("ka.extra") : t("ka.off")}${e.note ? " · " + UI.esc(e.note) : ""}</span></div>
            <div class="end"><button class="chip" onclick="KakiView.dropException('${e.id}')">${t("common.remove")}</button></div>
          </div>`).join("")
        : `<div class="card tint"><p>${t("ka.none")}</p></div>`}

        <div class="card">
          <h3>${t("ka.adddate")}</h3>
          <label class="f-label" for="exDate">${t("ka.date")}</label>
          <input class="f-input" id="exDate" type="date">
          <label class="f-label">${t("ka.part")}</label>
          ${UI.chipGroup("exHalf", ["all", "morning", "afternoon"], "all", "half")}
          <label class="f-label">${t("ka.working")}</label>
          ${UI.chipGroup("exAvail", ["Not available", "Extra availability"], "Not available", "exception")}
          <label class="f-label" for="exNote">${t("ka.reason")} <small>${t("common.optional")}</small></label>
          <input class="f-input" id="exNote" placeholder="${UI.esc(t("ka.reason.ph"))}">
          <button class="btn quiet" id="addEx">${t("ka.add")}</button>
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
          UI.toast(t("ka.saved"));
          availability();
        } catch (e) { UI.toast(UI.terr(e), true); }
      };

      UI.el("addEx").onclick = async () => {
        const date = UI.el("exDate").value;
        if (!date) return UI.toast(t("ka.pickdate"), true);
        try {
          await Api.post("/users/me/availability/exceptions", {
            date, half_day: UI.chipValue("exHalf") || "all",
            available: UI.chipValue("exAvail") === "Extra availability",
            note: UI.el("exNote").value.trim() });
          UI.toast(t("common.saved"));
          availability();
        } catch (e) { UI.toast(UI.terr(e), true); }
      };
    } catch (e) { UI.toast(UI.terr(e), true); }
  }

  async function dropCertificate(id) {
    if (!confirm(t("kp.cert.remove"))) return;
    try { await Api.del(`/users/me/certificates/${id}`); UI.toast(t("common.removed")); profile(); }
    catch (e) { UI.toast(UI.terr(e), true); }
  }

  async function dropException(id) {
    try { await Api.del(`/users/me/availability/exceptions/${id}`); UI.toast(t("common.removed")); availability(); }
    catch (e) { UI.toast(UI.terr(e), true); }
  }

  return { home, visit, impact, profile, availability, dropException, dropCertificate };
})();
