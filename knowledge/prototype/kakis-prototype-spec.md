---
title: "Kakis prototype — full screen-by-screen spec (feedback copy)"
status: draft
last_updated: 2026-07-11
based_on: [kakis-prototype.html, kakis-design-brief]
purpose: annotate this file with feedback; the prototype gets updated from it
---

This is the complete written mirror of `kakis-prototype.html` — every screen, every element, every piece of copy, every interaction. It exists so feedback can be left directly in this file. **How to give feedback:** every block ends with a `> FEEDBACK:` line — write under it. Add, strike, or rewrite anything; the prototype will be updated to match.

Working name throughout: **Kakis** (provisional).

---

## 0. Global shell — what wraps every screen

**Top bar (page, not phone):** "Kakis." wordmark (green serif, gold full stop) · tagline "*Trusted respite when a need arises.* Prototype · Pasir Ris ICCP pilot · SGLN TECH 2026" · three persona tabs: **Caregiver / Respite giver / Admin** (pill toggle, active tab solid green).

**Left panel (desktop only):** scenario card for the active persona — who they are, their situation, and a suggested walk-the-flow order.

**Centre:** a phone frame (390×800, dark bezel, rounded). Inside: status bar (09:41 · Kakis. · PASIR RIS), the active screen, and a persona-specific bottom nav (Caregiver: Home / Get help / Visits · Respite giver: Visits / Training / My impact · Admin: Agents / Onboarding / Matching / Quality).

**Right panel ("Demo notes"):** updates per screen — explains the design intent and lists the evidence files it's grounded in. Built for Demo Day narration.

**Design tokens:** pandan green `#14594A` primary, marigold `#F0A63C` reserved for urgent/activation moments, porcelain-green paper background, clay red only for locks/alerts. Type: Fraunces (display), Instrument Sans (body), Spline Sans Mono (IDs, timestamps, agent logs). No public star ratings anywhere, by design (MOH constraint).

> FEEDBACK:

---

## 1. Caregiver journey (persona: Priya, 41 — father Mr Nathan, 78, Tamil-speaking, walks with a stick; helper left this morning)

### 1.1 `cg-home` — Home / care circle

- Greeting: "Morning, Priya — Caring for Mr Nathan · Pasir Ris Dr 4".
- **Two peer CTAs:** marigold "⚡ Get help now — *urgent, matched within hours*" → trigger picker; green "Book ahead — *planned visits, appointments, vacations*" → straight to request details in planned mode.
- **"Papa's kakis"** list: Mdm Halimah, 63 (Chaperone & companionship · 6 visits with Papa · Tamil + English · pill "Regular") and Mr Koh Teck Seng, 61 (Wellness checks · 2 visits · met Papa at the AAC · pill "Backup").
- **Upcoming:** "Polyclinic escort — Tue 14 Jul, 9:30am · Halimah accompanies Papa · 2 hrs".
- **Care-plan card** (tinted): "Diabetes meds 2pm daily · walks with a stick · prefers Tamil · Tuesdays: physio. Kept up to date so any kaki arrives prepared." + button "View last visit report".

> FEEDBACK:

### 1.2 `cg-crisis` — "What happened?" (urgent path; the signature screen)

Header: "What happened?" / sub "Kakis is built for the moments care plans break". Six tactile trigger cards in a 2×3 grid (select one → highlights marigold, enables Continue):

1. 🧳 **Helper left suddenly** — bridging care for 1–2 weeks while you find a replacement
2. 🏥 **Spouse hospitalised** — one parent in hospital, the other now alone at home
3. 🛏️ **Discharge, no plan** — coming home from hospital and nobody's ready
4. 📉 **Sudden decline** — a fall, surgery or illness; weeks of extra help needed
5. 🕊️ **Loss of a spouse** — steady presence through the hardest months
6. 🆘 **My own emergency** — you're unwell or called away; someone trusted steps in

Footer link: "Not urgent? **Book a planned visit instead**".

> FEEDBACK:

### 1.3 `cg-details` — "What does Papa need?" (shared by urgent + planned)

Header echoes the chosen path (e.g. "Helper left suddenly · crisis activation" or "Planned visit · days or weeks ahead"). Fields, all chip-based single-select:

- **Task type:** Chaperone (selected) · Wellness check · Companionship · Household help · Medicine admin 🔒 (locked — greyed, not selectable).
- **When:** Today 2–5pm (selected) · Tomorrow am · Pick a date… · Every Wednesday (recurring).
- **Language with Papa** ("seniors settle faster in their own language"): Tamil (selected) · English · Mandarin · Hokkien · Malay.
- **Free-text note:** prefilled "Walks with a stick. Gets anxious with new faces — introduce slowly."
- CTA: marigold "Find Papa's kaki".

> FEEDBACK:

### 1.4 `cg-matching` — matching in progress

Pulsing green-gold orb + three timed status lines that narrate the algorithm's priorities:
1. "Checking Papa's regular kakis first — familiar faces before new ones."
2. "Halimah is free 2–5pm · Tamil ✓ · Tier 1 chaperone ✓"
3. "Applying subsidies from the Pasir Ris care fund…"
Auto-advances to the match result (~4s).

> FEEDBACK:

### 1.5 `cg-matched` — "Halimah can come" + the kaki pass + the price stack

- **The kaki pass** (dark green card, dashed perforation, signature element): gold avatar "HM", "Mdm Halimah — Chaperone & companionship · Pasir Ris", chips "Tier 1 · Chaperone-ready / Speaks Tamil / CPR certified", consistency line "Papa knows her — **6 visits together** since May. No re-introduction needed.", mono footer "KAKI-PR04-0117 · CERT VERIFIED BY VANGUARD · SHOW THIS PASS TO PAPA".
- **"What you pay" stack** (receipt style): Visit rate 3 hrs × $28 = **$84.00** → Community care subsidy (Vanguard healthcare fund · crisis activation) **− $45.00** → Foundation top-up (philanthropic pool · means-tested) **− $12.00** → **You pay $27.00**.
- Buttons: "Confirm booking" / "Change details".
- (Not shown in this scenario but designed: if no regular is available, the match is a new kaki and the card states "first visit comes with a Vanguard care staff".)

> FEEDBACK:

### 1.6 `cg-tracking` — live visit

Timeline: Booking confirmed (11:02, care plan shared) → On the way (13:44, "arriving by bus 15 — about 12 minutes out") → **With Papa now** (14:07, live note in Halimah's voice: "Uncle recognised me straight away lah. We're off to the market, then his 2pm meds.") → Visit report (pending). Tinted card: "2pm medication reminder — Halimah has Papa's checklist. She'll confirm in the visit report — you don't need to call."

> FEEDBACK:

### 1.7 `cg-report` — visit report + private care note

- Report card in Halimah's voice: market trip, fish for dinner, 2pm meds ticked, good spirits, kampong story, tea and radio. Structured pills: "Meds taken ✓ · Meal eaten ✓ · Mood: cheerful".
- **Private care note** (tinted): "Anything our care team should know? This goes to a care coordinator — **never** to a public rating." + free-text field.
- Buttons: "Book Halimah again" / "Done".

> FEEDBACK:

---

## 2. Respite giver journey (persona: Mdm Tan Bee Lian, 62 — early retiree, Pasir Ris, joins via her AAC)

### 2.1 `rg-welcome` — onboarding invitation

Centered: 🤝 · "**Be somebody's kaki**" · "Families in Pasir Ris need a trusted hand when a crisis hits — a hospital visit, a helper gone, a spouse in decline." · "Train free with Vanguard. Help on your own schedule. Earn while you're at it." · pills: "Free certified training / $10–12/hr + transport / You choose your hours" · CTA "Start onboarding" · fine print "Identity is verified with Singpass. Training is run by Vanguard, certified at St. Luke's Hospital."

> FEEDBACK:

### 2.2 `rg-skills` — "What can you help with?"

- 🚶 **Chaperone** — Selected ✓
- ☕ **Companionship** — Selected ✓
- 🩺 **Wellness checks** — tap to add (toggles)
- 💊 **Medicine administration** — 🔒 Tier 2 (visible but locked: "needs the clinical module — unlocks after Tier 1")
- 🧠 **Dementia care** — 🔒 Tier 2 (locked: "needs Vanguard's dementia module")
- CTA "Continue to training".

> FEEDBACK:

### 2.3 `rg-training` — "Your training path" (Vanguard's real modules)

Progress card "Tier 1 — Chaperone-ready · 3 of 4 done" (75% bar), then:

- ❤️ **CPR + AED** — external certification · St. Luke's Hospital · half day — **Passed ✓**
- 🦯 **Mobility assistance** — wheelchair, frames, safe transfers · half day, in-house — **Passed ✓**
- 🗣️ **Working with seniors** — first introductions, dialects, when to call for help · SOPs — **Passed ✓**
- 👥 **Shadow visit with Vanguard staff** — "your first real visit, alongside a care staff — Thu 16 Jul, 10am, Pasir Ris SCC" — **Booked** (marigold; this is the pre-relationship layer)
- 🧠 **Dementia basics (Tier 2)** — greyed, "After Tier 1"
- CTA "View my certification wallet".

> FEEDBACK:

### 2.4 `rg-wallet` — certification wallet

- Her own kaki pass: "Mdm Tan Bee Lian — Respite giver · Pasir Ris sub-region", chips "Tier 1 · pending shadow visit / Chaperone / Companionship", note "One step left: your shadow visit on Thu 16 Jul. After that, you'll appear in family matches." Mono: "KAKI-PR04-0212 · SINGPASS VERIFIED · TRAINING BY VANGUARD".
- Certificates with registry IDs: CPR + AED (STL-2026-8841 · expires Jul 2028) · Mobility (VGD-MOB-3307) · Seniors + SOPs (VGD-SOP-3308) — all "Valid".
- CTA "See available visits".

> FEEDBACK:

### 2.5 `rg-jobs` — "Visits near you"

Intro card: "**Your regulars** — families you've helped before see you first — seniors settle best with a face they know." Then offers (filtered by certs + language, stated at the bottom):

1. ⚡ **Crisis · Chaperone, today 2–5pm — $36 + transport** · Mr Nathan, 78 · Pasir Ris Dr 4 · "**you've visited him 6 times**" · Tamil (marigold-tinted)
2. **Polyclinic escort, Tue 9:30am — $24 + transport** · Mdm Chua, 81 · "first visit — paired with Vanguard staff"
3. **Companionship, every Wed 3–5pm — $22 + transport** · Mr Silva, 76 · recurring weekly · mahjong kaki wanted · English

> FEEDBACK:

### 2.6 `rg-job` — visit detail + accept

- "Why you were matched" card: 6 prior visits, helper-runaway context, Tamil match.
- "The visit" card: market trip, 2pm diabetes meds against checklist, walks with a stick — take the lift, daughter Priya reachable in-app. Pills: Chaperone / Meds checklist / 3 hours.
- Pay stack: 3 hrs × $12 = $36.00 + transport $3.20 = **you receive $39.20**.
- CTA "Accept this visit" → morphs to "✓ Visit accepted — see you at 2pm", then auto-advances to My impact.

> FEEDBACK:

### 2.7 `rg-earnings` — "My impact"

- Dark green header card: **$318.40 earned · 27 hours** (July).
- Ledger leads with meaning, not money: "4 seniors, 11 visits (Mr Nathan 6, Mdm Chua 2, Mr Silva 2, Mdm Wong 1)" · "Consistency streak: 6 repeat visits — seniors do best with faces they know" · "2 crisis activations covered (a helper runaway and a post-discharge week)".
- Nudge card: "Tier 2 within reach — complete dementia basics to unlock dementia-care visits — higher rate, and Pasir Ris needs 5 more Tier 2 kakis." + "Book the module".

> FEEDBACK:

---

## 3. Admin — agent console (persona: Wei Lin, ops lead, Vanguard Pasir Ris pilot)

### 3.1 `ad-overview` — "Ops · Pasir Ris"

- Header stats (dark card): **41 bookings this week · 92% consistency score · 3 for your review**.
- **Three agent cards** (tap into each):
  - **Onboarding agent** — "Verified 12 applicants against St. Luke's + Singpass records · **2 flagged for you**"
  - **Matching agent** — "34 visits auto-matched, regulars preserved · **1 exception**: no Tamil-speaking kaki free Tue am"
  - **Quality agent** — "Read 18 visit reports · overall positive · 1 senior showing repeat fatigue — suggests a check-in call"
- "Why agents?" card: Vanguard's manual pattern (phone triage + WhatsApp rosters) works at 20–30 bookings/month; agents do the routine 90% so one coordinator can run 200+. Every agent action keeps its evidence trail; you approve, they execute.

> FEEDBACK:

### 3.2 `ad-onboarding` — onboarding queue

- **Mdm Tan Bee Lian, 62** (needs decision) — agent's mono evidence trail: "✓ Singpass verified · ✓ CPR STL-2026-8841 matched St. Luke's registry · ✓ Mobility + SOP passed (Vanguard LMS) · ◐ Shadow visit booked, not yet done · ⚠ Dementia module not taken". **Agent recommends:** approve at Tier 1, chaperone + companionship only, dementia locked. Buttons: "Approve at Tier 1" (one tap) / "Hold for interview".
- **Mr Rajesh Kumar, 58** (flagged) — ex-Grab driver via the GrabTask transition pool; CPR valid but the caregiving reference document looks reused from another application. **Agent recommends:** request original + video interview. Button: "Request documents".
- Footer: "10 applicants auto-cleared this week — all records matched, auto-scheduled for shadow visits."

> FEEDBACK:

### 3.3 `ad-matching` — matching weights + agent recommendation

- **Four live sliders:** Consistency (same kaki, same senior) **45%** · Language match **20%** · Proximity (within sub-region) **20%** · Speed to fill **15%**.
- **Agent recommendation card:** two Hokkien-speaking seniors got English-only kakis this week; both first visits went poorly. **Raise language to 30% (from speed).** Simulated on last month's 163 bookings: fill time +18 min, first-visit success 84% → 93%. Buttons: "Apply recommended weights" (updates the sliders) / "Dismiss".
- **Hard rules no agent can override** (tinted card): first visit to a new senior → paired with Vanguard staff · no public ratings or rankings of care staff (MOH) · certification tier must cover the task — no exceptions · urgent triggers jump the queue.

> FEEDBACK:

### 3.4 `ad-quality` — quality patterns (never public ratings)

- **This week's themes** (18 reports read): "Meds adherence strong (11)" · "Seniors greeting kakis by name (7)" · "Transport delays, Elias Rd (3)" · "Fatigue flags (1)".
- **Flagged case — Mr Silva, 76:** three consecutive reports mention tiring quickly and skipping his walk; individually minor, together a pattern the family may not have connected. **Agent recommends:** care-coordinator check-in call + flag to the Vanguard nurse for the next PHV touchpoint. Buttons: "Schedule the check-in" / "Mark as noted".
- Priya's private care note ("Papa seemed tired after the market trip") shown routed here and filed against the same pattern check.
- "Why no stars?" card: MOH/AIC won't permit public rating of care staff — quality lives in structured reports, private notes, and patterns, reviewed by a human.

> FEEDBACK:

---

## 4. Cross-cutting behaviours

- **Consistency-first matching** everywhere: regulars ranked first, reasons stated, first-visit-with-staff for new pairs.
- **Certification gates tasks** — locked states are visible, never hidden (the path up is the point).
- **Multi-payer stack shown openly** on every price ($84 → $27 example).
- **No public ratings anywhere**; feedback = private care notes → quality agent → human.
- **The senior never installs anything**; trust reaches them as a person + the kaki pass artifact.
- **Language is a first-class matching field** (incl. Hokkien, Teochew via "Mandarin/Hokkien/Malay/Tamil/English" chips).
- Deliberate scope cuts: no real algorithm, no payments, no senior-facing surface, agents scripted (see [[kakis-design-brief]]).

> FEEDBACK:

---

## 5. Open design questions we'd most value feedback on

1. Should **planned bookings** get their own confirmation flow (calendar-style) instead of sharing the urgent flow's matching screen?
2. Is the **kaki pass** the right trust artifact — and should it be printable/physical for the senior?
3. Pricing display: is showing the full **multi-payer breakdown** reassuring or confusing for a stressed caregiver?
4. Respite-giver framing: does "**My impact**" (contribution-first) land, or should earnings lead?
5. Admin: is **one coordinator + three agents** the right shape, or should the matching-weights screen be hidden behind an "advanced" flap?
6. What's missing for the **Aug 20 pressure test** — which screen would Vanguard poke first?

> FEEDBACK:
