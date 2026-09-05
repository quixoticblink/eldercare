---
title: "Purpose & Importance of the Eldercare Sprint"
status: solid
last_updated: 2026-09-05
---

# Purpose & Importance of the Eldercare Sprint

## What This Is

This repository is the living working space for the **Eldercare Sprint**—a six-month structured leadership exercise (May–November 2026) run by a five-person team within the **SGLN TECH** programme (Singapore Leaders Network, technology track). It is simultaneously an internal wiki for honest, evolving thinking and a public microsite that judges, coaches, and stakeholders can follow in real time.

This is not a finished product. It is a documented journey from personal motivation to evidence to strategy to prototype to pitch—with every shift in belief preserved along the way.

---

## The Problem We Are Working On

Singapore is aging faster than almost any society in history. By 2030, roughly one in four residents will be aged 65 or older. About 70,000 elderly Singaporeans already live alone. Survey after survey flags loneliness and social disconnection as top-of-list concerns—not just comfort issues, but drivers of cognitive decline, physical deterioration, and premature mortality.

The instinctive response—more care beds, more caregivers, more apps—treats eldercare as a logistics problem. Early fieldwork and research pushed the team toward a harder and more important claim: **the deepest unmet need is not physical care. It is genuine daily connection.**

The team frames the problem through four functions the traditional multi-generational family used to provide:

1. **Physical care** — help with daily activities
2. **Instrumental support** — transport, navigation of systems, logistics
3. **Companionship and social connection** — being seen, having structure, belonging
4. **Cognitive and identity continuity** — being known, remembered, still mattering

Modern infrastructure has begun addressing (1) and (2). It has barely touched (3) and (4). That gap is where this sprint is focused.

---

## The North-Star Question

> **How might we help elderly in Singapore experience genuine daily connection, so that Singapore is brimming with elderly communities that are happy, mentally and physically healthy?**

This question emerged from the convergence of five individual team perspectives and one week of observation-first discovery. It is deliberately not a solution. It is a reframe—insisting that the unit of success is *experienced connection*, not *delivered services*.

The question will sharpen as more fieldwork is done. It is treated as a living hypothesis, not a locked brief.

**Note (2026-08-09):** this remains the *north star* — the outcome we are ultimately arguing for. It is no longer the *working* HMW. Fieldwork moved the working question to the caregiver, and from companionship to respite: see [[reframing/hmw-current]] and the five dated iterations in [[reframing/README]]. Keeping both is deliberate — the north star is what makes the narrow wedge worth doing.

---

## Why This Matters

### At the Singapore level

Singapore is a concentrated, high-fidelity lens on a global trend. The same dynamics—nuclear family structures replacing multigenerational ones, aging populations outpacing caregiver supply, technology penetration rising among seniors—are playing out in Japan, South Korea, Germany, the United Kingdom, and eventually most of the developed world. Insights earned here are designed to generalize.

### At the human level

Loneliness is not a soft problem. Chronic loneliness carries health risks comparable to smoking fifteen cigarettes a day. It accelerates cognitive decline. It shortens lives. And it is **structurally under-served** because it is hard to monetize, hard to measure, and easy to mistake for something else (depression, physical illness, caregiver burnout).

The people the team has spoken with do not primarily describe a lack of services. They describe an **empty calendar**, the loss of roles that gave their days meaning, and the quiet grief of being cared *for* rather than contributing *to* something. The design space that follows from that is very different from the one most technology products have entered.

### At the programme level

The SGLN TECH programme grades this sprint on four axes, each worth 25 points:

| Rubric | What it asks |
|--------|-------------|
| Leadership journey | Did the team learn, adapt, and grow visibly over six months? |
| Quality of thinking | Is the problem understanding rigorous, evidence-led, and intellectually honest? |
| MVP / prototype | Did a real, testable thing get built from that understanding? |
| Presentation | Can the team make judges care and believe? |

This repository is the receipt for all four. The wiki captures the thinking and the changing of minds. The microsite carries the narrative for external audiences. The journal entries preserve the arc. The eventual prototype will be built on top of this foundation.

---

## Why This Repository Exists

Most sprint or hackathon teams lose their reasoning. They arrive at an idea, build a thing, and present it—with no record of what they believed at the start, what evidence changed their minds, or why they chose one direction over another. Judges and coaches see the destination but not the journey.

This repo is built to be different. It is:

- **Observation-first**: no solutioning until the problem is understood
- **Evidence-linked**: every claim in the problem space traces to a source in `knowledge/evidence/`
- **Reframing as a first-class activity**: How Might We iterations are preserved, not overwritten
- **Honest about uncertainty**: interviews are marked with sample sizes; weak evidence is flagged as such
- **A live record of belief change**: the journal and devil's advocate file show what the team believed before fieldwork and what shifted after

The microsite at `site/` is what the world sees. The `knowledge/` wiki is where the real work lives.

---

## The Team

Five people, each bringing a lived lens to the problem:

- **Abhishek Kaul**
- **Lara PuReum Yim**
- **Aditi Agarwal**
- **Shobhit Singhal**
- **Zheng Wei**

Each joined the sprint with family experience of eldercare—caregiving decisions, aging parents, grandparents navigating isolation. That personal grounding is treated as a source of empathy and a risk of bias in equal measure.

---

## Where We Are Now

This section is a snapshot; the living record is at [[maps/timeline]] and updates every week.

As of 5 September 2026 (roughly fifteen weeks in):

- **Round 1 field interviews** (six conversations) completed and synthesized ([[evidence/interview-round-1-findings]]).
- **HMW has gone through five iterations.** Now at *"How might we enable caregivers of the relatively healthy elderly in Singapore to activate trusted respite when a need arises — planned or urgent — layered onto Vanguard's Pasir Ris ICCP pilot as our first operational proof"* ([[reframing/hmw-2026-07-11-broader-need]]). The Jul 8 iteration had narrowed this to crisis-only; we caught that as too tight three days later.
- **Partnership frame is real.** NCSS convenes, Vanguard operationally anchors, AIC provides the sector-level demand data. Vanguard has volunteered a Pasir Ris pilot by year-end. See [[maps/actors]].
- **Strategy activated.** Marketplace 2×2 framework, respite marketplace concept, consistency-as-design-constraint all written up in [[strategy/README|strategy/]].
- **The prototype became a running app.** [[prototype/kakis-app]] — live at **https://singaporekakis.com**, three roles, real sign-in codes to real phones, audited against ISO/IEC 5055. `prototype/` and `pitch/` are both awake.
- **The pilot became a tabletop, and the tabletop happened.** On 3 August Vanguard countered our live-pilot ask with a supervised tabletop exercise ([[journal/2026-08-03-ncss-vanguard]]); no operational pilot inside the Demo Day window, scope narrows to chaperoning. On 18 August NCSS desk-reviewed the app role by role ([[journal/2026-08-18-ncss-app-review]]), and on 21 August eight seniors ran it on their own phones at Care Corner's Toa Payoh 261A AAC with Vanguard and NCSS facilitating ([[journal/2026-08-21-tabletop-vanguard-ncss]]). The concept held; the onboarding around it did not. Two recommendation registers, mapped to app modules: [[prototype/ncss-app-review-2026-08-18]] and [[prototype/tabletop-2026-08-21-feedback]].
- **The feedback is built in.** v1.6 shipped on 5 September — eighteen features from Buckets 1 and 2 of [[prototype/feature-buckets-2026-09-04]], each behind an end-to-end test: the door check both ways (kaki photo and code, then the family's start code), exact times charged by the half hour, gender and same-kaki preferences, cancellation with reasons, certificates read at approval, and the onboarding fixes. The same evening, v1.7 put every caregiver and kaki screen into Mandarin as well, with the coordinator console kept English by design. What shipped and what waits is [[prototype/roadmap]]; the builds are [[journal/2026-09-05-v1.6-build]] and [[journal/2026-09-05-v1.7-language]].

Key early findings that still hold:

- Loneliness is often experienced as **loss of structure**, not just absence of people — the "empty calendar" pattern.
- AI-based companionship faces a **half-life problem**: even willing users notice patterns and disengage.
- The elderly population is **not one segment** — those with structured days at Activity Centres differ fundamentally from those isolated at home or in institutions.
- Connection through **contribution and role** is more durable than connection through charity-shaped visits.
- **Consistency** matters more than intensity — one-off programs do not hold. Now written up as [[strategy/consistency-as-design-constraint]] with a triangulated evidence base.

Sharper findings from July:

- The sharpest pain is **crisis activation** (helper runaway, spousal-couple emergency, discharge scramble), not routine chaperone. Vanguard's own chaperone service runs at 20–30 appointments/month across four centres — small. See [[evidence/vanguard-operational-data]]. *Corrected Jul 11:* crisis is the sharpest moment, not the whole product — planned respite is the same service with a longer lead time, and building for crisis alone yields a product that disappears for eleven months of the year.
- The moat is **not code.** Certification, trust, ecosystem density — none of which is software.
- A **multi-payer stack** (private pay + healthcare fund + philanthropic capital + corporate partners) is required because willingness-to-pay is broken at the senior-facing layer.

Added in August:

- **Supply, not demand, is the binding constraint** — the inverse of the usual marketplace assumption, and it reframes the product. Certification gates supply hard: mobility training → on-the-job training → activation, with CPR cohorts a month or more out. A booking promise the operator can't honour is a harm to a vulnerable person, not a bad user experience. See [[journal/2026-08-03-ncss-vanguard]].
- **Three framings are live at once and nobody has reconciled them:** caregiver relief (ours), resilient caregiving (NCSS), and operational digitisation of an existing manual service (implied by Vanguard's proposed success metric, "lessen your administrative burden", which quietly moves the primary user from the caregiver to the coordinator). This is the most important unresolved thing in the sprint and it is not on anyone's action list.
- **The wall is before the product.** From the 21 August session: wifi, "what is a browser", the approval wait, a placeholder number in a form field. None of it is in the app's module table and all of it decides whether a senior ever reaches the booking screen. Language is a gate, not a localisation ticket — participants understood English and still asked for Mandarin. And every money question was about the *rules* of subsidy, none about the price.
- **The start code proves the wrong thing for NCSS's threat model.** Built to prove a visit was admitted; read by NCSS as an identity check, which it isn't. Both halves are needed. Decide by testing on round 2.

---

## What This Sprint Is Trying to Prove

That a small team, starting from genuine curiosity and honest fieldwork, can produce a more useful and more human understanding of elderly loneliness than desk research alone—and that the understanding can be turned into something testable and worth building.

If it works, the artefacts here become a model for how to approach hard social problems: not with a solution in search of a problem, but with a question rigorous enough to find its own answer.

---

*2026-08-09: re-cut the "Where we are now" snapshot, which had been stuck at mid-July and was still quoting the superseded crisis-only HMW as current. Marked the May 19 question explicitly as the north star rather than the working HMW. Added the running app, the Aug 3 tabletop counter-proposal, the supply-constraint finding, and the three-unreconciled-framings problem.*

*2026-09-04: snapshot re-cut to 4 September. Added the 18 Aug NCSS review, the 21 Aug Table Top Exercise, and the two findings that came out of them (the wall before the product; the start-code direction).*
*2026-09-05: snapshot bumped for v1.6; roadmap linked.*
