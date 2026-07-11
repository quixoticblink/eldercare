---
title: "Marketplace 2×2 — control axes for platform positioning"
aliases: [platform 2x2, marketplace matrix]
status: draft
last_updated: 2026-06-25
based_on: 2026-06-25-solutioning
---

ok so this is a framework, not a decision. Abhishek pulled it together during the [[../journal/2026-06-25-solutioning]] session to give the team a way to argue about the marketplace shape without talking past each other. Once the axes were on the whiteboard the debate collapsed to a specific quadrant in about ten minutes. Useful pattern; worth writing down.

## The two axes

Every marketplace platform sits somewhere in a plane defined by two orthogonal choices:

**Matching control** — does the *customer* pick the specific supplier, or does the *platform* assign one?
- Amazon lets you browse and choose a seller.
- Uber hands you a driver.
- Fiverr shows you gigs; you pick.
- DoorDash assigns a courier.

**Management / integration depth** — how much does the platform *do* on the supply side?
- Listing-only platforms just publish supply; supply self-onboards, sets prices, handles delivery.
- Managed platforms vet, train, price, standardise, and sometimes supply tools to supply.
- Integrated platforms *own* the supply outright — the "marketplace" becomes a retailer with a directory front-end.

## The five archetypes along the plane

Roughly, most real platforms land in one of five spots:

1. **Open / listings marketplace** — supply self-onboards, sets prices, customer picks. Amazon 3P, eBay, Etsy. Trust and payments come from the platform; almost nothing else does. Supply is *differentiated* — one seller is not fungible with another, so the buyer has to choose.

2. **Curated / freelance marketplace** — customer still picks, but the platform shapes how supply is packaged. Standardised gigs, profiles, ratings, escrow, light vetting. Fiverr, Upwork, Airbnb. Fiverr sits a notch further right than Upwork because it *forces* sellers into productized formats.

3. **On-demand dispatch** — the defining shift: the customer no longer picks. Because supply is *fungible* — one ride ≈ another — the platform can algorithmically assign and set price (including surge). Vetting exists but the platform stays asset-light — drivers own the cars. Uber, Lyft, DoorDash.

4. **Managed marketplace** — platform-led matching PLUS deep supply management. Vets and trains providers, sets price, defines service protocol and quality standards, sometimes supplies tools. The supplier is a controlled extension of the platform without being employed by it. **Urban Company / UrbanClap.** Parts of Thumbtack, Instacart. This is where our current thinking sits.

5. **Owned / integrated** — the platform owns the inventory or employs the providers outright. Stops being a marketplace and becomes a vertically integrated retailer or operator. Amazon Retail (1P/FBA), cloud kitchens, hotel management chains.

## Where we land

The [[../journal/2026-06-25-solutioning]] session settled on **archetype 4 — managed marketplace** — for the eldercare-respite platform.

Two reasons.

**The trust constraint requires vetting.** *Take my elderly to the clinic* is not fungible-taxi work; it's a labor category the customer needs to trust before the transaction happens. Certification, training, and standardised service protocol have to be present or the platform fails at the trust layer. That rules out archetypes 1 and 2.

**The consistency constraint plus the small-market size makes assignment plausible.** NCSS's own IDIs say seniors need months to adjust to a new helper ([[../evidence/ncss-idi-findings]]). If the platform lets customers pick every time, you get high match churn. If the platform can *assign consistently* — same helper every time for a given caregiver-senior pair — you can partially solve the consistency problem at the platform level. That pushes toward on-demand dispatch mechanics, but with the vetting depth of a managed marketplace on top.

Zheng Wei anchored the call: *"controlled and curated over open."* Aditi held the open question: *what does 'own and manage the supply' actually mean* — gig workers or salaried employees? That is deferred to Vanguard ([[../landscape/vanguard]]).

## Where the axes stay open

Two things are *not* settled by the 2×2:

**Assignment vs choice.** We start at "platform assigns," but for repeat customers or for senior-specific matching, letting the customer choose (or lock in a specific helper) is probably necessary. The 2×2 tells us we can start left-of-Amazon and move right as we learn. Not committed.

**Depth of ownership.** Managed-marketplace archetype 4 does *not* imply we employ the workforce. Urban Company sets protocols but doesn't put helpers on payroll; Vanguard's Community Chaperone has a mix of salaried staff and micro-jobbers. The right depth is a labor-model question that intersects Singapore's employment classification framework. See [[gig-vs-employee-supply-model]] (proposed).

## What confused me / pitfalls

The 2×2 is descriptive, not prescriptive. Real platforms drift between quadrants and often run different services at different quadrants inside the same brand. Grab is on-demand dispatch for rides, managed for GrabPay, integrated for GrabPay-adjacent lending. Don't over-fit our platform to one quadrant.

"Managed marketplace" sounds like the safest quadrant because it names control and quality. It's also the *most expensive* quadrant — Urban Company burns money on ops for a reason. Aditi flagged this: *"if there's not enough demand, and you're running something like a managed marketplace, then you're just bleeding money."* The 2×2 doesn't score for unit economics; you have to apply that separately.

Archetype 3 (on-demand dispatch) *only* works when supply is genuinely fungible. Ours isn't — a Chinese-speaking chaperone matched to a Mandarin-only senior is not interchangeable with a Malay-speaking one. Any assignment logic has to price fungibility carefully.

## Connects to

[[respite-marketplace-concept]] is the working solution this framework informed. [[../reframing/hmw-2026-06-25-caregiver-respite]] is the HMW it points at. [[../journal/2026-06-25-solutioning]] is the session where it took shape. [[../landscape/urban-company]] is the closest existing analog (archetype 4). [[../landscape/snabbit]] is a hyper-local variant that leans toward archetype 3. [[../landscape/vanguard]] is where the "supply management depth" question gets validated.

## Proposed sibling / child entries

- [[gig-vs-employee-supply-model]] — the labor-model question the 2×2 defers.
- [[assignment-vs-choice-in-eldercare-marketplaces]] — the matching-control axis when trust and consistency are load-bearing.
- [[unit-economics-of-managed-marketplaces]] — Aditi's "bleeding money" caution written up.
