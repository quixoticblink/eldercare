# site/ — the public microsite

This is the Vercel-deployable microsite. Static HTML, one CSS file, no build step.

## Files

- `index.html` — single-page homepage. Hero, journey timeline, the HMW, team, problem space, knowledge-base index, rubric mapping.
- `style.css` — all styles, editorial / warm / restrained.
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

The microsite is a public-facing summary. The working wiki lives in `../knowledge/`. The site links into wiki entries via relative paths (e.g., `../knowledge/eldercare.md`). On a deployed Vercel site, those links will only resolve if you also include the `knowledge/` folder in deployment — see the project root README for two deployment strategies.

## Updating

Most updates over the six-month sprint will be:

- A new entry in the journey timeline (add a `<div class="entry">` block in `index.html` under `#journey`).
- A new knowledge-base card (add a `<a class="kb-card">` block under `#wiki`).
- A new HMW iteration (update the `.hmw-statement` and `.hmw-grid` cells; link the old one in the wiki).
- A new team member or role change (edit a `.team-card`).

Bigger redesigns will probably want to split `index.html` into multiple pages — `journey.html`, `hmw.html`, etc. — when content outgrows a single scroll. The CSS already supports that.
