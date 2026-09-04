---
title: "NCSS desk review of the app — the recommendation register — 2026-08-18"
date: 2026-08-18
status: solid
last_updated: 2026-09-04
source: "NCSS Feedback on Singapore Kakis App (.docx), a role-by-role walkthrough of the live app"
---

Three days before the [[../journal/2026-08-21-tabletop-vanguard-ncss|Table Top Exercise]],
NCSS staff sat down with the live app and went through it role by role — coordinator
("Admin"), caregiver, kaki — screen by screen, writing an observation against each area.
This is a different kind of evidence from the Aug 21 session. The seniors told us where
the product is hard to *reach*; NCSS told us where the product is *wrong*, from the point
of view of an organisation that runs services like this and will have to operate ours.

The register below keeps NCSS's own order and wording where it was already sharp, mapped
to the `app/SPEC.md` module that would own each change, with the same status vocabulary
as [[tabletop-2026-08-21-feedback]] (*new*, *partial*, *exists*, *fix*, *policy*). Where
an item also came up on Aug 21 the cross-reference is in the last column, so the two
registers can be worked as one list.

## The one that changes a design decision

Everything else here is a refinement. This one isn't:

> *"Caregiver should not be reading the code to Kaki. Kaki should read the code to the
> caregiver as a match for verification. This will prevent strangers from impersonating
> a kaki."*

The app's one-way start code was built to prove the opposite thing. The caregiver's screen
shows the code and the kaki enters it, so the record says *someone was at the door and the
family let them in* — it proves admission, not identity. NCSS's version proves identity —
*the person at the door is the one the app assigned* — and doesn't prove admission. Both
are impersonation defences pointing in different directions, and the Aug 21 participants
asked for the NCSS direction too (kaki photo, NRIC at the door). The honest answer is
probably both halves: the kaki shows something only the assigned kaki could have (a photo
and a code on their screen), then the caregiver's code is entered to start. That's a
two-step, and it's slower, and it should be tested on the second round before anyone
decides. See 2.9 below and 5.1, 5.4 in the Aug 21 register.

## 1. Coordinator ("Admin")

| # | Observation | Module | Status | Aug 21 ref |
|---|---|---|---|---|
| 1.1 | Can one user be admin, caregiver and kaki at once? NCSS suggests **admin only by work email** so admin and user roles can't overlap, and a further **owner** role that restricts what admins can see (e.g. case notes). | M-AUTH, M-USERS | new (roles are single today; `ADMIN_EMAILS` is the only admin gate) | 1.5 |
| 1.2 | A visible **settings** page, including notification preferences. | M-CORE (settings), M-USERS | partial (automation toggles exist; no notification prefs) | — |
| 1.3 | Dashboard indicators (e.g. *users awaiting approval*) should link straight to the actionable list. | M-ADMIN (frontend) | fix | — |
| 1.4 | From a case note, clickable access to both the caregiver's and the kaki's details without crossing screens. | M-ADMIN, M-CARE | fix | — |
| 1.5 | On the approval tab, contact details, profile and **certificates or supporting documents** directly accessible. | M-ADMIN, M-USERS | partial (no document upload yet — this is the certification-tracking module promised on Aug 3) | — |
| 1.6 | On the matching tab, manual changes should link to the user's profile, so a cancellation or a change of kaki is easy. | M-ADMIN (frontend) | fix | 7.1 |

## 2. Caregiver

| # | Observation | Module | Status | Aug 21 ref |
|---|---|---|---|---|
| 2.1 | Let users edit their **profile**, not only the care plan. | M-USERS | fix | — |
| 2.2 | Make the **profile picture mandatory** so the kaki can identify the care recipient. | M-USERS | new | 5.1 (mirror image) |
| 2.3 | Address: exact address or region? *"Clementi"* was accepted. Decide the required level of detail and validate it. | M-CARE | fix + policy | 3.10 |
| 2.4 | Users may need to **switch between caregiver and kaki**. | M-AUTH, M-USERS | new | 1.5 |
| 2.5 | "Book a visit" on the home tab duplicates the booking tab. Keep one. | M-CORE (frontend) | fix | — |
| 2.6 | Move the **care plan to the top** of the page. Add **bedridden** to mobility (currently independent / stick / frame / wheelchair). Split emergency contact into name, relationship, number. | M-CARE | fix | — |
| 2.7 | Add **additional care recipients** under one caregiver. | M-CARE | new | 1.9, 1.10 |
| 2.8 | **Reverse the start code**: kaki reads it to the caregiver. See the section above. | M-VISITS | design decision | 5.1, 5.2, 5.4 |
| 2.9 | A wait-time / ETA estimate from the distance between caregiver and kaki. | M-VISITS, M-ADMIN | new | 4.3 |
| 2.10 | Back navigation in the booking flow is awkward; a refresh drops you to step 1. | M-VISITS (frontend) | fix | — |
| 2.11 | Chaperone: status updates to the caregiver on reaching the location or clinic. | M-VISITS | new | 4.3, 4.5 |
| 2.12 | Chaperone: specify the **type** — medical appointment vs non-medical errand (groceries, shopping, haircut). | M-VISITS, `assumptions.json` services | new | 3.5 |
| 2.13 | Companion: capture **hobbies and interests** (in the care plan or profile) so matching can use them. | M-CARE, M-ADMIN | new | — |
| 2.14 | **Wellness check**: is it a specialised service, and how does it differ from companionship? Define or merge. | `assumptions.json` services + policy | policy | — |
| 2.15 | "Planned, book ahead": set a **maximum advance-booking horizon** for the pilot, to manage availability. | M-VISITS + policy | new + policy | — |
| 2.16 | Time window: replace the three preset windows (9–12, 2–5, 5–8) with a **specific start and end in 30-minute steps**. | M-VISITS, M-USERS (availability must align) | new | 3.1, 3.2 |
| 2.17 | Bug: an **urgent** request after 5pm still shows the 2–5pm window. | M-VISITS | fix | — |
| 2.18 | "Language with them": why single-select? And pull the recipient's language from the care plan instead of asking again. | M-VISITS, M-CARE | fix | 2.3, 2.4 |
| 2.19 | Chaperone is missing the **meeting / pick-up location**, the **destination**, and whether it's **one-way or return**. | M-VISITS | new | — |
| 2.20 | "What happened" (crisis trigger step): add **"Others, please specify"**; and since it doesn't affect the booking, move it to an after-service survey to shorten the flow. | M-VISITS | fix + design question (the trigger is our evidence line for the HMW — moving it after the visit changes what we can learn) | — |

## 3. Kaki

| # | Observation | Module | Status | Aug 21 ref |
|---|---|---|---|---|
| 3.1 | Make the **profile picture mandatory** so caregivers can identify the kaki. | M-USERS | new | 5.1 |
| 3.2 | Working hours show 8am–6pm. Pilot-only or standard? Either way, **align with the windows caregivers can book**. | M-USERS (availability), M-VISITS | fix + policy | 2.16 above |
| 3.3 | "Add a date": clarify what *extra availability* means — hours outside the usual schedule, or one-off dates. | M-USERS (copy) | fix | — |
| 3.4 | The weekly availability **grid is hard to use**. Replace with a simple day-and-time input. | M-USERS (frontend) | fix | — |

## What to take from it

Three things stand out once it's laid next to the Aug 21 register.

First, NCSS reviewed the coordinator role, which no senior did. Six of their items are
about the console, and all six are about *clicks between screens* — the operator cost of
running this thing. That is the "lessen your administrative burden" metric from
[[../journal/2026-08-03-ncss-vanguard|Aug 3]] showing up as concrete UI asks.

Second, the time-window preset is now hit from three directions: NCSS wants 30-minute
granularity, the seniors wanted exact start and end times, and the kaki availability grid
has to match whatever the answer is. This is one change across M-VISITS and M-USERS, not
three.

Third, item 2.20 is a quiet conflict with the HMW. The crisis trigger question exists
because the July 8 framing named six triggers and we wanted to count them. NCSS reads it
as friction in the booking flow, which it is. If it moves to an after-service survey, we
still get the data, later and with lower completion. Worth deciding on purpose rather than
by default.

*Connects to:* [[tabletop-2026-08-21-feedback]] ·
[[../journal/2026-08-21-tabletop-vanguard-ncss]] · [[kakis-app]] ·
[[../journal/2026-08-03-ncss-vanguard]] · [[../landscape/ncss]] ·
[[../reframing/hmw-2026-07-08-post-vanguard]]
