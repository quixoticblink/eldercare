---
title: Knowledge base
status: live
last_updated: 2026-05-19
---

This is the working wiki for our eldercare sprint. It's a notebook, not a polished document — capture first, refactor later. The microsite in `../site/` is the public-facing version; this folder is where the thinking actually happens.

## The folders

- `problem/` — observations about elderly people, demographics, what's hard, what's known. One topic per file. Outside-in framing only — no solutioning here.
- `humans/` — empathy maps + raw notes from actual conversations. One person/persona per empathy map; one date per conversation note.
- `reframing/` — How Might We iterations + devil's advocate. The framing-evolution record. [[reframing/hmw-current]] is the current HMW.
- `evidence/` — receipts. Stats with sources, instrument notes (UCLA-3, de Jong Gierveld), annotated citations.
- `landscape/` — existing solutions, prior art, postmortems of things that failed (Memory Lane, Oak Care, NCSS GrabCare, etc.).
- `journal/` — daily running log. The arc of the sprint, session by session.
- `strategy/` — strategy work. Empty until roughly September 2026.
- `prototype/` — prototype work. Empty until roughly September 2026.
- `pitch/` — pitch and narrative work. Empty until close to Demo Day.

Plus [[eldercare]] at the top of this folder — the problem-space overview, the starting point for anyone new to the wiki.

## The capture rule

When you encounter something interesting — a conversation, a stat, a counterargument, a new framing — write the smallest entry that makes sense. Drop it in the right folder. kebab-case filename. YAML front matter. Link to anything adjacent with `[[double-bracket links]]`. Three minutes total. Done.

The worst outcome is not "messy wiki" — it's "the observation never got written down because formatting it felt heavy."

## Naming

- kebab-case filenames. `elderly-loneliness.md`, not `Elderly_Loneliness.md`.
- Dated entries (conversation notes, journal, HMW iterations): `YYYY-MM-DD-<slug>.md` or just `YYYY-MM-DD.md` for the daily journal.
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

| Rubric line (25 pts each) | Wiki folder that feeds it |
|---|---|
| Leadership Journey — evidence of learning over 6 months | `journal/` |
| Quality of Thinking — evidence-backed analysis | `problem/` + `evidence/` + `landscape/` |
| MVP / Prototype — human centricity | `humans/` + later `prototype/` |
| Presentation & Influence | later `pitch/` |

This is why `journal/` matters even though it feels like the most boring folder. You can't reconstruct six months of journey from the prototype alone.

The four sprint learning outcomes — diagnose complex problems, translate insight to strategy, mobilise through narratives, high-performance teamwork — sit on top of the same folders. The wiki is the substrate; outcomes are what the substrate produces.
