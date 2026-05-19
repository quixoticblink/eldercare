# Microsite spec — design guidelines, flow, update recipes

**Purpose.** Hand this file to any future collaborator (human or AI) along with your "please update the site to add X" request. The spec is what keeps the site looking like itself across edits. If something here is ambiguous, the existing `index.html` is the authority — match its patterns.

**How to use this with an AI.** Paste this entire file, then add your specific ask. Example: *"Using the SPEC.md attached, add a new journey timeline entry for 2026-05-26 covering empathy-map work."* The AI then has the design rules, current section flow, and update recipe in one shot.

---

## 1. Design principles

We are aiming for *editorial / warm / restrained*. Reference points: Stripe Press, Vercel's marketing pages, Mercury's writing pages, Anthropic.com. The site should feel like a thoughtful magazine, not a SaaS landing page.

What we want:

- **Serif headings, sans-serif body.** EB Garamond for display, Inter for body. Mono only for labels and metadata.
- **Generous whitespace.** Sections are tall (5rem padding top and bottom). Body copy is narrow (about 38rem / 60ch).
- **Warm cream background.** Not pure white. Not gray. Warm.
- **One accent color.** A terracotta orange (`#B85C38`). Used sparingly — for the question itself, for hover states, for the dot on hero meta, for emphasis inside `<em>` tags. Never as a background of a full section.
- **Italics carry intellectual weight.** The lede paragraph is italic. The HMW statement is italic. Single-word emphasis inside paragraphs uses `<em>`. Don't bold-emphasize prose.

What we avoid:

- Drop shadows beyond the most subtle. The whole thing should feel like printed paper, not floating cards.
- Gradient backgrounds. Cream is the only background.
- Stock photography. The site is text-driven and the typography does the work.
- Emoji. Anywhere.
- Capitalization games. No ALL CAPS HEADLINES. Sentence case for everything except eyebrow labels (which are mono uppercase as a deliberate visual rhythm shift).
- Animations beyond the most subtle 120ms transitions on hover states.
- More than one accent color. Don't add green, blue, or pink anywhere.

---

## 2. Color palette

All defined as CSS custom properties in `style.css` under `:root`. Use the variable, never the hex. If you find yourself wanting a color that isn't defined, propose adding it to the palette in the SPEC update log (section 9) first.

```
--bg          #FAF7F0  Warm cream, page background
--bg-elev     #FFFFFF  Card surfaces (team, knowledge cards)
--bg-warm     #F5EFE2  Slightly darker warm cream (footer, rubric cards, timeline step chips)
--text        #1F2937  Primary text
--text-soft   #4B5563  Secondary text, descriptions
--text-muted  #8B8578  Tertiary text, eyebrow labels, dates
--accent      #B85C38  Terracotta — the one accent color
--accent-soft #E8D4C4  Faded accent for borders and selection
--accent-bg   #FBF1E8  Tinted background for HMW statement
--border      #E7E2D6  Standard card/section border
--border-soft #EFEBE0  Subtler border for chips and tertiary surfaces
--rule        #D4CDB8  Horizontal rules, timeline spine
```

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

The site is a single scrolling page. Anchor links (`#journey`, `#hmw`, etc.) drive in-page navigation from the sticky header. The header is a translucent strip with backdrop blur — it stays at the top, brand on the left, nav on the right.

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
2. **Journey.** The narrative arc. Currently a timeline from May 19 to Demo Day, with past entries in accent and future entries muted.
3. **The Question.** The HMW statement, the three-cell grid, the "How we got here" explanation, the honest-about-shortcomings callout.
4. **Team.** Five cards with initials, names, and lenses.
5. **Problem Space.** Three paragraphs of observation-first framing, ending with a link to the wiki overview.
6. **How We Work / Knowledge.** The wiki structure as cards, plus the four-part rubric mapping.
7. **Footer.** Project description, navigation links, colophon.

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

- **2026-05-19** — Initial build. Hero, journey (one past entry + four future), HMW with synthesis, team (5 cards), problem space, knowledge index, rubric. Style.css written from scratch. SPEC.md created.

---

## 10. What's NOT in scope

For clarity, things this SPEC deliberately doesn't try to govern, so future edits aren't constrained where they don't need to be:

- Multi-page structure. The site is single-page right now. When content outgrows scroll length (likely around month 3 or 4), split into pages — but that's a bigger redesign and should get a new SPEC entry.
- Internationalization. English only, for now.
- A CMS or build step. Plain HTML and CSS, edited directly. Adding a build step is fine but should be discussed.
- Analytics. Not implemented. If we add it, document the choice and rationale here.
- Forms or interactivity beyond anchor links. The site is a read.

If a future update wants to move outside any of these, that's allowed — but the change should be reflected in the SPEC before the code change ships.
