---
title: Knowledge base
status: live
last_updated: 2026-07-11
---

This is the working wiki for our eldercare sprint. It's a notebook, not a polished document — capture first, refactor later. The microsite in `../site/` is the public-facing version; this folder is where the thinking actually happens.

## Start here

Three files, in order, if you're landing cold:

1. [[purpose]] — why this sprint exists and where the thinking sits right now. The snapshot section at the top is kept current.
2. [[eldercare]] — the problem-space overview. What eldercare really is, why now, the four functions, the Singapore funnel.
3. [[reframing/hmw-current]] — the current How Might We. As of Jul 8: caregivers activating trusted respite in a crisis, layered onto Vanguard's Pasir Ris ICCP pilot.

If you want to see how the framing got here rather than just where it landed, [[reframing/README]] indexes the four dated iterations (May 19 → Jun 15 signal → Jun 25 caregiver reframe → Jul 8 post-Vanguard narrowing) with a one-line "what changed" note each.

## Where we are

Past the first HMW reframe (Jun 25) and a partner-anchored narrowing (Jul 8). Phase: **build shipped, tabletop next**. Vanguard is the anchor partner as of Jul 8 — a Pasir Ris ICCP-layered pilot offered by year-end. Devil's advocate is active on all three of the recent moves.

**As of Aug 9:** the prototype is a running app — [[prototype/kakis-app]], live at **https://singaporekakis.com**, three roles, real sign-in codes to real phones. On Aug 3 [[journal/2026-08-03-ncss-vanguard|NCSS and Vanguard]] steered the August milestone away from a launch and towards a **tabletop exercise with a limited user set**, which is the first instrument that puts the product in front of the demand side rather than another partner. Demo Day September.

## The folders

Content folders — substantive claims about the problem, our thinking, and our work:

- `problem/` — observations about elderly people, demographics, what's hard, what's known. One topic per file. Outside-in framing only — no solutioning here.
- `humans/` — empathy maps + raw notes from actual conversations. One person/persona per empathy map; one date per conversation note. Also holds the SGLN Google Form interview-responses PDF.
- `reframing/` — How Might We iterations + devil's advocate. The framing-evolution record. [[reframing/hmw-current]] always points at the current HMW; the four dated iterations sit alongside it.
- `evidence/` — receipts. Stats with sources, instrument notes (UCLA-3, de Jong Gierveld), annotated citations, and operational data from partner conversations (NCSS IDIs, Vanguard operational data, Marsiling AAC interviews, Grab market sizing). Primary source documents in `evidence/sources/`.
- `landscape/` — existing solutions, partners, competitors, prior art. Vanguard (our anchor partner), NCSS, AIC, Care Corner, the ICCP model, Lee Ah Mooi, LUCE, Snabbit, Urban Company, community-chaperone, SUSS-GIF-2026, plus the singapore-care-taxonomy overview that ties them together.
- `journal/` — daily running log. The arc of the sprint, session by session.
- `strategy/` — strategic decisions and frameworks (activated 2026-06-25). The respite-marketplace concept, the matching-control × management-depth 2×2, consistency as a load-bearing design constraint.
- `prototype/` — prototype work. Wakes up before the 2026-08-20 SGLN milestone.
- `pitch/` — pitch and narrative work. Wakes up close to Demo Day.

Meta folders — the connective tissue and supporting material:

- `maps/` — the atlas. Chronological views, actor relationships, HMW evolution, rubric alignment, dangling-link registry. Start here if you want to understand how the individual entries fit together. See [[maps/README]].
- `images/` — field-visit photos, indexed and cross-linked to interview notes and landscape entries.
- `artifacts/` — pptx decks checked in as source-of-record: Journey Documentation, SGLN Team Empathy Map, Solutioning Brainstorming (2026-06-25).

At the top of this folder:
- [[eldercare]] — the problem-space overview.
- [[purpose]] — project orientation, folded in from the former top-level `purpose/` folder on 2026-07-11.
- [[VOICE]] — the style guide for writing new entries.

## The capture rule

When you encounter something interesting — a conversation, a stat, a counterargument, a new framing — write the smallest entry that makes sense. Drop it in the right folder. kebab-case filename. YAML front matter. Link to anything adjacent with `[[double-bracket links]]`. Three minutes total. Done.

The worst outcome is not "messy wiki" — it's "the observation never got written down because formatting it felt heavy."

## Naming

- kebab-case filenames. `elderly-loneliness.md`, not `Elderly_Loneliness.md`.
- Dated entries (conversation notes, journal, HMW iterations): `YYYY-MM-DD-<slug>.md`, or just `YYYY-MM-DD.md` for the daily journal.
- Templates: `<thing>-template.md`.

## Front matter

Every entry starts with:

```yaml
---
title: <human-readable title>
status: stub | draft | solid
last_updated: YYYY-MM-DD
---
```

Add other keys (`aliases`, `prereqs`, `owner`, `based_on`, `participants`) as useful.

## Rubric mapping — why each folder exists

We get graded on four dimensions at Demo Day. Each one is fed by specific parts of this wiki:

| Rubric line (25 pts each) | Wiki folders that feed it |
|---|---|
| Leadership Journey — evidence of learning over 6 months | `journal/`, `reframing/` |
| Quality of Thinking — evidence-backed analysis and strategy | `problem/` + `evidence/` + `landscape/` + `strategy/` |
| MVP / Prototype — human centricity | `humans/` + `strategy/` + later `prototype/` |
| Presentation & Influence | later `pitch/` |

This is why `journal/` and `reframing/` matter even though they feel like the most process-oriented folders — you can't reconstruct six months of journey from the prototype alone, and the HMW evolution is itself evidence of learning. `strategy/` now sits under both Quality of Thinking (the analytic frameworks) and MVP / Prototype (the design constraints the prototype has to satisfy) — it started earning its double-listing on Jun 25.

The four sprint learning outcomes — diagnose complex problems, translate insight to strategy, mobilise through narratives, high-performance teamwork — sit on top of the same folders. The wiki is the substrate; outcomes are what the substrate produces.

## What changed on 2026-07-11

- `strategy/` un-dormanted in the rubric mapping (feeds both Quality of Thinking and MVP / Prototype now).
- Landscape list refreshed to match what's actually in `landscape/` (Vanguard, NCSS, AIC, Care Corner, ICCP, Lee Ah Mooi, LUCE, Snabbit, Urban Company, community-chaperone, SUSS-GIF-2026, singapore-care-taxonomy).
- New "Start here" and "Where we are" sections for cold readers.
- Frontmatter `last_updated` bumped from 2026-05-19.
- `purpose.md` fold-in from the former top-level `purpose/` folder (Jul 11) noted in the file list.
