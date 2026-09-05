---
title: "Kakis — what shipped, what's next"
status: live
last_updated: 2026-09-05
based_on: [prototype/feature-buckets-2026-09-04, prototype/tabletop-2026-08-21-feedback, prototype/ncss-app-review-2026-08-18]
---

One page to answer the two questions a partner asks first: *what did you change since we
saw it, and what are you going to change next.* The registers hold the detail; this is the
running summary, updated every release. The version that people can use is always at
**https://singaporekakis.com**.

## Shipped

### v1.7 — 2026-09-05 · 中文 on the caregiver and kaki screens

The biggest single ask from the seniors on Aug 21, built the same day v1.6 went out.
One button at the top of every caregiver and kaki screen switches the whole app
between English and Simplified Chinese — sign-in, the waiting screen, booking, the
door check, the kaki's visit page, profile, availability, the help panel, and the
SMS and email messages a person receives. The choice is remembered on the phone and
on the account, so it is the same next time and on a second phone; a phone already set
to Chinese starts in Chinese. Names, notes, reasons and anything a person types stay
exactly as typed, and every value the app stores stays English underneath. **The
coordinator console stays English by design**: one language across the console, the
audit log and every message subject, whatever the person on the other end chose.

Eight new Playwright specs (a full Chinese lifecycle with a no-English-leak check on
every screen) and 26 smoke assertions. Detail in `app/SPEC.md` §7 and §10;
[[../journal/2026-09-05-v1.7-language]].

### v1.6 — 2026-09-05 · the August feedback round

Eighteen features, all from Buckets 1 and 2 of [[feature-buckets-2026-09-04]], each
behind an end-to-end test. Grouped by what a person would notice:

**At the door.** The kaki now carries a photo and, per visit, a 4-digit code of their
own. The family compares the photo, enters the code, and only then does their own start
code appear to read back. Proof of identity (NCSS's ask) and proof of admission (ours),
in one flow. Both codes lock after five wrong tries.

**Booking.** Planned visits take an exact start and end in 30-minute steps and are
charged by the half hour with a one-hour minimum. Languages come pre-filled from the care
plan, several can be chosen, Cantonese is on the list. A family can ask for a female or
male kaki, or for a kaki who has visited before; both sort the coordinator's roster and
both are respected by auto-match. "Other — tell us" on the trigger step. A same-day window
that has already passed is never offered. Bookings open up to 30 days ahead, a coordinator
setting.

**Around the visit.** The caregiver is messaged when a kaki is matched, confirms, is on
the way, passes the visit back, or cancels, and the visit page says how long matching
usually takes. The kaki's assignment message states the hours and the task. The emergency
contact on the care plan is messaged when the visit starts and ends. Either side can cancel
after accepting or mid-visit, with a reason; the other side and the coordinator are told,
and the coordinator sees every cancellation under Quality.

**Kakis.** Working hours per day instead of a half-day grid. Profile photo. Gender.
Certificates (PDF or photo, up to ten), addable before approval and read by the
coordinator on the approval card. Household-help visits show only what the task needs
— no age, no medications, no private notes. "You don't need to keep the app open."

**Getting in.** No placeholder number in the sign-in box. A waiting screen that says
there is nothing to do. Required and optional fields marked. A refresh keeps you on the
same booking step. Caregivers can edit their own name and number. The coordinator's
dashboard counts are buttons.

Under the hood: the app clock is pinned to Singapore time (the server runs UTC), the
kaki never receives the family's start code on any response (it had, since v1, on four
of them — nobody saw it because no screen showed it), and cancellation reasons are
escaped before they reach an email. Detail and attribution in `app/SPEC.md` §10 and
[[../journal/2026-09-05-v1.6-build]].

### v1.5 and earlier — 2026-07-21 to 2026-08-09

Six build rounds in three weeks: initial build, prototype sync, dual-channel sign-in
(email or mobile), kaki availability and sourced assumptions, assignment notifications
and automation toggles, ISO/IEC 5055 hardening. [[kakis-app]] tells that story.

## Roadmap

Ordered by what has to be decided before it can be built, not by difficulty.

**Round 2 of the Table Top Exercise.** Same eight seniors, the v1.6 app, and this time
the crisis triggers — the one thing the HMW is about that round 1 didn't exercise. Owner:
us, with Care Corner and Vanguard. The open question from round 1 is still open: whether
a Vanguard-side session with ICCP participants is owed as well.

**Malay UI.** Mandarin shipped as v1.7 (above), which reverses the 2026-09-04 decision
to keep language out of round 2. Round 2 now tests v1.6 and the Mandarin screens
together. That is acceptable because the two are separable in the room: the door check,
exact times and cancellation are the same flow in either language, so a senior who
struggles can be switched to English with one tap and the observation is still about
the flow, and a senior who succeeds in Chinese has tested both at once. What is
confounded is only the *onboarding* reading — whether a screen was hard because of the
words or because of the step — and the facilitators note the language each senior used.
Malay is the same dictionary mechanism and waits for a Malay-speaking reviewer.

**Subsidy rules.** Every money question on Aug 21 was about the *rules* — means test,
flat type, can I decline — and none about the price. The app already shows an
illustrative stack with every figure sourced. Showing gross and net before a family
confirms needs Vanguard and NCSS to state the test. Until then every dollar figure keeps
the word *placeholder*.

**Dual-role accounts, and an owner above the coordinator.** Seniors wanted to sign up as
both caregiver and kaki; NCSS wants admin by work email only and a role that can see
what coordinators can't. Both are the same auth change, done once.

**Live updates.** Screens that refresh themselves when something changes, so nobody has
to reload; real push notifications after that (iOS web push has constraints).

**Further out.** Live location during chaperone visits (privacy review first). A
late-night / SOS path — an operating commitment before it is a feature, because someone
has to answer at 2am. Specialisation-based matching once certificates carry the skill.
Calendar sync. Singpass identity.

**Never, by rule.** Public ratings of kakis. Concerns go privately to a human.

## How to read this against the registers

[[tabletop-2026-08-21-feedback]] (the seniors, 43 items) and
[[ncss-app-review-2026-08-18]] (the operator, 30 items) are the source; [[feature-buckets-2026-09-04]]
is the cut into three buckets with the reasoning; this page is the outcome. When a bucket
ships, its items move up here; when a decision unblocks a roadmap line, it moves into the
next bucket.

*Connects to:* [[kakis-app]] · [[feature-buckets-2026-09-04]] · [[plans/v1.6-buckets-1-2]] · [[plans/v1.7-language-switch]] · [[../journal/2026-09-05-v1.7-language]] ·
[[../journal/2026-09-05-v1.6-build]] · [[../journal/2026-08-21-tabletop-vanguard-ncss]]
