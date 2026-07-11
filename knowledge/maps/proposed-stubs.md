---
title: "Proposed stubs — dangling wiki-links registry"
status: live
last_updated: 2026-07-11
---

Registry of concept entries that are referenced by name (`[[double-bracket links]]`) across the wiki but don't yet have their own file. The dangling-link pattern is deliberate — VOICE.md encourages linking to entries that don't exist yet, because the dangling link IS the growth plan.

This map ranks the dangling links by rough inbound-link count so the next writing session can target the highest-leverage stubs first.

## Method

Not a mechanical scrape (I could produce that via `grep -oE '\[\[[^]]+\]\]'` but the raw count is noisy). This is a curated ranking based on which stubs are actually load-bearing across recent strategy, HMW, and landscape work.

## Tier 1 — write next (referenced 4+ times, load-bearing)

- **[[multi-payer-stack]]** — the funding-model insight (private pay + healthcare fund + philanthropic capital + corporate hotel partners + potential enterprise-benefit). Referenced in [[../strategy/respite-marketplace-concept]], [[../reframing/hmw-2026-07-08-post-vanguard]], [[../landscape/vanguard]], and elsewhere. Deserves its own strategy entry — it's the answer to "how does the commercial model close given broken senior-facing willingness-to-pay."
- **[[crisis-activation-wedge]]** — the six trigger scenarios (helper runaway, spousal-couple emergency, discharge scramble, sudden decline, grief, caregiver's own emergency). Referenced across strategy, HMW, and journal entries. Deserves its own strategy entry — right now it's a bulleted list in [[../reframing/hmw-2026-07-08-post-vanguard]].
- **[[gig-vs-employee-supply-model]]** — the labor-model question deferred to Vanguard and now partially answered. Referenced in [[../strategy/marketplace-2x2]], [[../reframing/hmw-2026-06-25-caregiver-respite]], [[../landscape/vanguard]]. Deserves a strategy entry once the answer stabilises.

## Tier 2 — write soon (referenced 3–4 times, useful)

- **[[phv-population-health-visit]]** — AIC's ~3-page in-home survey framework. Referenced in [[../landscape/aic]], [[../landscape/vanguard]], [[../evidence/vanguard-operational-data]]. Deserves an evidence entry — it's the instrument behind several stats we quote.
- **[[met-medical-escort-transport]]** — the government-subsidised medical-escort programme that inspired Community Chaperone. Referenced in [[../landscape/community-chaperone]], [[../landscape/luce-sg]], and elsewhere. Deserves a landscape entry.
- **[[iccp-integration-design]]** — what an activation layer on top of Vanguard's ICCP platform actually looks like. Referenced in [[../strategy/respite-marketplace-concept]], [[../reframing/hmw-2026-07-08-post-vanguard]]. Deserves a strategy entry once the pilot scope is sharper.
- **[[homeage]]** — commercial competitor, named by NCSS. Referenced in [[../landscape/luce-sg]], [[../landscape/ncss]], and elsewhere. Deserves a landscape entry.
- **[[jagami]]** — commercial competitor, named by NCSS. Referenced similarly to Homeage. Deserves a landscape entry.

## Tier 3 — write when time permits (referenced 1–3 times)

- **[[assignment-vs-choice-in-eldercare-marketplaces]]** — the matching-control UX question. Referenced in [[../strategy/marketplace-2x2]], [[../strategy/respite-marketplace-concept]].
- **[[unit-economics-of-managed-marketplaces]]** — Aditi's "bleeding money" caution written up. Referenced in [[../strategy/marketplace-2x2]], [[../landscape/urban-company]].
- **[[care-corner-meeting]]** — placeholder for the divide-and-conquer follow-up meeting. Referenced in [[../landscape/care-corner]] and [[../landscape/ncss]].
- **[[caring-sg]]** — the NCSS-validated SSA. Referenced in [[../landscape/ncss]].
- **[[cal-caregiver-alliance]]** — the third NCSS-validated SSA. Referenced in [[../landscape/ncss]] and [[../landscape/vanguard]].
- **[[chaperone-supply-model]]** — paid vs volunteer vs job-redesigned older workers. Referenced in [[../landscape/community-chaperone]].
- **[[night-respite-vanguard]]** — the parallel Vanguard pilot to Community Chaperone. Referenced in [[../landscape/vanguard]], [[../landscape/community-chaperone]].
- **[[woodlands-active-ageing-centre]]** — the site of a planned Vanguard visit. Referenced in [[../landscape/vanguard]].
- **[[moh-holdings]]** — Vanguard's parent org. Referenced in [[../landscape/vanguard]].
- **[[demographic-transition]]** — the global aging picture. Referenced in [[../evidence/elderly-population-stat]] and elsewhere.
- **[[ageing-in-japan-and-korea]]** — comparative reference. Referenced in [[../evidence/elderly-population-stat]].
- **[[singapore-old-age-support-ratio]]** — macro accounting figure. Referenced in [[../evidence/elderly-population-stat]].
- **[[the-80-plus-surge]]** — the fastest-growing cohort. Referenced in [[../evidence/elderly-population-stat]].
- **[[loneliness-prevalence-singapore]]** — the missing rate estimate. Referenced in [[../evidence/elderly-population-stat]].

## Tier 4 — write as needed

Concept-of-a-concept entries that may or may not need to exist depending on how the work evolves:

- **[[elderly-loneliness]]** — factoring out the specific phenomenon.
- **[[companionship-vs-care]]** — the conceptual distinction.
- **[[caregiver-burnout]]** — the parallel problem.
- **[[quality-of-care-training]]** — a specific NCSS thread.
- **[[physical-activeness-for-seniors]]** — a thread that may or may not become a concept entry.
- **[[digital-inclusion-singapore-elderly]]** — the digital-exclusion mechanism.
- **[[elderly-mobility-and-safety]]** — the mobility thread.
- **[[reminiscence-therapy]]** — Memory Lane / Oak Care territory.
- **[[oak-care]]** — the caregiver-support startup NCSS referenced.
- **[[memory-lane]]** — reminiscence-therapy startup.
- **[[grabcare-postmortem]]** — the earlier failed NCSS-Grab attempt.
- **[[silver-zones]]** — traffic safety zones for elderly.
- **[[social-changemaker-series]]** — NCSS's convening format.
- **[[free-medical-escorts-programme]]** — the giving.sg campaign named in Luce research.
- **[[health-social-integration-singapore]]** — the AIC/NCSS convergence.
- **[[transient-volunteer-pattern]]** — the failure mode Lee Ah Mooi's board illustrates.
- **[[private-old-age-homes-singapore]]** — the long tail of small facilities like Lee Ah Mooi.
- **[[institutional-continuity-as-consistency-substitute]]** — from [[../strategy/consistency-as-design-constraint]].
- **[[pre-relationship-onboarding-layer]]** — from [[../strategy/consistency-as-design-constraint]].
- **[[consistency-vs-crisis-activation-tension]]** — from [[../strategy/consistency-as-design-constraint]].
- **[[commercial-eldercare-marketplace-comparison]]** — proper side-by-side of Luce, Homage, Jagami.
- **[[luce-mystery-shop]]** — placeholder for the actual booking experience.
- **[[national-silver-academy]]** — SUSS-adjacent lifelong-learning programme.
- **[[singapore-ageing-events-calendar]]** — running list of GIF-like venues.
- **[[theory-of-change-connection-to-community]]** — the middle step our May 19 HMW asserted but never justified.

## The prompt-file leftover

The extension-less file `evidence/elderly-population-stat` was the original filled-in "Write Prompt 1" used to seed the population-stats entry. It's not a wiki entry — it's a leftover artifact. On 2026-07-11 it was moved to `.stale/` alongside `Untitled.rtf` for eventual local deletion.

## The `-2` suffix files

Two entries carry an awkward `-2` suffix because they were team-authored alongside earlier same-named files that got superseded:

- **`humans/empathy-map-2.md`** — the canonical empathy map. Preferred name would be `empathy-map-elderly.md`. Kept as-is because the deployed site's GitHub links reference this exact filename.
- **`evidence/singapore-eldery-stats-2.md`** — the canonical Singapore stats entry. Preferred name would be `singapore-elderly-loneliness.md` (and the typo would be fixed). Kept as-is for the same reason.

The superseded originals (`humans/empathy-elderly.md`, `evidence/loneliness.md`) carry supersession headers and should not be linked to from new work.

Rename these at the next site update — that pass has to update GitHub URLs anyway.

## Related maps

- [[README]] — index.
- [[rubric-and-folders]] — how the tier-1 stubs unblock rubric-facing gaps.
- [[hmw-evolution]] — where several of these stubs surfaced in the HMW journey.
- [[../VOICE]] — the dangling-link convention (this file is its formal registry).
