# Eldercare Sprint

A six-month leadership sprint by five people, asking:

> **How might we help elderly in Singapore experience genuine daily connection, so that Singapore is brimming with elderly communities that are happy, mentally and physically healthy?**

Started May 19, 2026 · Singapore · Public journey.

---

## Two directories

```
.
├── knowledge/    ← the working wiki (Karpathy-voice markdown)
└── site/         ← the public microsite (Vercel-deployable)
```

Each directory has a spec file that governs how to update it without breaking the existing style:

- **`knowledge/VOICE.md`** — voice, reasoning order, structural conventions for wiki entries.
- **`site/SPEC.md`** — design principles, component patterns, update recipes for the microsite.

Both are written so you can paste them into a chat with an AI, then add your specific ask, and the result will match what's already there.

---

## Quick deploy

The microsite is static HTML. Three options:

1. **Vercel dashboard, drag-and-drop.** Drag the `site/` folder into Vercel. Done.
2. **Vercel CLI.** `cd site && npx vercel --prod`.
3. **GitHub + Vercel.** Push this repo, import to Vercel, set **Root Directory** to `site` in project settings.

If you want wiki links (`../knowledge/...`) to resolve on the deployed site, see `site/README.md` for the two build strategies.

---

## How to update — the wiki

Updates to the `knowledge/` folder should preserve the Karpathy voice. The full rules are in `knowledge/VOICE.md`. Copy any prompt below, fill in the placeholders, paste into an AI chat along with the contents of `knowledge/VOICE.md` (and the example entry the prompt mentions), and the output will match the existing style.

### Prompt 1 — Write a full new wiki entry

Use this when you have enough material to write a substantive entry (~800–1500 words). Examples: `caregiver-burnout`, `singapore-aging-population`, `companionship-vs-care`.

```
I want to add a new wiki entry to the eldercare knowledge base.

Topic: <TOPIC NAME>
Filename: knowledge/<FOLDER>/<KEBAB-CASE-NAME>.md
What I know / context: <PASTE NOTES, LINKS, OR A PARAGRAPH OF CONTEXT>

Rules:
1. Read knowledge/VOICE.md (attached / pasted below) for the voice and structural rules. The voice is Andrej Karpathy's: conversational, first-person-ish, technically rigorous, no corporate scaffolding, no closing summaries.
2. Use knowledge/eldercare.md as the reference example of tone and depth — match it.
3. Follow the six-section structure: opener (hook first) → tiny worked example → general formulation → walkthrough / code / concrete example → what confused me / pitfalls → connects-to paragraph → 3-5 proposed sibling stubs.
4. Use [[double-bracket]] cross-links to other entries even if they don't exist yet — those signal which entries should grow next.
5. Aim for 800–1500 words.
6. Start with YAML front matter: title, aliases (optional), prereqs (optional), status: draft, last_updated: <TODAY>.

Now write the entry.
```

### Prompt 2 — Write a stub entry

Use this when you want an entry to exist so other entries can link to it, but you don't have the substance yet.

```
I want to add a stub wiki entry.

Topic: <TOPIC NAME>
Filename: knowledge/<FOLDER>/<KEBAB-CASE-NAME>.md
Why it should exist: <ONE OR TWO SENTENCES>

Rules:
1. Read knowledge/VOICE.md for voice rules.
2. Write a stub: YAML front matter (status: stub), one paragraph stating what the entry will eventually cover, and the connects-to paragraph linking to 2-3 adjacent entries.
3. 50–200 words total. Keep it small — the point is just to hold the spot.

Now write the stub.
```

### Prompt 3 — Add a conversation note

Use this after talking to a real person (elderly, caregiver, family member) for the empathy work.

```
I just had a conversation with <NAME / RELATIONSHIP> on <YYYY-MM-DD>.

Raw notes / quotes / what I remember: <PASTE EVERYTHING YOU CAN RECALL OR SCRIBBLED DOWN>

Rules:
1. Read knowledge/humans/README.md for the conversation-note structure.
2. Create the file at knowledge/humans/<YYYY-MM-DD>-<name-slug>.md.
3. Use these sections: Context, Notes (raw — bullets fine), Quotes worth saving (3-5 verbatim), My read (honest, including what I might be projecting), Follow-ups.
4. Don't synthesize into an empathy map yet — that comes after 2-3 conversations.
5. YAML front matter: title, date, interviewer, duration, medium, status: raw.

Now write the conversation note.
```

### Prompt 4 — Synthesize an empathy map

Use this once you have two or three conversations with similar people.

```
I want to synthesize an empathy map from these conversations: <LIST OF CONVERSATION FILES>.

Persona / segment this map covers: <DESCRIPTION>

Rules:
1. Read knowledge/humans/README.md for the empathy-map structure.
2. Read each conversation file (paths above) before writing.
3. Create the empathy map at knowledge/humans/empathy-<persona-slug>.md.
4. Use these sections: Says, Thinks, Doesn, Feels, Pains, Gains, What surprised me, Open questions. Keep "Says" verbatim from the conversations. Hedge in "Thinks" since you're inferring.
5. YAML front matter: title, status: draft, last_updated, based_on (list the conversation files).
6. Voice: as in knowledge/VOICE.md — observation-first, honest about projection.

Now write the empathy map.
```

### Prompt 5 — Add a daily journal entry

Use this at the end of every working session.

```
I just finished a working session on <YYYY-MM-DD>.

What we did, in order: <BULLETS>
What we learned: <BULLETS>
What changed: <BULLETS>
What's next: <BULLETS>

Rules:
1. Read knowledge/journal/README.md for the entry shape.
2. Read knowledge/journal/2026-05-19.md as the reference example.
3. Create knowledge/journal/<YYYY-MM-DD>.md with sections: "The arc of the day", "What we learned", "What changed", "What's next".
4. Keep it short — five bullets per section is enough.
5. Voice: as in knowledge/VOICE.md. First-person plural ("we"). No corporate scaffolding.

Now write the journal entry.
```

### Prompt 6 — Add a new HMW iteration

Use this when the framing actually shifts — a conversation reframes the problem, a stat changes priors, devil's advocate lands.

```
The HMW is changing. The new framing is:

WHO: <NEW WHO>
DO: <NEW DO>
TO: <NEW TO>

What changed and why: <PARAGRAPH>

Rules:
1. Read knowledge/reframing/hmw-current.md (the current synthesis) and knowledge/VOICE.md.
2. Create a new file at knowledge/reframing/hmw-<YYYY-MM-DD>-<short-slug>.md following the structure of hmw-current.md (synthesis, how-we-got-here, why each component, what it does well, what it doesn't, devil's advocate seeds, connects-to). Add a "What changed from the previous HMW" section near the top.
3. Update knowledge/reframing/hmw-current.md to point at the new iteration as the current one — or replace its contents to match the new HMW.
4. Don't delete old HMW files — they're the journey record. Move outdated `hmw-current.md` content into a dated file before overwriting.
5. After writing the wiki side, use Prompt 9 (Update the HMW) below to update the microsite.

Now write the new HMW iteration.
```

### Prompt 7 — Add a landscape / evidence / problem stub

Use this to grow the "stubs to fill in" lists in the folder READMEs.

```
I want to write a real entry on <DANGLING WIKI LINK NAME> that's currently a stub.

Source material / what I know: <PASTE>

Rules:
1. Read knowledge/VOICE.md.
2. The entry goes at knowledge/<folder>/<existing-stub-name>.md.
3. Follow the full six-section structure (treat it as Prompt 1, but the topic is already defined in the relevant folder README).
4. Cross-link back to whatever entries currently link to this name.

Now write the entry.
```

### Prompt 8 — Revise an existing entry

Use this when new evidence or a new conversation changes something already written.

```
I want to revise this entry: knowledge/<path-to-file>.md

What changed in our understanding: <PARAGRAPH>

Rules:
1. Read knowledge/VOICE.md.
2. Read the current entry before editing — preserve its voice and structure.
3. Make the minimum edit consistent with the new understanding. Bump last_updated.
4. Add a single line at the very bottom of the file noting what changed (e.g. "2026-06-02: revised pitfalls after Lara's Mr. Tan interview; added [[loneliness-vs-grief]] cross-link.")

Now revise the entry.
```

---

## How to update — the microsite

Updates to the `site/` folder should preserve the editorial design. The full rules — color palette, typography, components, recipes — are in `site/SPEC.md`. Copy any prompt below, fill in placeholders, paste into an AI chat along with `site/SPEC.md`, and the result will match the existing look.

The SPEC is the authority. If the AI tries to invent colors, fonts, or components that aren't in the SPEC, push back and ask it to use what's there. The site stays self-consistent because everyone reads the same spec.

### Prompt 9 — Update the HMW on the microsite

Use this after Prompt 6 (a new HMW iteration). The microsite always shows the current question.

```
The HMW has been updated in the wiki. The new version is:

WHO: <NEW WHO>
DO: <NEW DO>
TO: <NEW TO>

Full statement: "How might we help <NEW WHO> <NEW DO>, so that <NEW TO>?"

Rules:
1. Read site/SPEC.md — specifically Recipe 2 (Update the HMW) in section 8.
2. Edit site/index.html in four places:
   a. The hero <h1> — restate the question.
   b. The hero .lede paragraph — update the "so that" clause.
   c. The .hmw-statement block in <section id="hmw"> — update the three <strong> segments.
   d. The .hmw-grid cells — update each .text content.
3. Add a new journey timeline entry (use Prompt 10 separately) noting the HMW revision.
4. Add a one-line entry to the SPEC update log (section 9 of SPEC.md) noting the change with today's date.

Now make the edits.
```

### Prompt 10 — Add a journey timeline entry

Use this for any significant moment in the sprint — a working session, a milestone hit, a reframing.

```
I want to add a new timeline entry to the microsite journey.

Date: <YYYY-MM-DD> · <Day label, e.g., "Day 7">
Heading: <SHORT HEADING — 4-7 WORDS>
What happened: <ONE PARAGRAPH OF PROSE>
Step chips (optional, the sequence of mini-steps within the session): <LIST OF 3-6 SHORT LABELS, MARK WHICH IS THE "FINAL" ONE>
Past or future event: <PAST | FUTURE>

Rules:
1. Read site/SPEC.md — specifically Recipe 1 (Add a journey timeline entry) in section 8, and the .timeline pattern in section 5.
2. In site/index.html, find <section id="journey"> and find the .timeline div.
3. Add a new <div class="entry"> in chronological position (the timeline currently runs oldest-to-newest top-to-bottom — match that).
4. If it's a future event, add the .future modifier class to the .entry div.
5. The arc chips are optional — only include if the session genuinely had a step sequence worth showing. Mark the final/punchline step with .step.final.
6. Add a one-line entry to the SPEC update log.

Now add the entry.
```

### Prompt 11 — Add a knowledge-base card

Use this when a new significant wiki entry is worth surfacing on the public site.

```
I want to add a knowledge-base card to the microsite.

Card title: <SHORT NAME, SERIF-DISPLAY APPROPRIATE>
Description: <ONE SENTENCE — WHAT'S IN THE ENTRY>
Target file: <RELATIVE PATH FROM site/, e.g., ../knowledge/problem/elderly-loneliness.md>
Status: <ACTIVE | DORMANT>

Rules:
1. Read site/SPEC.md — Recipe 3 (Add a knowledge-base card) in section 8.
2. In site/index.html, find <section id="wiki"> and find the .kb-grid div.
3. Add a new <a class="kb-card"> block. Use .dormant modifier if the folder isn't substantively active yet.
4. Match the structure of existing .kb-card blocks exactly: .name in serif (1.1rem, weight 500), .desc in soft body text.
5. Add a one-line entry to the SPEC update log.

Now add the card.
```

### Prompt 12 — Update a team member's lens

Use this if a team member's perspective deepens or changes through the work.

```
I want to update the lens for a team member on the microsite.

Team member: <NAME, INITIALS>
New lens (one sentence — what perspective they bring): <SENTENCE>

Rules:
1. Read site/SPEC.md — Recipe 4 (Update a team member's lens) and the .team-card pattern.
2. Find the matching .team-card in site/index.html.
3. Edit only the .lens paragraph. Keep it ONE sentence, observation-shaped — "whose ___" or "the lens: ___" or similar. No credentials, no titles, no bullets.
4. Add a one-line entry to the SPEC update log.

Now update the lens.
```

### Prompt 13 — Activate a dormant section

Use this when `strategy/`, `prototype/`, or `pitch/` wakes up — usually around month 3 or 4.

```
I want to activate the <STRATEGY | PROTOTYPE | PITCH> dormant card on the microsite.

What's actually in the folder now: <ONE-SENTENCE DESCRIPTION>

Rules:
1. Read site/SPEC.md — Recipe 5 (Move a knowledge card from dormant to active).
2. Find the relevant .kb-card.dormant in site/index.html.
3. Remove the .dormant class. Update the .desc to reflect actual content.
4. Add a one-line entry to the SPEC update log.

Now make the change.
```

### Prompt 14 — Make a bigger change to the microsite

Use this for anything that isn't covered by the recipes above — adding a new section, changing the layout, introducing a new component.

```
I want to make a bigger change to the microsite.

What I want: <DESCRIPTION>
Why: <REASONING>

Rules:
1. Read site/SPEC.md from top to bottom — design principles (section 1), color palette (2), typography (3), layout (4), components (5), voice (6), section flow (7).
2. Check whether the change fits an existing component or section. If yes, follow the pattern. If no, propose an extension to the SPEC FIRST — what new component, what colors (only from the palette unless we're extending it), what type styles.
3. Make the edit only after the SPEC has been extended.
4. Add a substantial entry to the SPEC update log (section 9) explaining the new pattern and when to use it.

Now propose the SPEC extension and the change.
```

---

## How to update — both at once

A few moves touch both directories. Example: HMW changes get a new wiki iteration AND a microsite update AND a journey entry. The right order is always:

1. Wiki first (the substance lives there).
2. Microsite second (it reflects the wiki).
3. SPEC update log last (records the change).

If you're using an AI to handle a multi-step update, paste both `knowledge/VOICE.md` and `site/SPEC.md` along with this README's relevant prompts, and tell the AI the order explicitly.

---

## The four-part rubric

This is what the sprint will be graded on at Demo Day. Each part is 25 points. The wiki is shaped by it:

| Rubric line | Wiki folder that feeds it |
|---|---|
| Leadership Journey (evidence of learning over 6 months) | `knowledge/journal/` |
| Quality of Thinking (evidence-backed analysis) | `knowledge/problem/` + `knowledge/evidence/` + `knowledge/landscape/` |
| MVP / Prototype (human centricity) | `knowledge/humans/` + later `knowledge/prototype/` |
| Presentation & Influence | later `knowledge/pitch/` |

The microsite is the substantive showcase of all four — it's literally what the judges will see when we point them at the URL.

## The team

- **Abhishek Kaul** — whose parents in India experience loneliness despite intact social circles.
- **Lara PuReum Yim** — finding new communities for recently-relocated elderly parents.
- **Aditi Agarwal** — carrying the observation that losing a life partner creates an irreplaceable absence.
- **Shobhit Singhal** — whose in-laws from Bangkok feel lonely in Singapore despite physical proximity to family.
- **Zheng Wei** — clinical and research lens on isolation and connection.

## Status

- ✅ Day 1 (May 19, 2026) — problem space, HMW, wiki, microsite, voice + design specs.
- ☐ Day 7 (May 26, 2026) — empathy maps + HMW revision.
- ☐ Demo Day — live prototype + pitch.

See `knowledge/journal/` for the running record.
