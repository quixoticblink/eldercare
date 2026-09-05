---
title: "Feature buckets after the August feedback round — 2026-09-04"
status: solid
last_updated: 2026-09-04
based_on: [prototype/tabletop-2026-08-21-feedback, prototype/ncss-app-review-2026-08-18]
---

The two registers ([[tabletop-2026-08-21-feedback]], [[ncss-app-review-2026-08-18]]) hold
seventy-odd items. This is the cut: what gets built next, in what order, and what waits.
It was made against three things — how often an ask repeated across sources, what the
v1.5 codebase can absorb without a rewrite, and what Homage and CaregiverAsia already
ship as table stakes.

The repetition test first. Asked by all three Aug 21 sources *and* by NCSS: gender
preference, kaki photo, exact times and flexible duration, arrival/ETA, hours in the kaki
notification, language matching, cancellation after match, subsidy rules. Those are the
spine of Buckets 1 and 2.

The market test second. Homage books on four hours' notice, lets a family request the
same caregiver again, and ships care reports. CaregiverAsia books in 30-minute units from
thirty minutes to eight hours. Kakis already has same-day (urgent) booking and reports;
it lacks the photo, the time granularity and the repeat-kaki ask. Those are table stakes,
not differentiators. What Kakis has that they don't — no public ratings, the one-way
start code, a coordinator in the loop, every subsidy figure shown with its source — is
the differentiator, and nothing below touches it.

Two decisions taken on 2026-09-04 that shape Bucket 2: flexible duration is charged at
the same hourly rate, prorated to the half hour; and identity runs both ways — the kaki
shows a **photo and a 4-digit kaki code** to the caregiver, then the caregiver's code is
entered to start the visit. Both halves, not one or the other.

**Status 2026-09-05:** Buckets 1 and 2 are live as v1.6. Bucket 2 item 1 shipped with
30-minute input steps (not 15); item 5 keeps mobility and the emergency contact visible
to a household-help kaki and hides age, medications and notes.

## Bucket 1 — days each, mostly one module, no or trivial schema change

In this order.

1. Approval-wait screen copy: "Nothing to do, we'll message you when approved." (M-USERS)
2. Remove the placeholder number in the phone field; label above, empty box. (M-AUTH)
3. Required vs optional markers on the booking form; back-navigation survives a refresh. (M-VISITS frontend)
4. Bug: urgent request after 5pm still offers the 2–5pm window. (M-VISITS)
5. Notify the caregiver on assignment. `notify()` exists and fires for the kaki only. (M-VISITS)
6. Hours and task type in the kaki's assignment message; "you don't need to keep the app open" on the kaki home. (M-VISITS, M-HELP)
7. "Kaki on the way" button that messages the caregiver. The cheapest possible ETA. (M-VISITS)
8. Booking pulls the senior's language from the care plan; multi-select; Cantonese added to the list. (M-CARE, M-CORE constants)
9. Explain the start code on the screen where it happens. Coordinator dashboard counts become links. Care plan: bedridden option, emergency contact split into name/relationship/number, care plan moved to top, profile editable. (M-VISITS copy, M-ADMIN, M-CARE, M-USERS)
10. "Others, please specify" on the trigger step. Max advance-booking horizon as a coordinator setting. (M-VISITS, M-CORE settings)
11. Notify the emergency contact on visit start and complete, using the contact already in the care plan. (M-CARE, M-VISITS)

## Bucket 2 — one build round each, schema change plus two or three modules

In this order.

1. Exact start and end time in 30-minute steps, flexible duration, price prorated to the half hour at the same rate from `assumptions.json`, and the kaki availability grid re-cut to match. Asked from three directions. (M-VISITS, M-USERS, `assumptions.json`)
2. Kaki profile photo shown to the caregiver on the assigned visit, plus a 4-digit kaki-side code, so identity is checked in both directions. Photos stored on the box; fine at pilot scale. (M-USERS, M-VISITS)
3. Gender preference on the request, gender on the kaki profile, matching sorts on it and never filters. (M-VISITS, M-USERS, M-ADMIN)
4. "Request the same kaki again": a preferred-kaki field that matching sorts to the top. Homage's continuity feature; cheap given availability sorting already exists. (M-VISITS, M-ADMIN)
5. Per-service data minimisation on the kaki's visit view: household help sees name, address and task; chaperone and companionship see the care plan. (M-VISITS, M-CARE)
6. Cancellation after accept and after start, by either side, with reason and who-cancelled recorded. The compensation rule stays policy and out of scope. (M-VISITS)
7. Certificate upload on the kaki profile, visible on the coordinator approval tab. Committed to Vanguard on Aug 3; gates supply. (M-USERS, M-ADMIN)

## Bucket 3 — defer, or decide something first

- Mandarin UI, then Malay. The biggest single ask from the seniors; deferred by decision on 2026-09-04, not by difficulty. (M-CORE)
- Gross and net cost with the rule shown, and an opt-out toggle. Needs the subsidy test from Vanguard and NCSS first. (M-VISITS, `assumptions.json`)
- Dual-role accounts (caregiver and kaki) with admin restricted to work email. Touches auth. (M-AUTH, M-USERS)
- Live-updating screens via polling; real push later. (M-CORE)
- Live location tracking during chaperone. Privacy review first, and a real-time channel the stack doesn't have.
- SOS / late-night requests. Someone has to answer at 2am; an operating commitment, not a feature.
- Multiple authorised users per household; an "owner" role above admin. A permissions-model rebuild.
- Specialisation-based matching (toileting, mobility). Depends on the certification module existing first.
- Calendar sync (ICS export is easy; keeping it in sync is not). iOS web push. Singpass identity.
- A rating filter in matching: rejected. Stays out.

## How this gets built

Per feature: name the module, write the failing Playwright assertion, implement, extend
`smoke.py`, run both suites, fix until green, restart the server and rerun the lifecycle
once (the second-boot check), commit. Nothing moves to the next feature while anything is
red. Every schema change is `ADD COLUMN IF NOT EXISTS` followed by `CHECKPOINT`, because
of [[kakis-app|the crash that only appeared on the second boot]]. When both buckets are
green, the same eight seniors get the changed app — round 2 — and this time it runs the
crisis triggers.

*Connects to:* [[tabletop-2026-08-21-feedback]] · [[ncss-app-review-2026-08-18]] ·
[[kakis-app]] · [[kakis-build-plan]] · [[../journal/2026-08-21-tabletop-vanguard-ncss]] ·
[[../landscape/luce-sg]]
