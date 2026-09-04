---
title: "NCSS reviews the live app, role by role — 2026-08-18"
date: 2026-08-18
attendees: [NCSS staff, reviewing asynchronously; team receiving]
medium: written desk review of singaporekakis.com, one table per role
status: solid
last_updated: 2026-09-04
source: "NCSS Feedback on Singapore Kakis App (.docx)"
---

NCSS took the prototype link we shared after [[2026-08-03-ncss-vanguard|Aug 3]] and did
what we asked for — feedback within days, no template — except that they brought their
own template: three tables, one per role, an observation against every screen. Thirty
items. The full register, mapped to SPEC modules and cross-referenced to what the seniors
said three days later, is [[../prototype/ncss-app-review-2026-08-18]].

## The arc

- They reviewed as the coordinator first, which nobody else has. Six items, all about
  clicks between screens: dashboard counts that should be links, case notes that should
  open profiles, an approval tab that should show certificates.
- Then as a caregiver, screen by screen through booking. The preset time windows, a
  single-select language field that should come from the care plan, a chaperone flow
  with no pick-up point or destination, and one real bug (urgent after 5pm still offers
  2–5pm).
- Then as a kaki: profile photo should be mandatory, the availability grid is hard to
  use, and 8am–6pm working hours have to line up with whatever caregivers can book.
- One item reverses a design decision: they want the kaki to read the start code to the
  caregiver, not the other way round.

## What we learned

The start code proves the wrong thing for NCSS's threat model. We built it to prove a
visit physically happened; they read it as an identity check and pointed out it doesn't
do that. It doesn't. Both directions are needed and the register says how.

A service operator reviews for operating cost. Every coordinator-side item is about
reducing navigation for the person who runs the pilot day to day. That's the Aug 3
"administrative burden" metric arriving as a feature list, and it's fair.

The crisis-trigger question reads as friction from outside. NCSS wants it moved to an
after-service survey. It's there because the HMW counts triggers. Deciding that on purpose
is on the list.

## What changed

- Role separation is now a partner ask, not just our preference: admin by work email
  only, and an owner role above admin. Alongside the seniors wanting dual caregiver-and-kaki
  accounts, the role model needs a rethink before the certification module is built on it.
- The time-window preset is dead. NCSS (30-minute steps), the seniors (exact start and
  end) and the kaki grid (must align) all point the same way.

## What's next

- Fold both registers into one SPEC amendment pass, module by module. The overlap column
  in the NCSS register is there so the same item isn't done twice.
- Fix the after-5pm urgent-window bug now; it's small and it was found by a partner.
- Decide the start-code direction with a test on round 2, not in a doc.

*Connects to:* [[../prototype/ncss-app-review-2026-08-18]] ·
[[2026-08-21-tabletop-vanguard-ncss]] · [[../prototype/tabletop-2026-08-21-feedback]] ·
[[../prototype/kakis-app]] · [[../landscape/ncss]]
