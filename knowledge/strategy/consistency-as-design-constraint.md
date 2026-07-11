---
title: "Consistency as design constraint"
aliases: [consistency constraint, months-to-adjust finding, senior helper consistency]
status: draft
last_updated: 2026-07-11
based_on: [interview-round-1-findings, ncss-idi-findings, vanguard-operational-data, 2026-07-08-vanguard-visit]
---

ok so this is the single load-bearing constraint that cuts across every solution design we've considered. It has been referenced in seven separate entries since May, always as *"see consistency-as-design-constraint (proposed)"* — writing the entry properly is overdue. The short version: **elderly people don't just prefer consistency in their helpers; they actively repel new faces at first contact, and adjustment takes months, not days.** Any answer that puts a new stranger in front of a senior on demand fails at the first appointment.

The name matters. It is not *"consistency is a nice-to-have."* It is a *design constraint* — a hard fact about the problem space that rules out a specific class of solutions before you build them.

## Where the finding comes from

Three independent evidence streams converged on the same claim:

**Round 1 field interviews (May 2026).** Signal 05 in [[../evidence/interview-round-1-findings]] — *"consistency is the product; transient help doesn't count."* Delivered most cleanly by the caregiver of a grandmother with dementia in [[../humans/2026-05-22-caregiver-dementia-grandmother]] — *"consistency is the most important thing in whatever solutions"* — and reinforced by the frontline caretaker at Lee Ah Mooi Old Age Home ([[../humans/2026-05-25-frontline-caretaker-old-age-home]]) describing volunteers who *"come for a limited period and go away."* The transient-volunteer thank-you board photo ([[../images/README]] IMG_9546) captures the failure mode: three years of well-meaning corporate CSR moments, none of which sustained a relationship.

**NCSS's late-2025 IDIs.** Documented in [[../evidence/ncss-idi-findings]] Finding 1. NCSS's exact language on the 2026-06-15 call: *"Seniors actually like consistency… when it comes to ad hoc, they actually repel every single time the new person comes because it takes them like months to get used to the person."* This is stronger than *"prefer familiar"* — "repel" is active rejection at first contact.

**Vanguard's own operational pattern (2026-07-08).** Vanguard's phone-triage → first-session-always-with-Vanguard-staff → subsequent-with-micro-worker pattern (see [[../landscape/vanguard]] and [[../landscape/community-chaperone]]) is Vanguard's *partial operational answer* to the same constraint. The first face a senior sees is a Vanguard-employed staff member — someone the senior has already met at the centre — not a stranger from a marketplace pool. Vanguard developed this pattern experientially without necessarily framing it as a solution to the consistency problem. But it is.

## The two sharp edges

**The months-to-adjust timeline.** If it takes months to adjust to a new helper, then a rotation-friendly marketplace (Uber-style assignment to whichever driver is nearest) has a broken time horizon. Marketplace supply that cycles weekly or monthly is failing the constraint before it starts. The economics of a marketplace *want* rotation — it lets supply scale independently of specific relationships. The end-user constraint *forbids* rotation — the relationship *is* the product. That's a real tension, not a wave-away.

**Active rejection at first contact.** *Repel* is different from *dislike.* If the senior actively pushes away when a stranger arrives, the first booking fails and there's no second booking. That's not a UX problem you fix with better onboarding. It's a fundamental constraint on how you introduce new supply into a senior's life.

## What this rules out

- **Pure on-demand dispatch models** ([[marketplace-2x2]] archetype 3). Uber-style "whichever helper is nearest" is exactly what the constraint rules out. This is why the [[../journal/2026-06-25-solutioning]] session settled on archetype 4 (managed marketplace) rather than 3.
- **Rating and review UX where the senior picks a stranger from a list.** Even if the senior is theoretically empowered, the *repel at first contact* dynamic doesn't discriminate between assigned strangers and self-chosen strangers.
- **Ad-hoc pool models where the platform matches without prior relationship.** Any marketplace where the first appointment is the first meeting will fail. There must be a pre-relationship layer — an introduction, a shadow session, a familiarity-building step.
- **AI companionship for anyone lucid.** Related but distinct — [[../evidence/interview-round-1-findings]] Signal 02 (the "AI half-life"). The mechanism is different (users detect patterns) but the failure mode is similar (novelty wears off, disengagement follows).

## What this shape-constrains

Solutions that survive the constraint have to include one or more of:

**A pre-relationship layer.** Senior meets the helper before the first "real" appointment. Could be through the AAC, a community touchpoint, or a shadow visit. Vanguard's first-session-with-staff pattern is this. Adds cost and time to onboarding.

**Long-lived matches.** The helper the senior meets on visit 1 is the same helper on visits 2–20. Not "whichever certified provider is available" — "your helper is Mary, and she's coming Tuesday." This is closer to insurance-panel matching than gig-economy matching.

**Repeatable identity signals.** The senior doesn't need to remember every helper's face — but the *branding* of the service, the way the helper introduces themselves, the uniform, the language should be consistent enough that even if the person is new, the *pattern* is familiar. Vanguard uses uniform + centre affiliation for this.

**Institutional continuity as a substitute for personal continuity.** If specific-person consistency isn't achievable, then a consistent *institution* — "someone from the RC centre / from Care Corner / from Vanguard" — is a partial substitute. It's the second-best answer when the first-best isn't affordable.

## The economic problem this creates

Consistency is expensive. Long-lived matches mean the helper can't be shared efficiently across households. A pre-relationship layer means every new senior costs the platform a *shadow* session before the paid work begins. Institutional continuity requires paying for the institution's overhead.

This is one of the two reasons the [[../strategy/respite-marketplace-concept]] concept moved toward a *multi-payer stack* — private pay alone can't fund consistency at market rates. The other reason is willingness-to-pay is broken at the senior-facing layer.

It's also why Aditi's "bleeding money" caution about managed marketplaces ([[../landscape/urban-company]]) is more acute for eldercare than for household services. A managed marketplace for cleaners can rotate supply freely. A managed marketplace for elder-care can't.

## Where the constraint bends but doesn't break

**Crisis activation** (the wedge in [[../reframing/hmw-2026-07-08-post-vanguard]]) may partially escape the constraint. When a caregiver is in a crisis (helper runaway, spouse hospitalisation), the willingness to accept a new face is temporarily elevated — the alternative is *no help at all*. But the elevated tolerance is transient; a service that shows up in the crisis and then rotates in a stranger next week will hit the constraint on booking two.

**Task categories with low intimacy** (chaperone escort to a clinic; food pickup) may tolerate more rotation than task categories with high intimacy (personal care, in-home night respite). The constraint isn't uniform across the [[../strategy/respite-marketplace-concept]] task grid.

**Institutional consistency substitutes.** If the senior can't have Mary specifically, but "someone from the Care Corner AAC" is close enough, the constraint is partially satisfied by the brand rather than the person.

## What confused us / pitfalls

- **NCSS said "months to adjust."** That's a strong specific claim. If it's directional from a handful of interviews it's very different from something measured with a scale. Worth pulling the source study if we quote the number.
- **The consistency finding is likely dose-dependent on cognitive status.** A senior with mild cognitive impairment or early dementia may need much longer adjustment than a fully lucid senior. The "months" figure may hide a wide distribution. Confirmed anecdotally by the [[../humans/2026-05-22-caregiver-dementia-grandmother]] note but not statistically.
- **We don't know how consistency degrades over time.** Does Mary-for-six-months build durable connection, or does the senior go back to *repel-at-first-contact* if Mary is away for two weeks? Nobody has told us.
- **The finding may be culturally specific.** All our evidence is Singapore-Asian. Whether the pattern generalises to other Asian cultures or to Western contexts is genuinely unclear.

## Connects to

[[../evidence/interview-round-1-findings]] Signal 05 is the round 1 anchor. [[../evidence/ncss-idi-findings]] Finding 1 is the NCSS validation with the "repel" and "months" language. [[../landscape/vanguard]] and [[../landscape/community-chaperone]] carry Vanguard's operational partial answer. [[../landscape/luce-sg]] is the live commercial competitor operating in the same constraint space — how they handle it (or fail to) is a live open question we've flagged for the Luce mystery-shop follow-up. [[../reframing/hmw-2026-07-08-post-vanguard]] is the HMW that must accommodate this constraint. [[marketplace-2x2]] rules out archetype 3 in part because of this. [[respite-marketplace-concept]] designs around it. [[../reframing/devils-advocate]] critique 6 (AI half-life) is the related-but-distinct constraint for the AI-companion path. [[../humans/2026-05-22-caregiver-dementia-grandmother]] and [[../humans/2026-05-25-frontline-caretaker-old-age-home]] are the original round-1 sources.

## Proposed sibling / child entries

- [[institutional-continuity-as-consistency-substitute]] — the "Care Corner branding replaces personal recognition" argument, written up separately.
- [[pre-relationship-onboarding-layer]] — what a first-session-with-staff pattern looks like at marketplace scale.
- [[consistency-vs-crisis-activation-tension]] — how the crisis-activation wedge partially escapes the constraint (and where it doesn't).
