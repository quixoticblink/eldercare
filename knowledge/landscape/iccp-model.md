---
title: "ICCP — Integrated Community Care Programme (85 sub-regions)"
aliases: [ICCP, integrated community care, 85 sub-regions, sub-region model]
status: draft
last_updated: 2026-07-08
---

The ICCP model is MOH's operating framework for how eldercare gets delivered across Singapore. In one sentence: **Singapore is divided into 85 sub-regions and every senior in every sub-region is meant to have local access to the full care continuum — active ageing centres, senior care centres, home care, and referral into higher-acuity nursing.** Operators like [[vanguard]] are assigned to specific sub-regions rather than serving nationwide. If we build a caregiver-respite pilot, it will sit inside this framework — that was the message from the 2026-07-08 Vanguard meeting.

## The framework

**Basis:** MOH reorganised the healthcare landscape into 85 sub-regions based on URA (Urban Redevelopment Authority) planning zones. The number reflects a granularity that maps to real neighbourhood boundaries — walking distance, transit lines, community centres.

**Service allocation per sub-region:** Each sub-region is planned to have:

- Home care services
- Senior care centres
- Active ageing centres

The continuum is meant to keep seniors well **upstream** (preventive; AAC-based social and activity work) and to catch them **downstream** (when care needs rise; SCC, home care, or nursing home).

**Goal — aging in place:** The sub-region model drives Singapore's national strategy of helping seniors age in their own homes and communities, reducing dependence on hospitals and institutional nursing homes.

**Data-driven allocation:** MOH uses population data — distribution, service utilisation patterns, projected demand — to decide which facility types go in which sub-region.

**Operator alignment:** Operators are assigned to specific sub-regions or locations rather than serving nationwide. Vanguard, for example, is the operator for Pasir Ris (one of the two Pasir Ris sub-regions, with ~15,000 seniors). This is the ICCP contract structure.

## Why this matters for our HMW

The ICCP framework is what makes the [[../reframing/hmw-2026-07-08-post-vanguard]] specifically local. When Angeline offered *"we can layer this onto the existing ICCP platform in Pasir Ris,"* she was pointing at:

- **A supply pool already assigned to a geography.** The ~19–20 micro-workers per centre in Pasir Ris are ICCP-attached; they can't just be reassigned to other sub-regions.
- **A demand pool with defined boundaries.** The 15,000 seniors in Pasir Ris are the addressable population for our pilot, not "1 million Singaporeans."
- **A referral pathway that already exists.** Discharge cases from Sengkang Hospital (which serves Pasir Ris) already flow into Vanguard's Pasir Ris operation. We can plug in without building the routing layer.
- **A funding envelope MOH has already committed.** Whatever the Pasir Ris ICCP pilot budget is, that's the money in the room.

The tradeoff: **scaling to a second sub-region isn't a marketing exercise, it's a policy exercise.** Each sub-region has its own operator, its own referral flow, and its own funding envelope. A successful Pasir Ris pilot doesn't automatically deploy to Ang Mo Kio; MOH has to want it to.

## The care taxonomy the framework depends on

Each sub-region gets some mix of the five care types. Full taxonomy in [[singapore-care-taxonomy]], but briefly:

- **Active Ageing Centres (AAC)** — well/robust seniors, preventive.
- **Senior Care Centres (SCC)** — mobility, dementia, rehab; day model.
- **Assisted Living** — HDB flat ownership with wraparound care.
- **Home Care Services** — in-home care + sensor tech.
- **Nursing Homes** — last-resort high-acuity institutional care.

## Sub-region examples

From the Vanguard meeting:

- **Pasir Ris** — two sub-regions; Vanguard runs one. ~15,000 seniors in that sub-region. Not extreme in either direction demographically — used as a representative example.
- **Ang Mo Kio** and **Toa Payoh** — described as having a much older demographic profile. These are the *harder* sub-regions.
- Ministry allocates operators and facility types with the demographic profile in mind.

## Where AIC fits under ICCP

Under the old model, referrals from hospitals went to [[aic]] centrally, and AIC routed them out to operators. Under ICCP, referrals flow **directly from healthcare institutions to the sub-region provider** — AIC is partially disintermediated in routing terms, but still holds the underlying data and administers the funding.

This is a signal: MOH wants shorter referral chains. Any tech layer we build should follow that direction (sub-region-native routing) rather than build a national aggregator (which would be swimming against the current).

## What confused us / open questions

- **Which 85 sub-regions map to which URA planning zones?** We haven't seen the map. Angeline offered to share the sub-region breakdown — worth chasing.
- **How does the framework handle cross-sub-region flows?** Seniors move; caregivers commute. What happens when demand originates outside your sub-region?
- **How rigidly is operator-to-sub-region matching enforced?** Can a Vanguard micro-worker take a job in the next sub-region over? Zheng Wei's fungibility question from [[../journal/2026-07-07-vanguard-prep]] lands here.
- **How does ICCP relate to the health-social integration push?** NCSS (social) and AIC (health) are converging — does ICCP's sub-region logic extend into NCSS's SSA network too?

## Connects to

[[vanguard]] operates the Pasir Ris sub-region under ICCP. [[aic]] holds the sub-region demand data. [[ncss]] is the parallel social-sector agency; the ICCP frame is evolving to include social. [[singapore-care-taxonomy]] documents the care types ICCP allocates. [[../reframing/hmw-2026-07-08-post-vanguard]] anchors our pilot inside Pasir Ris ICCP. [[../journal/2026-07-08-vanguard-visit]] is where the framework was explained to us. [[../strategy/respite-marketplace-concept]] gets shaped by the sub-region-native routing requirement.

## Proposed sibling / child entries

- [[iccp-referral-flow]] — how discharge → sub-region routing actually works.
- [[pasir-ris-sub-region-profile]] — the demographic and service map for our first pilot site.
- [[iccp-vs-national-scaling]] — the policy question of how a successful sub-region pilot moves to the next sub-region.
