# Eldercare Sprint

A six-month leadership sprint by five people, asking:

> **How might we help elderly in Singapore experience genuine daily connection, so that Singapore is brimming with elderly communities that are happy, mentally and physically healthy?**

Started May 19, 2026. Singapore. Public journey.

## Two directories

This repo has two top-level folders, each with its own purpose:

```
.
├── knowledge/    ← the working wiki (internal thinking, captured as we go)
└── site/         ← the public microsite (Vercel-deployable, our journey)
```

### `knowledge/` — the wiki

The working notebook. Where observations, HMW iterations, empathy maps, evidence, prior-art landscape, and the daily journal live. Plain markdown, kebab-case filenames, YAML front matter, `[[double-bracket]]` cross-links. Read `knowledge/README.md` for the folder rules and capture rule.

Key entries:

- `knowledge/eldercare.md` — the problem-space overview.
- `knowledge/reframing/hmw-current.md` — the synthesized HMW, with the full reasoning.
- `knowledge/reframing/hmw-2026-05-19-individual-exercise.md` — the six original individual HMWs from May 19.
- `knowledge/journal/2026-05-19.md` — Day 1 journal entry.

### `site/` — the microsite

Static HTML + CSS, Vercel-ready. The public face of the journey. `index.html` is a single-page editorial site with hero, journey timeline, the HMW, team profiles, problem-space summary, and a knowledge-base index. Read `site/README.md` for local preview and deployment.

## Why two folders

The wiki and the microsite optimize for different things:

- The **wiki** optimizes for low-friction capture. Markdown, plain folders, no build step, no styling overhead. We add to it daily. It's the substrate.
- The **site** optimizes for narrative presentation. Editorial layout, restrained typography, a story arc someone can scroll through in two minutes. We update it less often, mostly after big moments.

The site references the wiki via relative links (`../knowledge/...`) so a reader who wants depth can click straight from the public summary into the working notes.

## Deploying

Quickest path to a live site:

1. Push this repo to GitHub.
2. Import to Vercel.
3. In project settings, set **Root Directory** to `site`.
4. Done — homepage is live.

Alternative: drag-and-drop the `site/` folder into Vercel's dashboard. Same result, no Git needed.

If you want the links from the deployed site to resolve into the wiki (`../knowledge/...`), include both folders in the deployment. Two options:

- Deploy the **whole repo** (root directory unset). Vercel will serve `site/index.html` if you add a rewrite, or you'll need to visit `/site/`. Slightly less clean URL but the wiki links work.
- Deploy `site/` as root and use a small script to copy `knowledge/` into `site/knowledge/` at build time. Cleaner URLs, slightly more setup.

For now (May 19) we're keeping it simple — deploy `site/` as root and treat wiki links as repo-internal references. If you want the wiki to be browsable as part of the deployed microsite, raise it in the journal and we'll add a build step.

## The four-part rubric

This is what the sprint will be graded on at Demo Day. Each part is 25 points. The wiki is shaped by it:

| Rubric line | Wiki folder that feeds it |
|---|---|
| Leadership Journey (evidence of learning over 6 months) | `knowledge/journal/` |
| Quality of Thinking (evidence-backed analysis) | `knowledge/problem/` + `knowledge/evidence/` + `knowledge/landscape/` |
| MVP / Prototype (human centricity) | `knowledge/humans/` + later `knowledge/prototype/` |
| Presentation & Influence | later `knowledge/pitch/` |

The site is the substantive showcase of all four — it's literally what the judges will see when we point them at the URL.

## The team

- **Abhishek Kaul** — whose parents in India experience loneliness despite intact social circles.
- **Lara PuReum Yim** — finding new communities for recently-relocated elderly parents.
- **Aditi Agarwal** — carrying the observation that losing a life partner creates an irreplaceable absence.
- **Shobhit Singhal** — whose in-laws from Bangkok feel lonely in Singapore despite physical proximity to family.
- **Zheng Wei** — clinical and research lens on isolation and connection.

## Status

- ✅ Day 1 (May 19, 2026) — problem space, HMW, wiki, microsite.
- ☐ Day 7 (May 26, 2026) — empathy maps + HMW revision.
- ☐ Demo Day — live prototype + pitch.

See `knowledge/journal/` for the running record.
