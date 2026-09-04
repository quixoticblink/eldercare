---
title: "Table Top Exercise, round 1 — the recommendation register"
status: solid
last_updated: 2026-09-04
based_on: [journal/2026-08-21-tabletop-vanguard-ncss]
source: "Facilitators' consolidated feedback (Vanguard/NCSS), auto-generated meeting summary, team raw notes"
---

Every recommendation, question and observation from the [[../journal/2026-08-21-tabletop-vanguard-ncss|Aug 21 Table Top Exercise]],
deduplicated across the three post-session documents and mapped to the module in
`app/SPEC.md` that would own the change. The point of the mapping is Prompt 15 in the root
README: *name the module before you write any code.* Where the same ask appeared in more than
one source I've merged it and kept the sharpest phrasing.

Two columns need explaining. **Status** is my read of the app as of v1.5, not a promise:
*new* means nothing exists, *partial* means something adjacent exists, *exists* means the
session found a discoverability problem rather than a missing feature, *policy* means it's a
rule Vanguard/NCSS have to set before anyone codes it. **Priority** follows the facilitators'
own high/medium split where they gave one, and my judgement where they didn't; treat it as a
first sort, not a decision.

## 1. Getting in — connectivity, onboarding, roles

| # | Recommendation | Source | Module | Status | Priority |
|---|---|---|---|---|---|
| 1.1 | Some participants could not get onto wifi or mobile data without help. The session needs a connectivity step before anything else, and the pilot needs a printed one-pager. | team notes | out of app (ops) | policy | high |
| 1.2 | "Open Chrome / a browser" is not understood. The instruction that worked was *go to Google and type singaporekakis.com*. Write the onboarding card in exactly those words. | team notes | out of app (ops) | policy | high |
| 1.3 | The name singaporekakis.com landed well. Keep it (the Kampung Kakis collision in [[kakis-app]] still stands). | team notes | — | — | note |
| 1.4 | After sign-up, participants did not know what to do while waiting for approval. The waiting screen needs to say, in one line, *nothing — we will message you when you're approved*. | team notes | M-USERS | exists, copy fix | high |
| 1.5 | Allow one person to sign up as **both** kaki and caregiver. Several wanted to. | team notes | M-USERS, M-AUTH | new | medium |
| 1.6 | The label *caregiver* is confusing to seniors booking for themselves. Consider a plainer word or a "for myself / for someone I care for" fork. | team notes | M-USERS, M-CORE | new | medium |
| 1.7 | The greyed placeholder number in the phone field read as a real value. One participant kept trying to delete it. Replace with a label above the field or an empty box. | team notes | M-AUTH (frontend) | fix | high |
| 1.8 | Kakis were unsure whether the app must stay open to receive assignments. Answer it on the kaki home screen and send a real notification (see 4.1). | team notes | M-VISITS, M-HELP | partial (SMS/email on assignment exists) | high |
| 1.9 | Multiple authorised users on one account — family members booking and coordinating for a senior. | facilitators | M-USERS, M-CARE | new | medium |
| 1.10 | Multiple recipients at the same address sign up separately; show the right context on each. | auto-summary | M-CARE | new | low |

## 2. Language

| # | Recommendation | Source | Module | Status | Priority |
|---|---|---|---|---|---|
| 2.1 | Mandarin UI. Participants understood English and were still more comfortable in Mandarin. | facilitators | M-CORE (i18n) | new | high |
| 2.2 | Malay UI. | facilitators | M-CORE (i18n) | new | medium |
| 2.3 | Cantonese as a **kaki language option** (spoken, not UI). | team notes | M-CORE constants, M-USERS | partial (language list exists) | medium |
| 2.4 | Caregiver can specify the language the kaki must speak, and matching uses it. | facilitators, auto-summary | M-VISITS, M-ADMIN | partial (visit has a language field; check it sorts) | high |

## 3. Booking

| # | Recommendation | Source | Module | Status | Priority |
|---|---|---|---|---|---|
| 3.1 | Exact start and end time on a request, not just a half-day window. | team notes | M-VISITS | partial (`time_window`) | high |
| 3.2 | Flexible duration — 1-hour blocks, 1–4 hours or custom, not a fixed two-hour minimum. And say whether a third hour is prorated. | all three | M-VISITS, `assumptions.json` | new + policy | high |
| 3.3 | Mark which fields are required and which are optional. Participants didn't know what to fill in. | team notes | M-VISITS (frontend) | fix | high |
| 3.4 | Caregiver can state a **gender preference** for the kaki ("may not want a man to visit"). Add to the request and to matching. | all three | M-VISITS, M-USERS (kaki profile), M-ADMIN | new | high |
| 3.5 | Service specialisations on a request — mobility assistance, toileting, market run — so only qualified kakis are matched. | auto-summary | M-VISITS, M-USERS, M-ADMIN | partial (services list exists, no sub-skills) | medium |
| 3.6 | Does the free-text field feed matching? *If I want the curtains changed, will the kaki bring a ladder?* Either make free text visible to the kaki before accept, or say what it's for. | team notes | M-VISITS | exists (visible to kaki?) — verify | medium |
| 3.7 | Request the same kaki again; give caregivers a choice of kaki. | team notes | M-VISITS, M-ADMIN | new | medium |
| 3.8 | Sync booked visits to the caregiver's or senior's phone calendar. | facilitators | M-VISITS (ICS export) | new | low |
| 3.9 | Late-night / SOS request path; the auto-summary describes a press-and-hold SOS button. | team notes, auto-summary | M-VISITS or new module | new + policy (who answers at 2am?) | medium |
| 3.10 | Pilot geography: restrict matches to a tight local area so response is fast. | auto-summary | M-ADMIN (matching) | partial (`area` on kaki profile) | medium |

## 4. Notifications and the wait

| # | Recommendation | Source | Module | Status | Priority |
|---|---|---|---|---|---|
| 4.1 | Real-time notification when a match is made. Caregivers had no idea how long it would take and kept refreshing. Push, pop-up, or at minimum a live-updating screen. | team notes, facilitators | M-VISITS, M-CORE | partial (SMS/email on assignment; no in-app refresh) | high |
| 4.2 | Show the expected time-to-match on the confirmation screen. | team notes | M-VISITS | new | high |
| 4.3 | Arrival reminder — kaki en route, ETA, about to arrive. | all three | M-VISITS | new | high |
| 4.4 | The assignment notification to a kaki must state the **hours** and a clear task description (companionship vs household vs transport). | all three | M-VISITS (notify) | partial | high |
| 4.5 | Notify a designated next-of-kin or emergency contact when the kaki has checked in and when the visit is complete. | facilitators | M-CARE (contacts), M-VISITS | new | medium |
| 4.6 | Live location tracking during a chaperone visit, ride-hailing style. | facilitators | new module | new | low (heavy; privacy review first) |

## 5. Verification, safety, privacy

| # | Recommendation | Source | Module | Status | Priority |
|---|---|---|---|---|---|
| 5.1 | Show the assigned kaki's **photo** to the caregiver before the visit, from a pre-uploaded profile photo. Both sources raise it; the facilitators propose it as an alternative to the spoken code. | all three | M-USERS (profile), M-VISITS | new | high |
| 5.2 | The start-code exchange was new to everyone and executed without error once explained. Keep it; explain it on the screen where it happens. | team notes | M-VISITS (copy) | exists | medium |
| 5.3 | The kaki sees too much. Age is shown for a household-chores visit; the match view should carry name, address and what the task needs, not the full care plan. This is the hard one — some visits genuinely need the medical detail. | team notes, facilitators (high) | M-VISITS, M-CARE | new (data-minimisation per service) | high |
| 5.4 | Caregivers asked how the platform ensures the kaki who shows up is genuine; one wants to check an NRIC at the door. Decide what identity proof the pilot offers (photo + code, coordinator vouching, Singpass later). | team notes | M-USERS + policy | policy | high |
| 5.5 | Privacy and data concerns generally. Explicit consent text at registration, plain privacy messaging, and a stated deletion path. Pilot data is to be deleted after testing — this was promised in the room. | auto-summary, team notes | M-AUTH (consent), M-ADMIN (deletion), ops | new | high |

## 6. Money

| # | Recommendation | Source | Module | Status | Priority |
|---|---|---|---|---|---|
| 6.1 | How is the subsidy determined — means test, household income, flat type? Nobody could say. Vanguard/NCSS need to set the rule. | all three | policy → `assumptions.json` | policy | high |
| 6.2 | Show both gross and net cost before the caregiver confirms, with the rule that produced it. | facilitators, auto-summary | M-VISITS | partial (illustrative figures shown) | high |
| 6.3 | Option to **decline** the subsidy. | team notes | M-VISITS + policy | new | medium |
| 6.4 | A kaki who wants to volunteer: how to waive the income. | team notes | M-USERS (kaki profile) + policy | new | medium |
| 6.5 | When and how kakis are paid, and a confirmation that payment is guaranteed once a visit is accepted, to reduce no-shows. | auto-summary | M-VISITS, M-HELP | policy + copy | medium |

## 7. Cancellation and liability

| # | Recommendation | Source | Module | Status | Priority |
|---|---|---|---|---|---|
| 7.1 | Cancel after match but before the code exchange. | facilitators | M-VISITS | partial (pre-arrival cancel exists — verify who can trigger it) | high |
| 7.2 | Cancel **after** the code exchange, mid-visit, by either side. | team notes, facilitators | M-VISITS | new | high |
| 7.3 | Who compensates whom when a caregiver cancels just before or after the kaki arrives? Partial refunds mid-service? | team notes, auto-summary | policy → M-VISITS | policy | high |
| 7.4 | Liability in general was discussed with no answer. Ties to the MOU/CA question left open on [[../journal/2026-08-03-ncss-vanguard|Aug 3]]. | team notes | policy | policy | high |

## 8. Coordinator side

| # | Recommendation | Source | Module | Status | Priority |
|---|---|---|---|---|---|
| 8.1 | Abhishek approved users and assigned visits by hand throughout. Automate with configurable rules to reduce admin load. | auto-summary | M-ADMIN | exists (automation toggles, default off) | note |
| 8.2 | Matching filters: proximity, availability, language, gender, specialisation. | auto-summary | M-ADMIN (matching) | partial (availability sorts; others new) | medium |
| 8.3 | The auto-summary also lists *rating* as a matching filter. It stays out. No public ratings is a hard rule (MOH guidance, SPEC 9.5). | auto-summary | — | rejected | — |

## Read with the NCSS review

Three days before this session NCSS desk-reviewed the same app role by role —
[[ncss-app-review-2026-08-18]]. Its register cross-references item numbers here, and it
covers the coordinator console, which no senior touched. Work the two as one list.

## What this list does not contain

Nothing about the crisis triggers. The session ran planned bookings on a Thursday afternoon
at a Care Corner AAC in Toa Payoh; the six triggers from [[../reframing/hmw-2026-07-08-post-vanguard]] were not
exercised, so the app is still untested on exactly the thing the HMW is about. And nothing
about price level — every money question was about the *rules*, none about whether $25/hr
is right, which either means the number is fine or means nobody believed it was real.

*Connects to:* [[../journal/2026-08-21-tabletop-vanguard-ncss]] · [[ncss-app-review-2026-08-18]] · [[kakis-app]] ·
[[kakis-design-brief]] · [[../strategy/respite-marketplace-concept]] ·
[[../reframing/devils-advocate]]
