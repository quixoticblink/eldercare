---
title: "Beta testing session at Lions Befrienders — 2026-09-11"
date: 2026-09-11
attendees: [SGLN team; Lions Befrienders seniors and staff]
medium: in-person beta session on the live app, participants' own phones
status: draft
last_updated: 2026-09-20
source: "Post-session notes (docx, received 2026-09-20); more feedback being added in batches"
---

> **Draft.** Written from the notes as received on 20 Sept, nine days after the session,
> with more feedback still to come. Attendee names, numbers and the exact format of the
> session are not in the notes yet. Batch 2 (Lara's photos) shows the 中文 button on
> screen, so the group was on **v1.7**. The recommendation register, with every item mapped
> to what the app already does as of v1.7, is
> [[../prototype/lions-befrienders-2026-09-11-feedback]].

The second group of seniors to try the live app, and the first outside the Care Corner /
Vanguard / NCSS circle: Lions Befrienders, a befriending service for seniors living
alone, six days after v1.6 and v1.7 went out. Same shape as [[2026-08-21-tabletop-vanguard-ncss|Aug 21]]:
own phones, the real address, sign-up through to a visit.

## The arc of the session

- Getting online first, again. Some needed help with wifi; "browser" meant nothing, "go
  to Google and type singaporekakis.com" did. The name landed.
- Sign-up went through; the wait for approval was still the moment people didn't know
  what to do.
- Booking: exact times, which fields matter, a female or male kaki, and whether a third
  hour is prorated all came up. So did the free-text box: *if I ask for the curtains to
  be changed, will the kaki bring a ladder?*
- The wait after booking: how long, and having to refresh to find out.
- The door: the kaki's photo, and the code exchange, new but fine once explained. One
  caregiver wanted to check an NRIC.
- Money and liability: subsidy by means, the right to decline it, a kaki who wants to
  volunteer for nothing, who pays when a caregiver cancels as the kaki arrives.
- Two quotes worth keeping: *"I need help, because I live alone, and I'm not sure when
  something might happen"*, which is the HMW in one sentence; and *"two of them came over
  to play rummy-o"*, a senior who had already used something like this the week before.

## What we learned

- **Batch 1 is the Aug 21 list; batch 2 is the real session.** The docx repeats the Aug 21
  sheet line for line. Lara's photos and Abhishek's four points are new and specific, and
  they are what this session should be remembered for.
- **A kaki was matched to work she did not sign up for.** Carol Wong offered Chaperone
  and Companionship; her phone got "Household help for Madam G, today". The roster shows
  the mismatch to the coordinator but nothing stops the assignment. The fix is small
  (an alert and an explicit confirm on manual assign; a hard requirement in auto-match)
  and it is the first real correctness bug a tester has found since Aug 21.
- **Her phone called us a scam.** The sign-in SMS came from a sender iOS labels
  "Likely-SCAM". Nothing in the app can fix that; the sender ID has to be registered
  before seniors use the app without one of us in the room.
- **Availability reads as two forms.** The profile card and the availability screen are
  one thing with two doors; testers thought they were being asked twice, and "Am I
  working?" under Days off made it worse.
- **If the list is real, the build is invisible.** Fourteen of the twenty-six items were
  shipped in v1.6 (exact times, prorating, gender, photo, same kaki again, cancel after the
  code, the waiting-screen line, no placeholder number, Cantonese, hours on the kaki's
  message, "you don't need to keep the app open"). If a fresh group asked for all of them
  again on v1.7, the fixes are not being noticed, and the next session needs a facilitator
  walking each one.
- **What is new either way:** a uniformed sit-with-a-couple service the seniors could not
  name (worth finding for `landscape/`), and the NRIC ask put more sharply than before.
  "Caregiver" as a word came up again, and now has a Chinese twin (照顾者) to test.
- **The policy questions have not moved since Aug 3.** Subsidy rule, volunteering,
  compensation on a late cancel, liability. Three sessions, same four questions, no owner.

## What changed

- [[../prototype/lions-befrienders-2026-09-11-feedback]] created: every item as received,
  cross-referenced to the Aug 21 register, with status as of v1.7.
- [[../maps/timeline]], [[README]] and [[../README]] carry the session.
- Six photos in `images/2026-09-11-lb-*`, the video in `evidence/sources/`.
- No app change yet. Five small items (service-match alert, availability copy and
  layout, gender chip, task wording, sender ID) are a v1.8 candidate.

## What's next

- Confirm with whoever wrote the docx whether it is their own notes or the Aug 21 sheet.
- Append the remaining feedback batches to the register as they arrive.
- v1.8: block or confirm a service mismatch on assign; one availability entry point;
  two gender chips; warmer task notes; register the SMS sender ID.
- Name the uniformed companion service and add it to `landscape/`.

*Connects to:* [[2026-08-21-tabletop-vanguard-ncss]] · [[2026-09-05-v1.7-language]] ·
[[../prototype/lions-befrienders-2026-09-11-feedback]] · [[../prototype/roadmap]]
