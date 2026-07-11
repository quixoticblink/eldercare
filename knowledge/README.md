---
title: Knowledge base
status: live
last_updated: 2026-05-19
---

This is the working wiki for our eldercare sprint. It's a notebook, not a polished document — capture first, refactor later. The microsite in `../site/` is the public-facing version; this folder is where the thinking actually happens.

## The folders

Content folders — substantive claims about the problem, our thinking, and our work:

- `problem/` — observations about elderly people, demographics, what's hard, what's known. One topic per file. Outside-in framing only — no solutioning here.
- `humans/` — empathy maps + raw notes from actual conversations. One person/persona per empathy map; one date per conversation note. Also holds the SGLN Google Form interview-responses PDF.
- `reframing/` — How Might We iterations + devil's advocate. The framing-evolution record. [[reframing/hmw-current]] links to the current HMW ([[reframing/hmw-2026-07-08-post-vanguard]]).
- `evidence/` — receipts. Stats with sources, instrument notes (UCLA-3, de Jong Gierveld), annotated citations. Primary source documents in `evidence/sources/`.
- `landscape/` — existing solutions, partners, competitors, prior art (Vanguard, NCSS, AIC, Luce, Homage, etc.).
- `journal/` — daily running log. The arc of the sprint, session by session.
- `strategy/` — strategic decisions and frameworks (activated 2026-06-25).
- `prototype/` — prototype work. Wakes up before the 2026-08-20 SGLN milestone.
- `pitch/` — pitch and narrative work. Wakes up close to Demo Day.

Meta folders — the connective tissue and supporting material:

- `maps/` — the atlas. Chronological views, actor relationships, HMW evolution, rubric alignment, dangling-link registry. Start here if you want to understand how the individual entries fit together. See [[maps/README]].
- `images/` — field-visit photos, indexed and cross-linked to interview notes and landscape entries.
- `artifacts/` — pptx decks (empathy map deck, journey documentation, solutioning brainstorming) checked in as source-of-record.

Plus at the top of this folder:
- [[eldercare]] — the problem-space overview. Start here for the problem itself.
- [[purpose]] — the project orientation document (folded in from the former top-level `purpose/` folder on 2026-07-11).
- [[VOICE]] — the style guide for writing new entries.

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
