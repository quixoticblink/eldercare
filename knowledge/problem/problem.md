---
title: "The problem — caregiver respite for specific eldercare tasks"
aliases: [problem statement, respite problem]
status: draft
last_updated: 2026-07-11
prereqs: [eldercare]
---

ok so here is the problem in one sentence: **family caregivers in Singapore need to hand off specific, time-bounded eldercare tasks to trusted others — and there is no service today that lets them do that at the timing and price they can absorb.**

*Specific, time-bounded, trusted others.* Each word is carrying weight. Read on if you want to know why.

## The four functions, and the seam

[[../eldercare]] argues that eldercare is not one thing — it is at least four functions the old multi-generational family used to bundle together: **physical care** (ADLs like bathing and medication), **instrumental support** (logistics, transport, appointments), **companionship** (presence, existence-of-witness), and **cognitive/identity work** (being known and remembered).

Modern Singapore infrastructure has partially solved function 1 (nursing homes, home care sensors, foreign domestic workers) and function 2 (Medical Escort Transport, subsidised transport). Functions 3 and 4 are barely touched at institutional scale — [[../evidence/singapore-eldery-stats-2]] documents this at population level.

The interesting problem is not in any single function. It is at the **seam** — the concrete tasks that require *two functions at once* and cannot be handed off to a helper who only knows one of them. That seam is where family caregivers live, and where they burn out.

## What "specific, time-bounded" looks like

Not respite in the abstract. Specific tasks with specific triggers and specific time boxes:

- *"Take Grandma to the polyclinic on Tuesday morning."* Chaperone. Two hours. Requires: mobility support (function 1) + navigation and coordination (function 2) + patient company (function 3).
- *"Administer her diabetes medication at 2pm when I'm in a meeting."* Medicine administration. Ten minutes. Requires: clinical training (function 1) + trust + presence.
- *"Sit with Dad for two hours so I can pick up my son from soccer."* Companionship block. Two hours. Requires: presence (function 3) + supervision (function 1) + being someone Dad recognises (function 4).
- *"Watch Mum overnight because my brother is in the hospital."* Night respite. Twelve hours. Requires: overnight vigilance, capacity to handle mid-night crises, medication timing.
- *"Come every Wednesday afternoon while the FDW has her day off."* Recurring gap-fill. Three hours weekly. Requires: relationship stability, task variety.
- *"Come tomorrow. My helper ran away."* Crisis activation. One to two weeks of bridging care. Requires: rapid onboarding, tolerance for uncertainty, wide task range.

Each of those is a task, not a service category. A caregiver-respite marketplace has to think in tasks first, not in service categories.

## Why existing options don't fit

Six real options, all real gaps.

- **Foreign Domestic Workers (FDWs)** cover custodial and household work well. They do not cover medical accompaniment, specialised care, or task-specific certification. When an FDW runs away or resigns — [[../evidence/vanguard-operational-data|Vanguard flagged this as one of the six crisis triggers]] — the family is exposed with no bridging option.
- **Medical Escort Transport (MET)** is government-subsidised but scheduled, not on-demand. The 2–3 week lead time is fatal for the crisis-activation cases.
- **Commercial providers ([[../landscape/luce-sg]], Homage, Jagami)** exist. Luce specifically is closest to what we might build — AIC-accredited caregivers, same-day booking, ~$25/hour. But they don't segment by task category, don't cover the crisis-activation wedge as a headline offering, and don't integrate with the ICCP sub-region infrastructure.
- **[[../landscape/vanguard|Vanguard's Community Chaperone pilot]]** covers exactly one category (chaperone) at exactly one operator, at 20–30 appointments/month across four centres. Small. Not marketed. Manually matched.
- **Nursing homes** are last-resort institutional. They exist for high medical complexity, not for two-hour respite. Regulatory constraints prevent them from flexing to short-term coverage.
- **Family / volunteer help** is the ideal answer that people wish worked. It usually doesn't. Family members have jobs. Volunteers rotate — the "posters looked super old" pattern in [[../humans/2026-05-25-frontline-caretaker-old-age-home]] and [[../landscape/lee-ah-mooi-old-age-home]] shows what a broken volunteer pipeline looks like.

The pattern in the gaps: **there is no supply layer that can be booked task-by-task, on the timeline the caregiver needs, at the price the household can absorb.**

## The solution direction: a matching platform, task-typed

The convergent answer across the wiki — [[../strategy/respite-marketplace-concept]], [[../strategy/marketplace-2x2]], and the current [[../reframing/hmw-2026-07-08-post-vanguard|HMW]] — is a **matching platform between family caregivers and a curated supply of gig workers and community caregivers**, organised around specific task categories with matching trust requirements.

Concretely, the supply layer draws from three overlapping pools:

- **Certified gig workers** — the model Luce already operates. AIC-accredited caregivers on a gig basis. Trained through the same pipelines Vanguard uses ([[../landscape/vanguard]]'s CPR training at St. Luke's, mobility half-day, dementia basics). Paid $10–22/hour depending on task complexity, working single-caller shifts as their schedule allows. The economically-defensible base of the pool.
- **Young-elderly community caregivers** — the model Vanguard's micro-jobber programme is piloting. Well/robust seniors in their early 60s, early retirees who don't need income but want structure and contribution. Motivated differently from gig workers; loyal, low-turnover, cheaper. Aligned with the [[../strategy/consistency-as-design-constraint|consistency constraint]] because they don't rotate.
- **Potentially AV-displaced Grab drivers** — Lara's July 8 thread. Existing gig workforce, needing career transition, with proven capacity to follow assignment logic and handle intermittent trust-based work. Unproven whether the pipeline is real.

Demand routes to supply through **task-typed matching**: chaperone workers matched to chaperone tasks, medicine-administration-certified workers to medication tasks, night-respite workers to overnight care. Not a single pool where everyone does everything.

## Task categories the platform has to cover

At MVP, likely three of these; the full six over time:

1. **Chaperone** — accompanied appointments (clinic, dental, dialysis, physio), errands, meal outings. Low clinical burden; high trust and mobility burden. This is the closest thing to what MET does with a subsidy and what [[../landscape/community-chaperone|Vanguard's Community Chaperone pilot]] does with a small team.
2. **Medicine administration** — timed medication delivery and supervision, blood-sugar checks, blood-pressure monitoring, injection administration where nurse-qualified. Higher clinical burden; requires structured training and certification tier.
3. **Wellness checks and supervision** — drop-in to confirm meals, meds, safety; fall-risk supervision; dementia wandering / sundowning watch; overnight supervision.
4. **Companionship blocks** — one-to-three-hour presence, cognitive stimulation, games (mahjong, cards), reading, walks. Low clinical burden; but heavy on the [[../strategy/consistency-as-design-constraint|consistency constraint]] because relationship is the product.
5. **Household and errands** — meal prep, light housekeeping, groceries, pharmacy runs. Overlaps significantly with what an FDW would cover; but time-bounded and on-demand rather than live-in.
6. **Specialised respite** — dementia-trained cover, palliative respite, skilled nursing tasks. Reserved for a higher certification tier; small volume but high value.

## Design constraints that shape the platform

These are the load-bearing constraints; whichever platform we build has to satisfy them or fail visibly.

- **[[../strategy/consistency-as-design-constraint|Consistency]]** — seniors *repel* new helpers at first contact and need months to adjust. The platform cannot rotate supply freely; matching must be sticky at the senior level.
- **Multi-payer stack** — private pay alone can't fund it because willingness-to-pay is broken at the senior-facing layer. The stack is private pay + healthcare fund + philanthropic capital + corporate partners (hotel partners for stays, employer benefits, foundation grants).
- **MOH / AIC hesitancy on preference matching** — rating and ranking of care staff is politically sensitive at ministry level ([[../reframing/devils-advocate]] critique 14). The UX cannot be a stars-and-reviews consumer marketplace.
- **Language and vision affordances** — [[../evidence/marsiling-aac-grab-interviews]] flagged that many seniors speak dialect only and have vision problems. The caregiver interface has to be the caregiver's phone; the senior UI is a design that doesn't exist yet.
- **Certification is the moat** — see [[../strategy/marketplace-2x2]]. The certification layer is what commercial competitors already have; our differentiation cannot be that we also have it. Our differentiation has to be *task-typing + multi-payer stack + ICCP integration*.

## Why now

Three converging vectors make this the right moment.

- **Vanguard has volunteered a Pasir Ris pilot by year-end 2026** — an operational anchor exists in a way it didn't a month ago ([[../journal/2026-07-08-vanguard-visit]]).
- **AIC and NCSS have certification funding** for provider training that a commercial builder would have to buy — free supply-side onboarding for us.
- **The ICCP 85-sub-region framework** ([[../landscape/iccp-model]]) means we can build sub-region-native from the start rather than fighting for national coverage; Pasir Ris is a defensible starting geography.

## What confused us / open questions

- The multi-payer stack is currently a phrase. What are the actual amounts, actual payer boundaries, actual pathways to trigger each payer? Business-case scaffold is the immediate work.
- Task-typed matching implies task-typed certification. Vanguard's chaperone training is half a day. Medicine administration certification is different. How do we tier certification without becoming a training company?
- Consistency vs on-demand: Vanguard's operational answer (first-session-with-staff, then micro-worker for repeats) is a partial solution. At platform scale it might break — needs testing.
- Gig-worker versus employee is the labor-model question deferred to Vanguard. Different answer changes the entire cost structure.

## Connects to

[[../eldercare]] is the problem-space overview this entry narrows from. [[../reframing/hmw-2026-07-08-post-vanguard]] is the working HMW this entry articulates the problem-side of. [[../strategy/respite-marketplace-concept]] is the solution-side companion. [[../strategy/marketplace-2x2]] is the framework for positioning the platform. [[../strategy/consistency-as-design-constraint]] is the load-bearing constraint. [[../landscape/vanguard]], [[../landscape/community-chaperone]], [[../landscape/aic]], [[../landscape/iccp-model]] are the partnership infrastructure. [[../landscape/luce-sg]] is the closest live competitor. [[../evidence/vanguard-operational-data]], [[../evidence/ncss-idi-findings]], [[../evidence/interview-round-1-findings]] are the evidence base.

## Proposed sibling / child entries

- [[caregiver-respite-task-taxonomy]] — the six task categories written up as a proper taxonomy with training tiers, price bands, and certification requirements.
- [[gig-worker-supply-model]] — the specific case for building supply from gig workers, community caregivers, and job-transitioning older workers.
- [[caregiver-persona-map]] — the demand-side counterpart to [[../humans/empathy-map-2]] — an empathy map for the family caregiver, currently missing.
- [[matching-mechanics-respecting-consistency]] — the specific matching algorithm design that respects the consistency-as-design-constraint at platform scale.
- [[../strategy/multi-payer-stack]] — the funding-model entry (still a proposed stub in [[../maps/proposed-stubs]]).
- [[../strategy/crisis-activation-wedge]] — the six crisis triggers written up as their own entry (still a proposed stub).
