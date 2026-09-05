# Eldercare Sprint

A six-month leadership sprint by five people, asking:

> **How might we enable caregivers of the relatively healthy elderly in Singapore to activate trusted respite when a need arises — planned or urgent — layered onto Vanguard's Pasir Ris ICCP pilot as our first operational proof?**

Started May 19, 2026 · Singapore · Public journey. The app is live at **[singaporekakis.com](https://singaporekakis.com)**.

_The question has been through five dated iterations since we started. The [May 19 opener](https://github.com/quixoticblink/eldercare/blob/main/knowledge/reframing/hmw-2026-05-19-individual-exercise.md) → [Jun 15 NCSS reframe signal](https://github.com/quixoticblink/eldercare/blob/main/knowledge/reframing/hmw-2026-06-15-ncss-reframe-signal.md) → [Jun 25 caregiver reframe](https://github.com/quixoticblink/eldercare/blob/main/knowledge/reframing/hmw-2026-06-25-caregiver-respite.md) → [Jul 8 post-Vanguard narrowing](https://github.com/quixoticblink/eldercare/blob/main/knowledge/reframing/hmw-2026-07-08-post-vanguard.md) → [Jul 11 broadening](https://github.com/quixoticblink/eldercare/blob/main/knowledge/reframing/hmw-2026-07-11-broader-need.md) is the record of that. [`hmw-current.md`](knowledge/reframing/hmw-current.md) always points at the live one._

---

## Three directories

```
.
├── knowledge/    ← the working wiki (Karpathy-voice markdown)
├── site/         ← the public microsite (Vercel-deployable)
└── app/          ← Kakis, the working app (FastAPI + DuckDB + static frontend)
```

Each directory has a spec file that governs how to update it without breaking what's already there:

- **`knowledge/VOICE.md`** — voice, reasoning order, structural conventions for wiki entries.
- **`site/SPEC.md`** — design principles, component patterns, update recipes for the microsite.
- **`app/SPEC.md`** — the module contract, data model, API surface, and the full feature reference / user guide (section 9).

All three are written so you can paste them into a chat with an AI, then add your specific ask, and the result will match what's already there.

---

## Quick deploy

**The microsite** is static HTML. Three options:

1. **Vercel dashboard, drag-and-drop.** Drag the `site/` folder into Vercel. Done.
2. **Vercel CLI.** `cd site && npx vercel --prod`.
3. **GitHub + Vercel.** Push this repo, import to Vercel, set **Root Directory** to `site` in project settings.

Wiki links on the site are **absolute GitHub URLs** (`https://github.com/quixoticblink/eldercare/blob/main/knowledge/...`) rather than relative paths, so nothing needs bundling into the deployment. Any new wiki link should follow the same scheme — rationale in `site/README.md` and `site/SPEC.md` section 9.

**The app** runs on one small VM — backend serves the frontend, DuckDB is a single file, Caddy handles TLS. [`app/deploy/EC2-DEPLOYMENT.md`](app/deploy/EC2-DEPLOYMENT.md) documents the box that's actually live; [`app/deploy/README.md`](app/deploy/README.md) is the generic two-shape guide (note: its environment block predates v1.2, so check `app/backend/config.py` for the current variable list). Smoke test before any deploy:

```bash
cd app && python3 backend/tests/smoke.py    # full lifecycle; prints its own assertion count
cd app && npx playwright test              # 24 end-to-end specs against a throwaway backend on :8100
```

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

Use this when a folder wakes up. As of Aug 2026 there are **no dormant cards left** — strategy, prototype and pitch were all un-dormanted on the microsite in the same 2026-07-11 pass. Keep the recipe for the next folder that gets added.

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

## The app — Kakis

The prototype became a real thing. `app/` is a deployed application at **[singaporekakis.com](https://singaporekakis.com)** — a database, sign-in codes arriving on real phones, and three roles that transact with each other. The working name *Kakis* (Singlish for the trusted companions you can call on) is provisional; there's a Kampung Kakis collision noted in the wiki.

**Stack:** FastAPI + DuckDB behind a no-framework HTML/JS frontend, on one t3.micro in Singapore, TLS via Caddy. One box, one file for a database. That's not a placeholder for a "real" stack — at pilot scale it's the right amount of machinery, and one person can understand the whole thing in an afternoon. The Next.js/Postgres upgrade path is written down in `knowledge/prototype/kakis-build-plan.md` and deliberately not taken yet.

**Three roles share one app:**

- **Caregiver** — set up the household and care plan once, book a visit (service → urgency → trigger → details), read the 4-digit start code to the kaki, receive the report.
- **Kaki** — declare availability as a weekly half-day grid plus dated exceptions, accept or pass back an assigned visit, start it with the family's code, finish with a report.
- **Coordinator** — approve people, match visits (urgent first, availability sorts rather than filters), and optionally automate both.

**Four design decisions worth knowing before you change anything:**

1. **The start code is one-way.** The kaki never sees it in their own app. That asymmetry is what turns "the app says a visit happened" into "someone was at the door and the family let them in."
2. **No public ratings, anywhere.** Concerns from either side go privately to the care team — MOH guidance, and it removes the mechanism that makes gig workers performatively cheerful.
3. **Every automation defaults off.** Each one removes a human from a decision about who enters a vulnerable person's home.
4. **Every number lives in `app/assumptions.json`** with its source. Most are still `PLACEHOLDER` and say so on every screen showing a dollar figure.

**Where to read further:**

| File | What's in it |
|---|---|
| [`app/SPEC.md`](app/SPEC.md) | The contract: architecture, the seven modules and their change boundaries, roles/auth, data model, API surface, environment variables, the change log (v1 → v1.5), and **section 9 — the full feature reference and user guide** |
| [`app/deploy/EC2-DEPLOYMENT.md`](app/deploy/EC2-DEPLOYMENT.md) | The box that's actually running — the live deployment, start to finish |
| [`app/deploy/README.md`](app/deploy/README.md) | The generic two-shape guide: systemd, Caddy, backups, third-party service checklist. Its env block predates v1.2 — `app/backend/config.py` is the real variable list |
| [`app/deploy/SECURITY-AUDIT.md`](app/deploy/SECURITY-AUDIT.md) | ISO/IEC 5055 self-assessment (v1.5, 9 Aug 2026), findings closed, residual risk, and what "fit for a supervised pilot" excludes |
| [`knowledge/prototype/kakis-app.md`](knowledge/prototype/kakis-app.md) | The wiki entry — why it's built this way, and the failures that cost real time |
| [`knowledge/prototype/roadmap.md`](knowledge/prototype/roadmap.md) | What shipped in each version and what's next, ordered by the decision each item waits on |

**Status:** v1.6, live, hardened, 368 smoke assertions plus a 24-spec Playwright suite (`cd app && npm i && npx playwright test`) covering the full lifecycle. Fit for a **supervised tabletop**, which is exactly what NCSS and Vanguard asked for on Aug 3. Not fit for unsupervised public launch — backups have never been restore-tested, there's no PDPA review or user-facing deletion path, and the pricing is still placeholder.

---

## How to update — the app

The SPEC is the contract: **every change names the module it touches, and only that module's files change.** If a change can't be expressed that way, amend the SPEC first (add a module or split one), then write the code.

### Prompt 15 — Change something inside an existing module

```
I want to change something in the Kakis app.

What should change: <DESCRIPTION, IN USER TERMS>
Why: <REASONING — evidence, partner feedback, or a bug>

Rules:
1. Read app/SPEC.md (attached / pasted below). Identify which module owns this —
   M-AUTH, M-USERS, M-CARE, M-VISITS, M-ADMIN, M-HELP or M-CORE — using the
   "If you want to change…" column in section 2.
2. Name the module before you write any code, and touch only that module's files.
   Routers never import each other; shared logic goes in db.py/security.py/services/.
   Frontend views never call fetch directly — always through api.js.
3. Respect the hard rules in SPEC section 9.5: no public ratings, certification gates
   tasks, urgent sorts first, the kaki never sees the start code, money figures are
   labelled illustrative.
4. If the change touches the schema, add a migration in db.py and checkpoint after
   schema init — an un-checkpointed ALTER left a WAL entry that crash-looped the
   service on its second boot.
5. Update SPEC section 9 (the user guide) if the change is user-visible, and add a
   change-log line to SPEC section 10.
6. Extend backend/tests/smoke.py to cover the new behaviour.

Now name the module and make the change.
```

### Prompt 16 — Add a new module

Use this when the change genuinely doesn't fit an existing module — payments, certification tracking, an elderly self-book surface.

```
I want to add a new module to the Kakis app.

What it does: <DESCRIPTION>
Why it isn't an existing module: <REASONING>

Rules:
1. Read app/SPEC.md. Check section 8 ("Out of scope in v1") first — it already names
   where several likely additions would land.
2. Amend the SPEC BEFORE writing code: add a row to the section 2 module table
   (owns / backend files / frontend files / "if you want to change…"), any new tables
   in section 4, new endpoints in section 5, new env vars in section 6.
3. Then write the code, following the boundaries you just declared.
4. Add the user-facing description to SPEC section 9 and a change-log line to section 10.
5. Add smoke-test assertions for the new endpoints.

Now propose the SPEC amendment, then the code.
```

### Prompt 17 — Record a build round in the wiki and on the site

Use this after shipping a version, so the build leaves a trace outside the code.

```
We shipped a new version of the Kakis app.

Version: <vX.Y> · Date: <YYYY-MM-DD>
What changed: <BULLETS, GROUPED BY MODULE>
What went wrong on the way: <ANY FAILURE WORTH REMEMBERING — be honest>

Rules:
1. Add the change-log entry to app/SPEC.md section 10, matching the existing entries:
   one bold headline, then prose naming the modules touched.
2. Update knowledge/prototype/kakis-app.md — revise "Where it stands", and add to
   "What confused me / what went wrong" if a failure is worth keeping. Read
   knowledge/VOICE.md first; this is a wiki entry, so it follows the wiki voice.
3. Add a journey timeline entry to the microsite (Prompt 10 above) if the round is
   externally visible.
4. Bump last_updated in any front matter you touched.

Now make the updates.
```

---

## How to update — all three at once

A few moves touch more than one directory. An HMW change gets a new wiki iteration AND a microsite update AND a journey entry. A shipped app version gets a SPEC change-log line AND a wiki revision AND (sometimes) a timeline entry. The right order is always:

1. Wiki first (the substance lives there).
2. App second, if code is involved — SPEC amendment before code, always.
3. Microsite third (it reflects the wiki and the app).
4. SPEC update logs last (they record what changed).

If you're using an AI to handle a multi-step update, paste the relevant specs — `knowledge/VOICE.md`, `site/SPEC.md`, `app/SPEC.md` — along with this README's relevant prompts, and tell the AI the order explicitly.

---

## The four-part rubric

This is what the sprint will be graded on at Demo Day. Each part is 25 points. The repo is shaped by it:

| Rubric line | What feeds it |
|---|---|
| Leadership Journey (evidence of learning over 6 months) | `knowledge/journal/` + `knowledge/reframing/` |
| Quality of Thinking (evidence-backed analysis and strategy) | `knowledge/problem/` + `knowledge/evidence/` + `knowledge/landscape/` + `knowledge/strategy/` |
| MVP / Prototype (human centricity) | `knowledge/humans/` + `knowledge/strategy/` + `knowledge/prototype/` + **`app/` — the running application** |
| Presentation & Influence | `knowledge/pitch/` + the microsite |

The microsite is the substantive showcase of all four — it's literally what the judges will see when we point them at the URL. The app is the answer to the MVP line: a prototype proves you understood the journey; a running app proves the journey survives contact with an SMS provider and a coordinator's Tuesday.

## The team

- **Abhishek Kaul** — whose parents in India experience loneliness despite intact social circles.
- **Lara PuReum Yim** — finding new communities for recently-relocated elderly parents.
- **Aditi Agarwal** — carrying the observation that losing a life partner creates an irreplaceable absence.
- **Shobhit Singhal** — whose in-laws from Bangkok feel lonely in Singapore despite physical proximity to family.
- **Zheng Wei** — clinical and research lens on isolation and connection.

## Status

- ✅ Day 1 (May 19, 2026) — problem space, HMW, wiki, microsite, voice + design specs.
- ✅ Round 1 (May 21–25, 2026) — six field interviews, five signals.
- ✅ Day 7 (May 26, 2026) — HMW held, first empathy map delivered.
- ✅ NCSS meeting (Jun 15, 2026) — reframe signal; caregiver-respite framing surfaces; Vanguard named as a possible partner.
- ✅ Solutioning (Jun 25, 2026) — HMW reframed to caregivers; managed-marketplace shape; strategy folder activated.
- ✅ Vanguard site visit (Jul 8, 2026) — anchor partner confirmed; Pasir Ris ICCP-layered pilot offered by year-end.
- ✅ HMW narrowing (Jul 8, 2026) — crisis-activation, six named triggers, WHERE + WHEN inside the sentence.
- ✅ HMW broadening (Jul 11, 2026) — crisis-only caught as too tight three days later; DO widened to "when a need arises — planned or urgent". Same product, wider demand curve.
- ✅ SGLN masterclass (Jul 20, 2026) — reframe validated by the cohort; prototype milestone re-aimed at caregiver testing; devil's advocate at 15 critiques.
- ✅ Kakis app built and deployed (Jul 21 – Aug 9, 2026) — six rounds, v1 → v1.5: initial build, prototype-sync, dual-channel sign-in, kaki availability + sourced assumptions, assignment notifications and automation toggles, then ISO 5055 security hardening. Live at [singaporekakis.com](https://singaporekakis.com).
- ✅ NCSS + Vanguard (Aug 3, 2026) — our live-pilot ask countered with a **tabletop exercise**: two separate sessions, roughly five sets of staff + micro-jobber + senior run as two or three groups. Scope narrows to chaperoning. Supply, not demand, named as the binding constraint.
- ✅ NCSS desk review (Aug 18, 2026) — the live app walked role by role, thirty items, one reversing the start-code direction. [journal/2026-08-18-ncss-app-review.md](knowledge/journal/2026-08-18-ncss-app-review.md); register in [prototype/ncss-app-review-2026-08-18.md](knowledge/prototype/ncss-app-review-2026-08-18.md).
- ✅ Table Top Exercise, round 1 (Aug 21, 2026) — eight seniors on their own phones at a Care Corner AAC in Toa Payoh, Vanguard + NCSS facilitating. Lifecycle held; onboarding around it didn't. Session record in [journal/2026-08-21-tabletop-vanguard-ncss.md](knowledge/journal/2026-08-21-tabletop-vanguard-ncss.md); every recommendation, mapped to app module, in [prototype/tabletop-2026-08-21-feedback.md](knowledge/prototype/tabletop-2026-08-21-feedback.md).
- ✅ Prototype milestone (Aug 20, 2026) — met in substance by the Aug 21 session. Not yet tested against the six crisis triggers; the session ran planned bookings.
- ✅ Build round v1.6 (Sep 5, 2026) — Buckets 1 and 2 of [prototype/feature-buckets-2026-09-04.md](knowledge/prototype/feature-buckets-2026-09-04.md), eighteen features, each behind a Playwright test (24 specs) and a smoke assertion (368). Identity both ways at the door, exact times, gender and same-kaki preferences, cancellation lifecycle, certificates. Live.
- ☐ Table Top Exercise, round 2 — same group, to validate the changes. NCSS/Care Corner's own session still to be arranged.
- ☐ Demo Day (September 2026) — pilot design + pitch.

**Current phase:** v1.6 shipped, Table Top Exercise round 2 next. **Anchor partner:** Vanguard (MOH Holdings), convened by NCSS. **Current HMW:** [reframing/hmw-current.md](knowledge/reframing/hmw-current.md). **Live app:** [singaporekakis.com](https://singaporekakis.com).

**The most important unresolved thing:** three framings are live at once and nobody has reconciled them — caregiver relief (ours), resilient caregiving (NCSS), and operational digitisation of an existing manual service (Vanguard's proposed success metric, "lessen your administrative burden", which quietly moves the primary user from the caregiver to the coordinator). See [journal/2026-08-03-ncss-vanguard.md](knowledge/journal/2026-08-03-ncss-vanguard.md).

See `knowledge/journal/` for the running record, `knowledge/maps/timeline.md` for the chronological view, and `knowledge/README.md` for the current snapshot. (`knowledge/purpose.md` is the orientation document — good on why this sprint exists, but its "where we are now" section is a mid-July snapshot and hasn't been re-cut since.)
