---
title: "Kakis — what shipped, what's next"
status: live
last_updated: 2026-09-20
based_on: [prototype/feature-buckets-2026-09-04, prototype/tabletop-2026-08-21-feedback, prototype/ncss-app-review-2026-08-18]
---

One page to answer the two questions a partner asks first: *what did you change since we
saw it, and what are you going to change next.* The registers hold the detail; this is the
running summary, updated every release. The version that people can use is always at
**https://singaporekakis.com**.

## Shipped

### v1.8 — 2026-09-20 · the befrienders' round

Ten small things from the [[../journal/2026-09-11-lions-befrienders-beta|Lions Befrienders session]],
nine days after it. **The bug:** a kaki can no longer be assigned a service she did not
offer without the coordinator reading a warning and saying yes to it, and that yes is
recorded; automatic matching never crosses it. **Urgent visits can be long:** a booking
for now or soon carries how many hours, one to eight, and is priced on them. **The kaki's
message:** the task line reads like a message to a person, and the family's own note
rides along ("The family says: please help change the curtains"). **Plainer screens:**
"Who are you caring for?", "I'm booking for someone I care for", "Kaki arrived", the cost
stack behind a tap, the care plan skippable on day one, the kaki's availability behind
one door with "Different on a date?" instead of "Am I working?", two gender options, no
tier badge, and help questions that match what people asked in the room. All in English
and Chinese. Not code, but on the list: the SMS sender ID has to be registered before
anyone uses this without us there.

*v1.8.1, the same night:* certificates were never required, but the waiting screen
read as if they were. Now "Add a certificate", marked optional, and a "Skip for now"
on the pending kaki's profile, in both languages.

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

Ordered by what has to be decided before it can be built, not by difficulty. Revised
2026-09-20 after the Lions Befrienders session; the two items at the top are new.

**A caregiver is not one senior.** A befriender visits many; a family has two parents
in two flats; a staff member books on behalf of a round. The app has had one household
per caregiver since v1. Pair it with the Aug 21 ask for many caregivers per senior and
it is one change: people and households as a many-to-many relationship, with a
"booking for whom?" step. Touches M-CARE, M-VISITS, M-ADMIN. Decide the shape first.

**What each side sees of the other.** "Do not reveal full name. No phone number.
Seniors call out of the blue, hound you forever." First name and initial, calls routed
through the coordinator or a masked number, while the photo and the two codes at the
door stay. A PDPA question as much as a design one; decide before the pilot, with
NCSS in the room.

**A mid-visit danger alert.** Either side presses one button and a human answers now.
Joins the late-night / SOS line below; someone has to be on the other end before the
button exists.

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

**Subsidy rules, opt-out, volunteering, compensation.** Every money question on Aug 21
and again on 11 Sept was about the *rules* — means test, flat type, can I decline, can I
volunteer for nothing, who pays when a caregiver cancels as the kaki arrives — and none
about the price. The app already shows an
illustrative stack with every figure sourced. Showing gross and net before a family
confirms needs Vanguard and NCSS to state the test. Until then every dollar figure keeps
the word *placeholder*.

**Dual-role accounts, and an owner above the coordinator.** Asked for a third time on
11 Sept. Seniors and befrienders want to sign up as both caregiver and kaki; NCSS wants
admin by work email only and a role that can see what coordinators can't. Both are the
same auth change, done once.

**Repeat and series bookings.** Several visits in one go. Small on the screen, a
matching and pricing question underneath.

**Free-text services and reimbursement.** "Change the curtains" is not one of the four
services; whether a kaki is qualified is a matching problem, and it sits with
specialisation-based matching below. A kaki who pays for the taxi first needs a way to
be paid back: a policy (who approves, what cap) before a field on the report.

**Live updates.** Screens that refresh themselves when something changes, so nobody has
to reload; real push notifications after that (iOS web push has constraints).

**Further out.** Live location during chaperone visits (privacy review first). A
late-night / SOS path — an operating commitment before it is a feature, because someone
has to answer at 2am. Specialisation-based matching once certificates carry the skill.
Calendar sync. Singpass identity and the PDPA package (consent text, deletion path);
the befrienders' privacy warning moves these up. Malay UI, when there is a Malay-speaking
reviewer.

**Never, by rule.** Public ratings of kakis. Concerns go privately to a human.

## How to read this against the registers

[[tabletop-2026-08-21-feedback]] (the seniors, 43 items) and
[[ncss-app-review-2026-08-18]] (the operator, 30 items) are the source; [[feature-buckets-2026-09-04]]
is the cut into three buckets with the reasoning; this page is the outcome. When a bucket
ships, its items move up here; when a decision unblocks a roadmap line, it moves into the
next bucket.

*Connects to:* [[kakis-app]] · [[feature-buckets-2026-09-04]] · [[lions-befrienders-2026-09-11-feedback]] · [[plans/v1.6-buckets-1-2]] · [[plans/v1.7-language-switch]] · [[plans/v1.8-befrienders-round]] · [[../journal/2026-09-20-v1.8-build]] · [[../journal/2026-09-05-v1.7-language]] ·
[[../journal/2026-09-05-v1.6-build]] · [[../journal/2026-08-21-tabletop-vanguard-ncss]]
