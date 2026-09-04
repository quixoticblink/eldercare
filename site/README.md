# site/ — the public microsite

This is the Vercel-deployable microsite. Static HTML, one CSS file, no build step.

## Files

- `index.html` — single-page homepage. Sections in order: Hero, Journey, The Question (HMW chronology), Team, Problem Space, What We Heard (field signals), Empathy Map, Strategy, Knowledge base + rubric.
- `style.css` — all styles. Editorial / restrained, SGLN TECH theme: blue-gradient hero and deep-navy footer bookending a cool-toned light body. Serif display, sans body, one accent color.
- `SPEC.md` — the design spec. Colors, typography, component patterns, update recipes, and the update log. **Read this before making any non-trivial change to `index.html` or `style.css`.**
- `vercel.json` — clean URLs + a couple of security headers.

## Local preview

Open `index.html` directly in a browser — no build needed. Or for a proper local server (so relative links resolve like they would in production):

```bash
cd site
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploy to Vercel

Option 1 — through the Vercel dashboard, drag-and-drop the `site/` folder.

Option 2 — from the command line:

```bash
cd site
npx vercel        # for a preview deploy
npx vercel --prod # for production
```

Option 3 — connect this repo to Vercel and set the **Root Directory** to `site` in project settings. Vercel will auto-deploy on every push.

## How this site relates to the wiki

The microsite is a public-facing summary. The working wiki lives in `../knowledge/`. As of 2026-05-25, every wiki link on the site is an **absolute GitHub URL** (`https://github.com/quixoticblink/eldercare/blob/main/knowledge/...`), not a relative path — that way the links resolve on the deployed Vercel site (Root Directory = `site/`) without needing to bundle the wiki folder into the deployment. Any new wiki link on the site should follow the same scheme. See `SPEC.md` section 9 for the rationale.

The tradeoff: if the GitHub repo ever goes private, public visitors won't be able to follow the links. That's a known and accepted risk for the six-month sprint window.

## Updating

Most updates over the six-month sprint will be:

- A new entry in the journey timeline (add a `<div class="entry">` block in `index.html` under `#journey`). See SPEC Recipe 1.
- A new knowledge-base card (add an `<a class="kb-card">` block under `#wiki`). See SPEC Recipe 3.
- A new HMW iteration (add a step to the `.hmw-history` chronology and update the `.hmw-statement` + `.hmw-grid` cells to the new current). See SPEC Recipe 2.
- A new team member or role change (edit a `.team-card`). See SPEC Recipe 4.
- Activating a dormant knowledge card (remove the `.dormant` class). See SPEC Recipe 5. As of 2026-07-11 there are **no dormant cards left** — strategy was activated in the reframe pass, prototype and pitch in a second pass the same day. Keep the recipe for the next folder that gets added.

Anything bigger — a new top-level section, a new component, a palette extension — should start with a SPEC change, not a code change. SPEC section 9 has the pattern.

Bigger redesigns will probably want to split `index.html` into multiple pages — `journey.html`, `hmw.html`, etc. — when content outgrows a single scroll. Likely around month 3 or 4. The CSS already supports that.
