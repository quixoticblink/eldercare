# Microsite spec — design guidelines, flow, update recipes

**Purpose.** Hand this file to any future collaborator (human or AI) along with your "please update the site to add X" request. The spec is what keeps the site looking like itself across edits. If something here is ambiguous, the existing `index.html` is the authority — match its patterns.

**How to use this with an AI.** Paste this entire file, then add your specific ask. Example: *"Using the SPEC.md attached, add a new journey timeline entry for 2026-05-26 covering empathy-map work."* The AI then has the design rules, current section flow, and update recipe in one shot.

---

## 1. Design principles

We are aiming for *editorial / professional / restrained*, themed to **SGLN TECH** — the Singapore Leaders Network technology programme this sprint belongs to. SGLN TECH's brand signature is a blue gradient; the microsite borrows that identity. The site should feel like a thoughtful publication produced by a serious leadership programme — not a SaaS landing page, and not a generic corporate template either.

The structure is *dark bookends, light body*: a blue-gradient hero and a deep-navy footer frame a cool-toned light reading area. Header and footer are navy; the content in between stays light for readability.

What we want:

- **Serif headings, sans-serif body.** EB Garamond for display, Inter for body. Mono only for labels and metadata. This editorial type system is what keeps the site from looking like a stock corporate template — keep it even though the palette is now corporate blue.
- **Generous whitespace.** Sections are tall (5rem padding top and bottom). Body copy is narrow (about 38rem / 60ch).
- **Cool-toned light body.** A very light blue-grey (`--bg`), not pure white, not warm. The reading area stays light.
- **Blue-gradient hero.** The hero is a diagonal gradient from deep navy to azure — the SGLN TECH signature. White text on top.
- **One accent color.** SGLN blue (`--accent`, `#1466AC`). Used for the question, hover states, timeline dots, card top-borders, emphasis. A brighter azure (`--azure-bright`) is reserved for small bright marks on dark backgrounds only.
- **Italics carry intellectual weight.** The lede paragraph is italic. The HMW statement is italic. Single-word emphasis inside paragraphs uses `<em>`. Don't bold-emphasize prose.

What we avoid:

- Drop shadows beyond the most subtle. Cards are flat or near-flat; the one exception is a soft blue-tinted lift on knowledge-card hover.
- Gradients anywhere except the hero. The hero gradient is the signature — don't scatter gradients across other sections.
- Stock photography. The site is text-driven and the typography does the work.
- Emoji. Anywhere.
- Capitalization games. No ALL CAPS HEADLINES. Sentence case for everything except eyebrow labels (which are mono uppercase as a deliberate visual rhythm shift).
- Animations beyond the most subtle 120ms transitions on hover states.
- Accent colors outside the blue family. Stay within the SGLN blue / navy / azure palette — no green, no orange, no pink.

---

## 2. Color palette

All defined as CSS custom properties in `style.css` under `:root`. Use the variable, never the hex. If you find yourself wanting a color that isn't defined, propose adding it to the palette in the SPEC update log (section 9) first.

Light body — the reading area:

```
--bg          #F5F8FC  Cool light blue-grey, page background
--bg-elev     #FFFFFF  Card surfaces (team, knowledge, HMW cells)
--bg-warm     #E9F1F9  Light blue tint (rubric cards, timeline step chips, callout)
--text        #0F2742  Primary text, dark navy slate
--text-soft   #44566E  Secondary text, descriptions
--text-muted  #5F7288  Tertiary text, eyebrow labels, dates (was #7587A0; tightened 2026-07-11 for WCAG AA on small mono text)
--accent      #1466AC  SGLN blue — the one accent color
--accent-soft #BCD6EC  Faded accent for borders and selection
--accent-bg   #E7F1FA  Tinted background for the HMW statement
--border      #DBE3EF  Standard card/section border
--border-soft #E7ECF4  Subtler border for chips and tertiary surfaces
--rule        #C3D1E2  Horizontal rules, timeline spine
```

Dark sections — header, hero gradient, footer:

```
--navy-deep     #0A2740  Deepest navy — header bg, footer bg, gradient start
--navy-mid      #134B86  Mid blue — gradient middle
--azure         #2487C8  Bright azure — gradient end
--azure-bright  #4FB0E4  Brightest azure — small marks on dark (hero dot, nav hover)
--on-dark       #FFFFFF  Text on dark
--on-dark-soft  #C5DBED  Soft text on dark (hero lede, footer body)
--on-dark-muted #93A9C2  Muted text on dark (hero meta, footer colophon)
```

The hero gradient is `linear-gradient(122deg, --navy-deep 0%, --navy-mid 58%, --azure 116%)`. The header is `--navy-deep` at 93% opacity with blur. The footer is solid `--navy-deep`.

A few literal hexes appear in `style.css` for text-on-dark accents that don't recur often enough to justify variables: `#93C6E8` (hero eyebrow), `#6FC5EE` (hero `<em>` highlight), `#7FC4EC` (footer links). If you touch these, keep them in the same light-azure family.

Selection color uses `--accent-soft`. Code (`<code>`) inherits body color but uses mono — no boxes around it.

---

## 3. Typography

Font stack (loaded from Google Fonts at the top of `index.html`):

- **Display.** `--display: "EB Garamond", Georgia, "Times New Roman", serif;`
- **Body.** `--body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;`
- **Mono.** `--mono: "JetBrains Mono", "Menlo", "Consolas", monospace;`

Hierarchy:

- **h1 (hero only).** `clamp(2.4rem, 5vw, 4.0rem)`, EB Garamond 500, line-height 1.15. One per page.
- **h2 (section headings).** `clamp(1.7rem, 3vw, 2.2rem)`, EB Garamond 500.
- **h3 (sub-sections).** `1.35rem`, EB Garamond 500.
- **h4 (cards).** `1.05rem`, Inter 600 — note this is the only h-level that's sans, because it's used for compact card titles where the serif gets too ornate.
- **Body paragraph.** Inter 400, `17px` base, line-height 1.65.
- **`.lede`** — italic EB Garamond, used for the one-line summary right under each h2.
- **`.eyebrow`** — mono, 0.72rem, uppercase, letterspacing 0.14em. Goes above each section heading.
- **`.small`** / **`.muted`** — utility classes for fine print and de-emphasis.

Italic display type is structurally important — it's how the site signals "this sentence is the thesis." Used on the lede paragraph and the `.hmw-statement` block.

Don't introduce new font weights. Don't shrink the body type. Don't switch to a different serif.

---

## 4. Layout system

Two container widths:

- **`.container`** — `max-width: 56rem` (var `--measure-wide`). For wide section content like the hero, knowledge grid, footer.
- **`.narrow`** — `max-width: 38rem` (var `--measure`). For body-copy-heavy sections. This is the editorial column width — about 60ch.

Padding inside containers is `1.5rem` horizontal. Sections have `5rem 0` vertical padding. Sections are separated by a 1px `--border` line.

The site is a single scrolling page. Anchor links (`#journey`, `#hmw`, etc.) drive in-page navigation from the sticky header. The header is a deep-navy translucent strip with backdrop blur — brand on the left, nav on the right. The hero directly below it is a blue gradient, so at the top of the page the header reads as floating on the gradient; once you scroll into the light body it reads as a solid dark bar. The footer is solid deep navy. These dark bookends are the SGLN TECH frame around the light reading area.

Mobile breakpoint is `~720px`. The HMW grid collapses to one column, the team grid auto-fits to as many cards as fit at min 200px each, the footer collapses to a single column, and the header nav disappears below 600px (the brand stays).

---

## 5. Component patterns

When adding new content, reach for one of these patterns first. If nothing fits, the right move is usually to extend an existing pattern, not invent a new one.

### `.eyebrow` + `<h2>` + `<p class="lede">`

The opening rhythm for every section. Eyebrow is the section's category in mono uppercase; h2 is the actual heading in serif; lede is one italic sentence summarizing the section. Always in this order. Always.

```html
<p class="eyebrow">The Question</p>
<h2>One sentence, hard-earned.</h2>
<p class="lede">A short, single-sentence framing in italic.</p>
```

(The lede class can be on a `<p>` even when the h2 has body paragraphs following — they sit comfortably together. The first non-lede paragraph just uses default styling.)

### `.hmw-statement`

The big italic block-quote-style display of the HMW. Cream-tinted background, left border in accent, italic serif. Use the inline `<strong>` tags to highlight the three slots (WHO, DO, TO) in non-italic accent color.

Update this every time the HMW changes. Old HMWs don't stay on the page — they move into the wiki at `knowledge/reframing/hmw-YYYY-MM-DD-*.md`. The microsite always shows the current.

### `.hmw-grid`

Three-cell grid (WHO / DO / TO). Each cell has a mono label, a small subtitle, and the actual content in display type. Pairs with `.hmw-statement` above it. Collapses to one column on mobile.

### `.timeline` (the journey)

The journey timeline is a vertical list of `.entry` blocks against a left-side rule line. Each entry has:

- `.date` — mono uppercase, in accent color for past/present entries, muted for future.
- An `<h3>` heading.
- A paragraph of prose describing what happened (or what will happen).
- Optionally, an `.arc` div with `.step` chips representing the sequence within that working session. Mark the final step with `.step.final` (accent-colored chip).

The `.entry.future` modifier muffles the entry (gray dot instead of accent, muted heading).

When you add a new entry, the most recent goes at the *top* of the timeline (so the page reads "here's what just happened" first). Or you can keep chronological — pick one and stick with it. Currently the page is chronological top-to-bottom (May 19 → Demo Day).

### `.team-card`

A card with mono-style initials in serif italic at the top, a name in serif, and a one-paragraph "lens" describing what perspective the person brings. Don't write conventional bios. The voice is *"the lens this person brings is X"* — one sentence, observation-shaped, not credentials-shaped.

Update when team composition changes or when someone's lens deepens through the work.

### `.kb-card` (knowledge base index)

Hyperlinked card with a serif name and a one-line description in soft text. Hover lifts slightly. The `.dormant` modifier dims cards for folders that aren't active yet (strategy, prototype, pitch until later in the sprint).

### `.rubric-card`

A warm-tinted card showing one of the four rubric dimensions. Points in mono uppercase, dimension name in serif, description in soft body. The four are fixed (Leadership Journey, Quality of Thinking, MVP/Prototype, Presentation & Influence) — don't add or rename them unless the rubric itself changes.

### `.callout`

Cream-tinted block with an accent left border, used for honest asides — "what this doesn't do well," self-critiques, hedges. Use sparingly. One per section is more than enough.

### `<hr class="rule">`

Subtle horizontal rule inside a `.narrow` container, used to separate two sub-areas inside a single section.

### `.signal` (field-interview signals)

Used in the "What We Heard" section. A `.signals` container holds a vertical stack of `.signal` blocks separated by hairline rules. Each `.signal` is a two-column grid: a large serif-italic number (`.signal-num`) on the left, and `.signal-body` on the right holding an `<h3>` finding statement, a paragraph of supporting prose, and a `<blockquote class="signal-quote">` carrying a verbatim interview quote with a `<cite>` attribution. Collapses to one column on mobile.

Use this only for findings backed by a real quote — the quote is the point, it's what makes the section read as human-centred rather than asserted. Keep quotes verbatim (light punctuation cleanup is acceptable for presentation; the exact raw wording lives in the wiki conversation notes). Attributions stay anonymous — respondent role and date, never names.

### `.empathy-map` (empathy-map quadrants)

Used in the "Empathy Map" section. A `.empathy-map` is a 2×2 grid of `.quadrant` cards — Says, Thinks, Does, Feels, the four classic empathy-map quadrants. Below it, `.empathy-pg` is a two-column pair of `.pg-card` blocks for Pains and Gains. Each card carries a mono uppercase `.q-label` and a short `<ul>` of 3–5 items. The four quadrants are white (`--bg-elev`); the Pains/Gains pair is warm-tinted (`--bg-warm`) so it reads as the synthesis layer beneath the quadrants. The Says quadrant takes a `.says` modifier, which italicises its items because they are verbatim quotes. Both grids collapse to one column below 640px.

This is the one place bulleted lists are correct on the site — empathy-map quadrants are genuine enumerations. Keep items to one line each and grounded in the interviews; the full map with attributions and flagged inferences lives in the wiki.

---

## 6. Voice and tone

The site copy follows the same voice as the wiki entries — observation-first, conversational, technically rigorous but never stiff. Specifically:

- **Lowercase "ok so" / "the punchline is" allowed** in long-form wiki entries, but not in microsite copy. The microsite is a touch more composed than the wiki notes.
- **First-person plural.** "We started May 19." Not "the team" (third-person feels distant) and not "I" (this is a five-person sprint).
- **No corporate scaffolding.** No "in this section we will…" No "let's dive in." No "stay tuned." No closing summaries.
- **Concrete over abstract.** Numbers, names, specific quotes. "30,000 people, roughly the capacity of the National Stadium" beats "many elderly Singaporeans."
- **Honest about what we don't know.** The site explicitly says what the HMW *doesn't* do well. We keep that habit. A microsite that claims to have all the answers reads worse than one that's openly mid-journey.
- **One thesis per section.** Each section is built around one sentence-long claim, articulated in the lede and developed across two or three paragraphs.

Punctuation:

- **Em-dashes** ( — ) for parenthetical asides. Real em-dashes, not double hyphens.
- **Single quotes** inside double, standard English usage.
- **Oxford comma**, always.
- **Italics for emphasis** inside running prose; **bold only** inside HMW slot highlights and rubric points. Don't bold for emphasis.

---

## 7. Section flow (current page structure)

The page reads in this fixed order. New sections can be added but they should slot in here, not appear at random.

1. **Hero.** Project name (brand in header), the HMW restated as a question, the lede with the "so that" clause, meta line.
2. **Journey.** The narrative arc. Currently a timeline from May 19 onward to Demo Day, with past entries in accent and future entries muted.
3. **The Question.** The HMW statement, the three-cell grid, the "How we got here" explanation, the honest-about-shortcomings callout.
4. **Team.** Five cards with initials, names, and lenses.
5. **Problem Space.** Three paragraphs of observation-first framing, ending with a link to the wiki overview.
6. **What We Heard.** Field-interview signals. A short intro honest about sample size, then a numbered set of `.signal` blocks — each a finding plus a verbatim quote — ending with links to the wiki synthesis and raw notes. This is the section that most directly evidences "human centricity" for the rubric.
7. **The Empathy Map.** The customer empathy map synthesized from the six field interviews — a 2×2 of Says / Thinks / Does / Feels, then a Pains / Gains pair, closing on a callout. Sits right after What We Heard because it is the same interviews, synthesized into the persona.
8. **How We Work / Knowledge.** The wiki structure as cards, plus the four-part rubric mapping.
9. **Footer.** Project description, navigation links, colophon.

Adding new sections: most additions will fit inside an existing section. If you really need a new top-level section, put it before *Team* (which functions as a midpoint) or between *Problem Space* and *Knowledge*. Don't add anything after the rubric — the rubric is the closer.

---

## 8. Update recipes

The five most common updates over the sprint.

### Recipe 1 — Add a journey timeline entry

Inside `<section id="journey">`, find the `.timeline` div. Add a new `.entry` block in chronological position (newest entries near the top of the section if you've been adding latest-first; near the bottom if chronological — match what's there).

```html
<div class="entry">
  <div class="date">May 26, 2026 · Day 7</div>
  <h3>Empathy maps and a revised HMW</h3>
  <p>One paragraph of prose — what happened, what we learned, what changed. Same voice as existing entries.</p>
  <div class="arc">
    <span class="step">interview prep</span>
    <span class="step">six conversations</span>
    <span class="step">synthesis</span>
    <span class="step final">HMW v2</span>
  </div>
</div>
```

Move the entry's `future` class off when the date passes. (Past entries don't carry the `future` modifier.)

### Recipe 2 — Update the HMW

When `knowledge/reframing/hmw-current.md` changes, the microsite needs three edits:

1. The hero `<h1>` — update the question phrasing if WHO or DO changed.
2. The hero `.lede` — update if the TO changed.
3. The `.hmw-statement` block in `#hmw` — update the `<strong>` segments.
4. The `.hmw-grid` cells — update the `.text` content in each.

Note the date of the change in the SPEC update log (section 9). Add a journey timeline entry noting the revision.

### Recipe 3 — Add a knowledge-base card

Inside `<section id="wiki">`, find the `.kb-grid` div. Add a new `<a class="kb-card">` with a serif name and a one-line description. Use the `.dormant` modifier for folders not yet active.

```html
<a class="kb-card" href="../knowledge/<path>/README.md">
  <div class="name">Card name</div>
  <p class="desc">One sentence about what's in there.</p>
</a>
```

### Recipe 4 — Update a team member's lens

Inside `<section id="team">`, find the relevant `.team-card`. Edit the `.lens` paragraph. Keep it one sentence, lens-shaped ("whose ___" or "the lens: ___"). Don't add credentials, titles, or bullet points.

### Recipe 5 — Move a knowledge card from dormant to active

Remove the `.dormant` class from the `<a>`. Update the description to reflect what's actually in the folder (it'll have been empty before).

---

## 9. Update log

Keep this current. Each entry: date, what changed, who or what triggered it. Most recent at the top.

- **2026-07-11 (major — reframe + strategy section)** — The sprint has moved twice since May 26; the site now reflects it. **Hero** rewritten around the July 8 HMW (*"activate trusted respite when a crisis hits"*), meta updated to "Phase: strategy & pilot design" and "Demo Day · September 2026". **Journey timeline** gained five new past entries (Jun 15 NCSS, Jun 25 solutioning, Jul 7 prep, Jul 8 Vanguard visit, Jul 8 afternoon HMW narrowing); the three "future" entries were replaced with Jul 20 Masterclass, Aug 20 Prototype milestone, Sep 2026 Demo Day. **"The Question" section** restructured — h2 changed from "One sentence, hard-earned" to "The question has moved twice," HMW-statement and grid rewritten to the July 8 version, callout rewritten. New **`.hmw-history` component** (see section 5) shows the four dated iterations (May 19 → Jun 15 signal → Jun 25 → Jul 8 current) with what-changed prose; the `.current` modifier highlights the active row. **New top-level Strategy section (`#strategy`)** inserted between Empathy and Knowledge — lede paragraph, three-paragraph body, new **`.strategy-grid`/`.strategy-card` component** (see section 5) presenting the triad (managed marketplace / consistency as constraint / multi-payer stack), a Vanguard-in-one-paragraph `.callout`, and wiki deep-links. Nav (header + footer) gained a "Strategy" link. **Knowledge base** gained eleven new kb-cards (three new HMW iterations, the whole strategy folder, NCSS IDIs, Marsiling AAC, Grab market sizing, Vanguard operational data, Vanguard landscape, Singapore care taxonomy, Purpose). **Strategy** un-dormanted; **Prototype/Pitch** stay dormant. **Team lenses** for Abhishek, Lara, Aditi, and Zheng Wei each gained one sentence tying them to the strategy work. **Problem section** ¶3 lightly rewritten to acknowledge the caregiver reframe without overwriting the original framing. **What We Heard** and **Empathy Map** kept largely intact (the round-1 findings are still true), but each gained one sentence noting how the June/July field material moved the WHO. **Accessibility pass:** added skip-link, `<main>` landmark, `aria-labelledby` on every section, `aria-label` on the primary nav, `aria-hidden` on decorative initials/dots/signal numbers, visible focus rings, and `prefers-reduced-motion` guard. Update log written after the edit, per instruction. Triggered by the June–July knowledge deltas: hmw-2026-06-15, hmw-2026-06-25, hmw-2026-07-08, strategy/*, evidence/vanguard-operational-data, journal/2026-06-15 through 2026-07-08.
- **2026-05-25 (links)** — Repointed every wiki link in `index.html` from relative `../knowledge/...` paths to absolute GitHub URLs (`github.com/quixoticblink/eldercare/blob/main/knowledge/...`). This fixes the long-standing issue that relative wiki links 404 on the deployed site when Vercel's root directory is `site/`. Added a prominent "Browse the full wiki on GitHub" link in the `#wiki` section intro, and a "Full wiki on GitHub" footer link. Future kb-cards should use the same GitHub URL scheme, not relative paths. Note: this assumes the GitHub repo is public — if it is private, public site visitors cannot follow these links.
- **2026-05-25 (section)** — Added "The Empathy Map" section (`#empathy`) between What We Heard and Knowledge. New `.empathy-map` component — a 2×2 Says/Thinks/Does/Feels quadrant grid plus a warm-tinted Pains/Gains pair, closing on a `.callout` (see section 5). Content synthesized from the wiki empathy maps (`empathy-map-2.md`, `empathy-elderly.md`). Header and footer nav gained an "Empathy" link. Triggered by a request to surface the empathy-map synthesis on the homepage.
- **2026-05-25 (supersede)** — Repointed two kb-cards and their footer links to the team's newer, fuller wiki entries. "Empathy map — elderly" now → `empathy-map-2.md` (the six-interview map, replacing the three-interview `empathy-elderly.md`). The loneliness card, renamed "Singapore ageing and loneliness", now → `singapore-eldery-stats-2.md` (replacing the rougher `loneliness.md`). The May 26 timeline entry was reworded to match the six-interview basis. The superseded wiki files still exist but are no longer linked from the site. HMW unchanged. Triggered by the user's decision to treat the newer entries as current.
- **2026-05-25 (sync)** — Synced the site with new knowledge-base entries. The "May 26 · upcoming" journey entry became a completed "deliverable met" entry (HMW held; first empathy map synthesized). Three kb-cards added — "Empathy map — elderly", "Interview round 1 — findings", "Loneliness — what it is". "Humans", "Evidence" and "Devil's advocate" card descriptions refreshed to match current wiki state. Footer gained empathy-map and loneliness deep-links. HMW unchanged in the wiki, so no HMW edit. Triggered by team additions to the knowledge base (empathy map, loneliness overview).
- **2026-05-25 (content)** — Added the **"What We Heard"** section (`#field`) between Problem Space and Knowledge, presenting five signals from round 1 field interviews. New `.signal` component (see section 5). Added a "Round 1" past entry to the journey timeline. Hero meta updated "Day 1 · May 19" → "Started 19 May 2026". Header and footer nav gained the new section; footer gained a link to the interview-findings wiki entry. Triggered by upload of the round 1 interview results.
- **2026-05-19 (theme)** — Re-skinned to the **SGLN TECH** theme. Palette moved from warm cream / terracotta to SGLN blue: cool light-blue-grey body, SGLN-blue accent, blue-gradient hero (deep navy → azure, white text), deep-navy header and footer. Added six dark-section variables (`--navy-deep`, `--navy-mid`, `--azure`, `--azure-bright`, `--on-dark`, `--on-dark-soft`, `--on-dark-muted`). HMW grid cells gained a blue top-border; timeline `.step.final` chip is now solid accent; knowledge cards gained a soft blue hover-lift shadow. `index.html` was NOT changed — re-skin is entirely in `style.css`, all class names preserved. Triggered by request to match the SGLN Tech site (sgln.hcli.org/sgln-tech). Note: exact brand hexes could not be extracted from the live site; palette is a faithful interpretation of the SGLN TECH blue-gradient identity and should be reconciled against official brand colors if they become available.
- **2026-05-19** — Initial build. Hero, journey (one past entry + four future), HMW with synthesis, team (5 cards), problem space, knowledge index, rubric. Style.css written from scratch. SPEC.md created. (Original theme: warm cream / terracotta editorial.)

---

## 10. What's NOT in scope

For clarity, things this SPEC deliberately doesn't try to govern, so future edits aren't constrained where they don't need to be:

- Multi-page structure. The site is single-page right now. When content outgrows scroll length (likely around month 3 or 4), split into pages — but that's a bigger redesign and should get a new SPEC entry.
- Internationalization. English only, for now.
- A CMS or build step. Plain HTML and CSS, edited directly. Adding a build step is fine but should be discussed.
- Analytics. Not implemented. If we add it, document the choice and rationale here.
- Forms or interactivity beyond anchor links. The site is a read.

If a future update wants to move outside any of these, that's allowed — but the change should be reflected in the SPEC before the code change ships.
