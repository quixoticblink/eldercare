---
title: "Kakis prototype — spec v2 (post-feedback build target)"
status: draft
last_updated: 2026-07-21
based_on: [kakis-prototype.html (v1), kakis-design-brief]
feedback_round: "Caregiver/elderly: Lara, Aditi · Respite giver: Shobhit, Aditi · Admin: Zheng Wei, Aditi"
supersedes: v1 of this file (screen mirror with empty FEEDBACK slots — in git history at e2bb2fc)
---

ok so the v1 spec went out, the team walked the live build (eldercare-rho.vercel.app), and three reviews came back — caregiver/elderly (Lara + Aditi), respite giver (Shobhit + Aditi), admin (Zheng Wei + Aditi). This file is now the **v2 build target**: each block records what v1 did, what the feedback said (attributed), and what v2 will be. The prototype gets rebuilt from this document.

**How to read each block:** *v1* → *Feedback (who)* → *v2 target*. Anything marked **[ops]** is a pilot-operations decision, not a prototype change. Anything marked **[tension]** conflicts with an evidence-base constraint and needs a partner ruling before it ships.

---

## 0. Priority register

| Pri | Change | Module |
|---|---|---|
| P0 | "Who needs help today?" role-selection landing; persona switcher removed from consumer surface (ops via deep link `#admin`) | Global |
| P0 | Service-first IA: services shown before urgency; then three urgency tiers (Urgent / Soon / Planned) replacing the binary | Caregiver |
| P0 | Accessibility bump: 48px min tap targets, larger type on pickers, high contrast; "Need help booking? Call Pasir Ris ICCP" on every consumer screen | Global |
| P0 | Elderly self-book module (low-density UX, larger type, simpler language) | New |
| P0 | Respite giver: proper start page (Sign in / Sign up), Singpass consent flow, preference capture, task-centric home | Respite giver |
| P0 | Admin: "Agents" → "Today"; tally fix; matching split into broad-base states + case-by-case | Admin |
| P1 | Editable care plan; add-kaki flow; matching backup + ETA by tier; "Why this price?"; cancellation policy; prompt-chip care notes; add-to-regulars + recurring in one tap | Caregiver |
| P1 | Task detail: OTP start/end, cancel window, cash/cashless label; Impact drill-down; profile with editable prefs + PayNow link | Respite giver |
| P1 | Quality: three categories, archive/retrievable past cases; settings/profile icon | Admin |
| [ops] | SLA commitments per tier, subsidy rules per trigger, payment rail, month-1 volume cap | Vanguard |
| [tension] | Star ratings & feedback shared with organisations vs MOH/AIC no-public-ratings constraint | All |

---

## A. Landing & routing (new, P0)

*v1:* the page opened with a persona switcher (Caregiver / Respite giver / Admin) in the header — a demo affordance, not a product surface.

*Feedback (Lara/Aditi):* consumers never see a persona switcher. Add a landing screen before any module: **"Who needs help today?"** with three routes — "I'm booking for a parent / loved one" → Caregiver · "I'm an elderly person booking for myself" → Elderly self-book · "I want to help as a kaki" → Respite giver. Ops gets a separate build or deep link.

*v2 target:* first screen inside the phone is the role-selection landing. Three large tappable cards (48px+ targets), warm copy, no jargon. The demo's persona tabs move out of the consumer frame: admin reachable only by deep link (`#admin`) or a small "ops" link in the demo shell's footer, clearly marked as not part of the consumer app. The demo-notes panel notes this mirrors "separate builds for ops" in production.

---

## B. Caregiver module (Priya)

### B1. Home / care circle

*v1:* greeting, two CTAs (Get help now / Book ahead), Papa's kakis (regular + backup), one upcoming visit, read-only care plan card.

*Feedback (Lara/Aditi):* works — regular vs backup, upcoming card, care-plan snippet. Gaps: care plan is read-only → make it **editable** (meds checklist, mobility, language, emergency contacts). No **add-kaki flow** → request a familiar kaki from the AAC/Vanguard pool after a first paired visit. Upcoming shows only one item.

*v2 target:* care plan opens into an edit screen (meds ×2 daily with times, mobility, languages, emergency contacts — chip + field editing, Save confirmation). "Papa's kakis" gains a "+ Request a kaki" row → short flow: pick from "people Papa has met" (AAC/Vanguard pool, met-context shown) → request first paired visit. Upcoming becomes a 2–3 item list.

### B2. Service-first entry (restructured, P0)

*v1:* binary "Get help now" (crisis picker) / "Book ahead" (details).

*Feedback (Lara/Aditi):* introduce the **range of services first**, each leading to a timing question: Chaperone (clinic, market, errands) · Companionship (conversation, games, walks) · Wellness check (meals, meds, safety drop-in) · Household help (light chores) · Medicine admin (Tier 2 only — locked/upsell). Then replace the binary with **three urgency tiers**: **Urgent** — need someone now (next 30–60 min) · **Soon** — within the next 2 hours · **Planned** — pick date / recurring.

*v2 target:* Home's booking entry becomes "What does Papa need?" — five service cards (icon, name, examples, duration estimate: chaperone 2–3h, wellness 1h, companionship 1–3h, household 1–2h; medicine admin greyed with "Ask about Tier 2"). Selecting a service → "When?" screen with the three tiers. Urgent and Soon route through the "What happened?" trigger screen; Planned routes to calendar + recurring. Progress indicator "step 1 of 4" across the flow.

### B3. "What happened?" (triggers)

*v1:* six equal-weight trigger cards, reachable only via Get help now; footer link to planned.

*Feedback (Lara/Aditi):* also reachable from **Soon** ("Something's come up"). **Pin top 3 for Pasir Ris**: helper left, spouse hospitalised, caregiver emergency. Add **"Not sure — talk to someone"** → click-to-call ICCP coordinator. Add progress indicator.

*v2 target:* triggers reordered — top row pinned (helper left · spouse hospitalised · my own emergency), marked "most common in Pasir Ris"; remaining three below; seventh card "Not sure — talk to someone" with phone glyph → call sheet "Pasir Ris ICCP coordinator · 6XXX XXXX". Step indicator "2 of 4".

### B4. Details (task/time/language)

*v1:* task chips, when-chips including "Today 2–5pm" on all paths, language chips, free-text note.

*Feedback (Lara/Aditi):* hide same-day slots on the planned path — show **calendar + recurring**; medicine admin greyed with "Ask about Tier 2"; add **duration estimates** per task; **auto-flag first visits** to a new senior (pair with Vanguard staff). Chips too small for stressed 70s+ users → larger type, 48px targets.

*v2 target:* task selection already made at B2, so this screen is timing + language + notes. Planned path: mini month calendar + "repeats weekly" toggle; no same-day chips. Urgent/Soon: time window auto-set by tier (30–60 min / 2 hours), editable. Duration line under the chosen service. If the matched senior–kaki pair is new, an automatic banner: "First visit — a Vanguard care staff will come along." All chips restyled: ≥48px height, 1rem+ labels. Step "3 of 4".

### B5. Matching

*v1:* orb + three narration lines → single match (Halimah).

*Feedback (Lara/Aditi):* show **primary + backup**; show an **unavailable path** (why + next best); show **expected confirmation ETA by tier** (urgent 15 min · soon 45 min · planned 24h).

*v2 target:* result screen shows the primary kaki pass plus a compact backup card ("If Halimah can't make it: Mr Koh — Papa has met him twice"). A demo toggle shows the unavailable state: "Halimah is on another visit until 4pm — next best: Mr Koh (met Papa at the AAC) or wait for Halimah at 4:15." ETA line by tier on the confirmation. Step "4 of 4".

### B6. Confirm + pay

*v1:* price stack ($84 − $45 − $12 = $27), confirm button. No payment method, no subsidy explanation, no cancellation policy.

*Feedback (Lara/Aditi):* add **payment method** (PayNow / linked card / bill ICCP); **"Why this price?"** expandable explaining subsidy logic; **cancellation policy** (free cancel >2h; crisis-fee rules).

*v2 target:* payment selector row (PayNow QR default · linked card · bill to ICCP account); "Why this price?" disclosure expanding to one plain-language paragraph per payer; cancellation line: "Free to cancel up to 2 hours before. Urgent bookings: $10 if cancelled after a kaki is on the way." **[ops]** exact subsidy-per-trigger rules pending Vanguard.

### B7. Visit tracking

*v1:* four-step timeline with live notes; single active visit.

*Feedback (Lara/Aditi):* add **Call / message kaki** (masked number); **escalate to Vanguard coordinator** if late or no-show; Visits tab should hold **history + filters**, not just the active visit; map tracking optional — placeholder for Beta.

*v2 target:* tracking screen gains a contact row ("Message Halimah · Call (masked)") and an "Escalate — running late?" link to the coordinator. Visits tab becomes two segments: Active / History (filterable list: month, kaki, service). A dashed "Live map — coming in Beta" placeholder block.

### B8. Visit report + feedback

*v1:* report in the kaki's voice, structured pills, private care note (free text only), "Book Halimah again."

*Feedback (Lara/Aditi):* one-tap **"Add to regular kakis + schedule recurring"** [P1]; **prompt chips** for the care note: tired after walk · refused meds · fall concern [P1]; **share feedback with the organisations + star ratings**.

*v2 target:* action row: "Make Halimah a regular + repeat every Tuesday" single tap. Care note gains prompt chips (tired after walk / refused meds / fall concern / new confusion / all fine) + free text. Feedback routing line: "Shared with Vanguard and the Kakis quality team." **[tension]** Public star ratings conflict with the MOH/AIC constraint recorded in [[../reframing/devils-advocate]] critique 14 (and Vanguard said it to us directly on Jul 8). v2 compromise pending a partner ruling: a private 1–5 "how did the visit go" signal visible to Vanguard and the quality agent only — never displayed on kaki profiles, never used for consumer-facing ranking. Flagged as an open question for Vanguard (G5).

---

## C. Elderly self-book module (new, P0)

*Feedback (Lara/Aditi):* split caregiver mode vs **elderly self-book** mode — different UX density, language, and payment paths.

*v2 target (first cut):* entered from the landing screen ("I'm an elderly person booking for myself"). Three screens, radically simpler than the caregiver flow: (1) "What do you need?" — four oversized cards (Someone to go with me / Someone to visit me / Help at home / I'm not sure — call me), ≥64px targets, 1.15rem+ type, minimal text, no English idioms; (2) "When?" — Today / Tomorrow / Pick a day, three big buttons; (3) confirmation with the kaki's face, name, and a phone-sized "they will call you before coming" line. Payment defaults to "bill my ICCP account / my family" — no card entry in this mode. A persistent "Call the centre instead · 6XXX XXXX" footer on every screen. Language toggle (EN / 中文 / Melayu / தமிழ்) top-right — static in prototype, real in Beta. Grounded in [[../evidence/marsiling-aac-grab-interviews]] (transaction fear, dialect, vision).

---

## D. Respite giver module (Mdm Tan) — restructured per Shobhit/Aditi

### D1. Start page

*v1:* single welcome screen with "Start onboarding"; bottom tabs (Training / My impact) visible pre-signup.

*Feedback:* tighten copy; two CTAs — **"Already a member: Sign in"** and **"New member: Sign up"**; bottom tabs must not appear on the start page.

*v2 target:* clean start screen — wordmark, one line ("Help a Pasir Ris family. Train free with Vanguard. Choose your own hours."), two buttons: Sign in / Sign up. No bottom nav until authenticated.

### D2. Sign-up flow

*v1:* skills → training → wallet; Singpass mentioned in fine print only.

*Feedback:* **phone number as unique identifier**; **show the Singpass verification flow** in the prototype, including a **consent/approval step** for using Singpass info; services able to provide should **mirror the caregiver service set**; capture preferences — languages, time/day, origination location (low priority in a small pilot), destination preference, email (Singpass doesn't provide it); all preferences editable later in Profile.

*v2 target:* sign-up becomes: (1) phone number + OTP → (2) Singpass screen — mock Myinfo consent listing exactly what's pulled (name, NRIC-verified identity, DOB, address) with "Allow" / "Decline", styled like the real thing → (3) email capture ("Singpass doesn't share this") → (4) services (Chaperone / Companionship / Wellness check / Household help / Medicine admin 🔒 Tier 2 — mirroring B2's set) → (5) preferences: languages (multi), days/times (chips), area (default Pasir Ris), destination preference → (6) then the training path (unchanged in substance: CPR at St. Luke's, mobility, seniors+SOPs, shadow visit).

### D3. Home page (post-login)

*v1:* jobs list, training tab, impact tab.

*Feedback:* home = **upcoming scheduled tasks** (naming TBD — "tasks" feels cold); a tab for **available asks** split **Now (next 30 min, geofenced)** / **In future**; bottom of page: impact summary (hours + money), training, profile.

*v2 target:* home screen: "Your upcoming visits" (renamed from tasks — carried from the kaki vocabulary) as list, each with date, time + duration, and $. Below: compact impact strip (hours · earned MTD). Bottom nav: Visits · Available · Impact · Profile (Training folds into Profile → Training, per D7). "Available" tab: two segments — "Now" (within 30 min, "near you" geofence badge — scripted in prototype) and "Coming up"; a filter row at top reflecting her stored preferences (editable dropdown, multi-select).

### D4. Task (visit) detail

*Feedback:* each item shows date, time incl. duration, $$; detail view: person's name, start/end time, start location + destination, fee, cash or cashless (suggest cashless-only at start, settlement via Vanguard), **cancel option** (allowed up to a cutoff), **Start Task CTA with OTP exchange**, **End Task CTA → feedback/ratings**.

*v2 target:* visit detail screen: who (name + "you've met him 6 times"), when (start–end), where (from → to), fee, payment badge "Cashless · settled weekly via Vanguard" **[ops: confirm cashless-only]**, "Cancel visit" (enabled until 2h before, then greyed with reason), **"Start visit — exchange OTP"** (senior/caregiver reads a 4-digit code, kaki enters it; mocked), **"End visit"** → structured feedback (how did it go chips + note). Rating element subject to the same [tension] ruling as B8 — v2 shows a private "flag a concern" rather than stars.

### D5. Impact

*v1:* earnings card + meaning-led ledger.

*Feedback:* kudos summary; hours contributed (click → task-level detail); money earned MTD (click → detail); **withdraw to linked PayNow**.

*v2 target:* impact screen keeps the kudos framing, adds tappable rows: Hours (27 → per-visit list), Earned MTD ($318.40 → per-visit list), and "Withdraw to PayNow" (mock balance → confirmation). Consistency streak stays — it's the product.

### D6. Training

*Feedback:* trainings done / in progress / certification corner.

*v2 target:* three segments: Done (CPR, mobility, seniors+SOPs with registry IDs), In progress (shadow visit — booked), Certification corner (wallet view + Tier 2 upsell). Substantively v1's content, reorganised.

### D7. Profile

*Feedback:* name **with rating**, contact details, editable preferences, PayNow link, log out, delete/suspend account.

*v2 target:* profile screen: photo + name + Tier badge (+ private quality standing shown as "Good standing · Vanguard-verified" rather than a public star number — same [tension] ruling), phone/email (editable), preferences (languages, days, services — editable, mirrors D2 step 5), PayNow account (masked, relink), Log out, and "Suspend or delete my account" (two-step confirm).

---

## E. Admin module (Wei Lin) — restructured per Zheng Wei/Aditi

### E1. "Agents" → "Today"

*v1:* header stats (41 bookings · 92% consistency · "3 for your review") + three agent cards (badges 2 + 1 + 1 = 4 — tally bug).

*Feedback:* review count doesn't tally (3 vs 4); "consistency score" unclear; rename the page — suggest **"Today"**; unsure bookings/consistency numbers help ops (needs a focus group).

*v2 target:* page renamed **Today**. Tally fixed: "4 items need you" matching the badges. "Consistency score" replaced with a plain label + tooltip: "Repeat-pair rate — % of this week's visits where the senior saw a kaki they already knew (target ≥90%)." Header stats trimmed to what ops acts on: items needing review · unfilled visits today · repeat-pair rate. A demo-note records the open question: validate which numbers ops actually wants with a focus group before pilot.

### E2. Matching — two levels

*v1:* one screen of four toggleable weight sliders + an agent recommendation.

*Feedback (Zheng Wei):* split into **broad base** and **case-by-case**. Broad base: ops shouldn't toggle factor sliders across all cases — confusing. Instead offer **states**: High demand/low supply (reduce consistency weight, favour proximity, fill faster) · Low demand/high supply (favour consistency + language). Algorithm **displayed but not toggleable** at broad base. Case-by-case: per-elderly, agent recommendation shown, **custom weights only here**.

*v2 target:* Matching becomes two screens. **(1) Broad base:** a mode selector with three named states — "Balanced (default)", "High demand / low supply — fill fast: proximity first, consistency relaxed", "Low demand / high supply — deepen bonds: consistency + language first" — each showing its (read-only) weight profile; the matching agent recommends a state ("demand up 40% this week — suggest High-demand mode") and ops confirms. **(2) Case-by-case:** a queue of exceptions by senior (e.g. "Mdm Lee — no Tamil speaker free Tue am"), each opening a detail with the agent's recommendation and — only here — custom weight override for that senior. Hard-rules card unchanged (staff-paired first visits, no public ratings, cert gates, urgent jumps queue).

### E3. Quality — categorised + retrievable

*v1:* weekly theme chips + one flagged case + private-note routing.

*Feedback (Zheng Wei):* categorise into **(a) elderly quality of life** (mental/physical health, living conditions), **(b) respite-giver quality of service** (caregiver feedback about the kaki), **(c) respite-giver quality of life** (volunteering conditions, how caregivers/elderly treat the kaki). Past cases must be **retrievable** — add an **archive**.

*v2 target:* Quality screen gains three category tabs matching (a)/(b)/(c) — note (c) is new ground: the kaki is also a person the platform protects; the quality agent reads visit reports both ways. Each tab: open flags + themes. An **Archive** segment lists resolved cases (searchable by senior, kaki, month) with outcome notes — quality control requires follow-up context. Mr Silva's fatigue case files under (a); a new demo case under (c): "Kaki reports a family member repeatedly cancels on arrival — coordinator to call."

### E4. Settings / profile (new)

*Feedback (Zheng Wei):* profile icon top-right; track which caregiver/respite giver is tagged to cases; app feedback; FAQs/resources/agent for the user.

*v2 target:* avatar icon top-right of the admin frame → sheet: Wei Lin's profile (role, sub-region), "My cases" (items she's touched, with the caregiver/kaki tagged on each), "Send feedback on Kakis", and "Help — FAQs, resources, ask the assistant."

---

## F. Cross-cutting v2 rules

- **48px minimum tap targets and ≥1rem labels** on all consumer pickers; contrast re-checked at AA after the restyle.
- **"Need help booking? Call Pasir Ris ICCP · 6XXX XXXX"** footer on every caregiver/elderly screen.
- **Progress indicators** (step n of 4) across the caregiver booking flow.
- **Ratings stay non-public everywhere** pending the Vanguard/AIC ruling — private quality signals only ([tension], G5).
- Everything else from v1 stands: consistency-first matching, visible cert locks, open multi-payer pricing, senior never installs anything, language as a first-class field.

## G. Open questions for pilot ops / Vanguard

1. **SLA by tier** — can ops commit to <1h (urgent) / <2h (soon) / 24h (planned) for Pasir Ris? (Lara/Aditi)
2. **Pricing & subsidy rules** — is crisis activation always −$45, or trigger-specific? (Lara/Aditi)
3. **Payment rail** — PayNow to Vanguard vs in-app vs invoice? Cashless-only for kakis at launch, settlement via Vanguard? (Lara/Aditi; Shobhit)
4. **Volume** — demo shows 41 bookings/week; what's a realistic month-1 cap? (Lara/Aditi)
5. **Ratings** — the team wants feedback shared with organisations + star ratings; MOH/AIC hesitancy says no public rating of care staff. What exactly is permitted: private scores to Vanguard? Aggregate-only? Nothing numeric? (All → Vanguard/AIC)
6. **Ops metrics** — which numbers does the coordinator actually act on? Focus group before pilot. (Zheng Wei)

---

*2026-07-21: v2 — integrated the three team reviews (Lara/Aditi caregiver+elderly, Shobhit/Aditi respite giver, Zheng Wei/Aditi admin) into a build target. v1 (the plain screen mirror with empty FEEDBACK slots) is preserved in git history. Prototype rebuild to follow on request.*
