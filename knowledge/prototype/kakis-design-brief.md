---
title: "Kakis prototype — design brief and research synthesis"
status: draft
last_updated: 2026-07-11
based_on: [interview-round-1-findings, ncss-idi-findings, vanguard-operational-data, marsiling-aac-grab-interviews, consistency-as-design-constraint, hmw-2026-07-08-post-vanguard, respite-marketplace-concept]
---

ok so this is the bridge document between the evidence base and the first prototype. Every screen in `kakis-prototype.html` should trace back to a finding here, and every finding here traces back to an evidence file. The working name is **Kakis** — Singlish for trusted companions — provisional until the team votes.

## What the prototype has to prove

The rubric line is *human centricity, feasibility, viability, desirability*. Concretely, the prototype demonstrates the three-sided loop of the crisis-activation respite platform layered on Vanguard's Pasir Ris ICCP pilot:

1. **Respite giver** onboards, picks task skills, completes the Vanguard-certified training path (CPR at St. Luke's, mobility, dementia basics), and receives tiered certification before any job is offered.
2. **Caregiver** activates trusted respite — crisis-first (six named triggers) or planned — and gets matched with consistency preserved and the multi-payer price stack visible.
3. **Admin** runs the operation through agents — onboarding verification, matching tuning, quality review — approving recommendations rather than doing manual work. The thesis: Vanguard's phone-triage + WhatsApp-roster pattern works at 20–30 bookings/month; agents are how it survives 200+.

## Research synthesis → design requirements

**Method:** synthesis of 6 team field interviews (May 2026), NCSS IDIs (~20–30 respondents, late 2025, second-hand), Vanguard operational data (Jul 2026), and 14 Grab Marsiling AAC interviews (second-hand).

| # | Finding (source) | Design requirement in the prototype |
|---|---|---|
| R1 | Seniors *repel* new helpers; months to adjust (NCSS IDI 1; round-1 signal 05) | Sticky matching: "your kaki" regulars surface first; new matches labelled with the pre-relationship step; matching agent optimises a consistency score, not just speed |
| R2 | First-session-with-staff is Vanguard's operational answer (vanguard-operational-data) | Every first visit to a new senior is paired with a Vanguard care staff — shown in both caregiver match result and respite-giver job card |
| R3 | Crisis activation is the wedge — six triggers (hmw-2026-07-08) | The request flow leads with "What happened?" — six tactile trigger cards; planned booking is secondary |
| R4 | Willingness-to-pay broken; multi-payer stack required (vanguard pricing: $10–12 pay / ~$26 cost / $25–35 charge) | Price breakdown shows the stack: base rate minus subsidy minus fund contribution = caregiver pays. Nothing hidden |
| R5 | MOH/AIC hesitancy on rating/ranking care staff (devils-advocate 14) | **No public star ratings anywhere.** Post-visit feedback is a private care note routed to the quality agent; admin sees themes, not leaderboards |
| R6 | Caregiver is the buyer, not the senior (Marsiling; grab sizing) | The booking UI is the caregiver's phone. The senior never has to install anything |
| R7 | Dialect-only speakers, vision limits (Marsiling; round-1 signal 03) | Language matching is a first-class booking field (incl. Hokkien, Teochew, Tamil); large type, high contrast throughout |
| R8 | Contribution beats charity; micro-jobbers are early-60s retirees motivated by structure (round-1 signal 04; Vanguard supply profile) | Respite-giver onboarding is framed as contribution and community standing, not gig hustle; earnings shown honestly at $10–12/hr with free training |
| R9 | Certification is the moat, tiered by task (marketplace-2x2; Luce) | Skill tiers gate job categories — chaperone unlocks at Tier 1, medicine administration stays locked until certified. Locked states are visible, not hidden |
| R10 | Manual ops don't scale linearly (community-chaperone) | Admin console is agent-first: agents verify, match, and digest; the human approves exceptions. Every agent action shows its evidence trail |

## Visual direction

Not the AI-default cream-and-terracotta. The subject's world is Singapore's green civic identity plus kopitiam warmth: deep **pandan green** (#14594A) as primary, **marigold** (#F0A63C) reserved for the activation moments (crisis CTA, match found), porcelain-green paper (#F2F4EF), clay red only for genuine alerts. Type: **Fraunces** display (warm, human, institutional-but-not-corporate), **Instrument Sans** body, **Spline Sans Mono** for certification IDs, timestamps, and agent logs — the "receipts" texture the wiki itself favours.

Signature element: the **six-trigger crisis picker** — the strategy made tactile. One aesthetic risk: the matched-kaki card is styled as a physical "kaki pass" the caregiver can show the senior, acknowledging that trust transfers through artifacts, not apps, for this cohort.

## What the prototype does not claim

- No real matching algorithm — the weights panel simulates tuning.
- No real payments, MOM checks, or St. Luke's registry integration.
- The senior-facing surface is deliberately out of scope (R6); a future iteration should test a print/voice artifact for the senior.
- Agent behaviours are scripted; the point is the *operating model*, not the model.
