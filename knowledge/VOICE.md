# Knowledge wiki — voice and structure spec

**Purpose.** Hand this file to any future collaborator (human or AI) along with your "please add an entry on X" request. This is what keeps the wiki sounding like itself across many authors and many months.

**How to use this with an AI.** Paste this entire file, then add your specific ask. Example: *"Using VOICE.md, write a new wiki entry on `caregiver-burnout` and place it at `knowledge/problem/caregiver-burnout.md`."* The AI then has the voice rules, reasoning order, and structural conventions in one shot. Existing entries — `knowledge/eldercare.md` and `knowledge/reframing/hmw-current.md` — are the canonical examples of the style; point the AI at them too.

---

## 1. Voice and stance

The wiki is written in the voice of Andrej Karpathy's blog posts and from-scratch lectures: conversational, first-person-ish, technically rigorous but never stiff.

Markers that signal we're in voice:

- Short sentences mixed with longer ones.
- Em-dashes ( — ) for parenthetical asides. Real em-dashes, not double hyphens.
- Phrases like *"ok so,"* *"the punchline is,"* *"the thing that took me a while to see."*
- *"I"* is fine. *"We"* is fine when the team did the thing together.
- Concrete numbers over abstract claims. "30,000 people, roughly the capacity of the National Stadium" beats "many."

Markers we avoid:

- Corporate scaffolding. No *"in this article we will explore…"*, no *"let's dive in,"* no *"stay tuned."*
- Throat-clearing intros. The first sentence should already be doing work.
- Closing summaries. Get in, build the idea, get out — let the *Connects to* section be the closer.
- Bold for emphasis inside prose. Italics for emphasis. Bold only inside tables or genuinely structural callouts.
- Emoji. Anywhere.
- *"Genuinely,"* *"honestly,"* *"straightforward."* The voice doesn't lean on these adverbs.

---

## 2. Reasoning order

Each entry walks the reader through the idea in this order:

1. **Intuition.** What the thing is, why anyone should care. Hook first, definition second.
2. **Toy example.** The smallest concrete version of the idea. Real numbers, a specific case, or a tiny scenario.
3. **General formulation.** Now that the reader has the picture, write the math, the algorithm, or the precise definition. It should feel like compression of something they already understand.
4. **Code or concrete walkthrough.** If the topic admits code, include a minimal from-scratch snippet (20–60 lines, well-commented, no frameworks hiding mechanics). For non-code topics, use a worked example with real numbers, an ASCII diagram, or a thought experiment.
5. **What confused me / common pitfalls.** The honest part. Misleading notation, off-by-one traps, the "wait, why does this work?" moments.
6. **Connects to.** A short prose paragraph (not a list) pointing at 3–6 adjacent entries — existing or proposed — explaining the relationship in one clause each.

Never invoke a term before you've earned it. When you introduce a term, define it inline and say why we need the word.

---

## 3. Show the gears

Whenever the topic admits it, include something concrete a reader can run, trace, or replay in their head.

- **Code topics.** Minimal Python / NumPy / PyTorch preferred, 20–60 lines, no high-level frameworks doing the mechanics for you. Comments narrate the way you'd say it aloud.
- **Non-code topics (this whole eldercare wiki, mostly).** A concrete worked example with real numbers; a hand-traced diagram in ASCII; a tiny thought experiment. The goal is the same — the reader walks through the actual gears, not just an abstract claim.

---

## 4. Honesty

Flag what's confusing. Flag what notation is misleading. Distinguish folklore from proven. Distinguish your opinion from consensus. Say *"I'm not sure"* when you aren't. Say *"I haven't verified this"* when you haven't.

This is non-negotiable — the wiki is more valuable as a record of what we actually know than as a polished surface. A hedged claim with a source is worth more than a confident claim without one.

---

## 5. Anti-formatting bias

Prose carries the argument. Use headings sparingly. Use bullets only for genuine enumerations of 3+ truly parallel items. No bold-everywhere. No emoji. No tables unless tabular data is the point.

If a sentence works as prose, don't break it into bullets to look thorough. If a paragraph works as a paragraph, don't add a heading above it. The default unit of thought is the paragraph.

---

## 6. Entry structure

Each full entry follows this skeleton:

```
---
title: <human-readable title>
aliases: [<other names>]
prereqs: [<entries the reader should grok first>]
status: stub | draft | solid
last_updated: YYYY-MM-DD
---

<One-paragraph opener. Hook first.>

## <Tiny worked example>

<The smallest concrete version of the idea.>

## <General formulation>

<Math, algorithm, or precise definition — written as compression of what they already understand.>

## <Code or concrete walkthrough>

<From-scratch implementation OR worked example with real numbers OR thought experiment.>

## <What confused me / pitfalls>

<Honest. Specific. Cite folklore vs. opinion vs. proven.>

## <Connects to>

<Short prose paragraph pointing at 3–6 adjacent entries — use [[double-bracket]] links even if the entry doesn't exist yet.>

## <Proposed sibling / child entries>

- [[entry-name]] — one-sentence stub describing what the entry would cover.
- [[entry-name]] — one-sentence stub.
- (3–5 of these)
```

Section headings don't have to use the literal labels above (you can name them around the actual content), but the *order* and *intent* should match.

---

## 7. Wiki conventions

**Filenames.** kebab-case. `elderly-loneliness.md`, not `Elderly_Loneliness.md`. Dated entries (conversation notes, daily journal, HMW iterations) use `YYYY-MM-DD-<slug>.md`. Templates use `<thing>-template.md`.

**Front matter.** Every entry starts with a YAML block. Required fields: `title`, `status`, `last_updated`. Optional, add as useful: `aliases`, `prereqs`, `owner`, `based_on`, `participants`, `date`.

**Statuses.**
- `stub` — title and one-paragraph placeholder; entry exists so [[links]] resolve, but content is thin.
- `draft` — substantively written but not yet pressure-tested against the team or new evidence.
- `solid` — written, reviewed, and currently believed.
- `dormant` — folder-level READMEs for sections that wake up later (strategy, prototype, pitch).

**Cross-linking.** Use `[[double-bracket]]` references to other entries by filename-without-extension. Linking to entries that don't exist yet is *encouraged* — dangling links are the wiki's growth plan made visible. The more incoming links a not-yet-existing entry has, the higher leverage it is to write next.

**Length.** Target ~800–1500 words of prose plus one code block or worked example for a full entry. Stubs can be much shorter (50–200 words). Journal entries and conversation notes are shorter still — see those folders' READMEs.

**Updates.** When revising an entry, preserve the voice. Bump `last_updated`. Add a single line at the very bottom noting what changed (e.g. *"2026-06-02: revised pitfalls section after Lara's interview with Mr. Tan; added [[loneliness-vs-grief]] cross-link"*).

---

## 8. Folder placement

Brief guide — see each folder's README for fuller capture rules.

- `problem/` — observations about the elderly population, demographics, dynamics. One topic per file. No solutioning.
- `humans/` — empathy maps + raw conversation notes. Real people we talked to.
- `reframing/` — HMW iterations + devil's advocate. The framing-evolution record.
- `evidence/` — receipts. Stats with sources. Instrument notes. Annotated citations.
- `landscape/` — existing solutions, prior art, postmortems of things that failed.
- `journal/` — daily running log of the sprint.
- `strategy/`, `prototype/`, `pitch/` — dormant for now; wake up later.

If you can't tell where something goes, put it in `journal/` and we'll move it later. Capture first, refactor later.

---

## 9. Examples of solid entries

When in doubt, pattern-match against these. They're the canonical examples of the voice and structure.

- **`knowledge/eldercare.md`** — full problem-space overview. Demonstrates the six-section structure with a real-numbers worked example (the Singapore funnel) and an honest pitfalls section. Good model for any `problem/` entry.
- **`knowledge/reframing/hmw-current.md`** — argumentative synthesis entry. Demonstrates how to compress a team's reasoning into a defended position while staying honest about what the position doesn't do well. Good model for any synthesis or decision entry.
- **`knowledge/journal/2026-05-19.md`** — short-form journal entry. Demonstrates the daily-log shape: arc of the day, what we learned, what changed, what's next. Good model for journal entries.
- **`knowledge/reframing/hmw-2026-05-19-individual-exercise.md`** — record/source entry. Demonstrates how to preserve raw artifacts verbatim while adding light synthesis. Good model for capturing meetings, workshops, or exercises.

---

## 10. Update log

- **2026-05-19** — Initial voice spec. Distilled from the original wiki-author instructions; aligned with the conventions already used in `eldercare.md`, `hmw-current.md`, and the journal entry.
