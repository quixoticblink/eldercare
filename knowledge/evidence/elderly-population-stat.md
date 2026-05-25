---
title: Elderly population — the numbers
aliases: [ageing statistics, demographic data, elderly population stats]
prereqs: [eldercare]
status: draft
last_updated: 2026-05-25
---

ok so before we argue about what to build, it's worth knowing how big the thing actually is — and the first surprise is that "how many old people are there in Singapore" does not have one answer. It has two, they differ by almost two percentage points, and both are official. Quote the wrong one in a deck and someone will (correctly) call it out. So this entry does two jobs: pin down the real numbers, and explain why the same country reports two of them.

The headline, though: Singapore is ageing about as fast as anywhere on earth, and the steep part of the curve is happening right now — not in some 2040 projection.

## The two numbers, 2025

Here's the thing that took me a while to see. Singapore counts its population in nested circles. The outer circle is the *total population* — 6.11 million in 2025 — everyone physically here: citizens, permanent residents, and non-residents (work pass holders, students, dependants). Inside that is the *resident population* — citizens plus PRs, about 4.2 million. Inside that again is the *citizen population* — citizens only, roughly 3.6 million.

The 65-and-over share gets reported against the inner two circles, and they don't match:

- Residents aged 65+: 18.8% in 2025 — about 789,580 people. (Singapore Department of Statistics, *Population Trends 2025*.)
- Citizens aged 65+: 20.7% in 2025. (*Population in Brief 2025*, National Population and Talent Division.)

Same country, same year, both correct. The citizen figure is higher because PRs and non-residents skew younger than citizens — adding them to the denominator dilutes the elderly share. So when you see "Singapore is over 20% elderly," that's the citizen number; when you see "18.8%," that's residents. Neither is wrong — they answer different questions. The research brief that seeded this entry quietly mixed the two series into one table, which is exactly the trap: always check which denominator a second-hand stat used.

For our purposes — designing for elderly people who live here — the *resident* figure is the cleaner working number, because PRs age in place here too and the problem doesn't care about passport colour. Use 18.8% / ~790,000, and say "of residents" when you do.

## The trajectory

A single year's number doesn't tell you much; the slope does.

The resident 65+ share went 11.8% (2015) → 18.0% (2024) → 18.8% (2025). The citizen share went 13.1% (2015) → 20.7% (2025). Either series roughly doubled in a decade. The median age of residents moved from 39.6 to 43.2 over the same ten years.

And it's accelerating, not levelling. The official projection has citizens aged 65+ reaching about 23.9% by 2030 — roughly one in four. By 2050, the elderly are forecast at about a third of the population. The very old are the fastest-growing slice of all: citizens aged 80+ went from 91,000 (2015) to about 145,000 (2025), a ~60% jump in ten years.

Two structural drivers make this near-impossible to reverse on a short horizon. First, fertility: Singapore's total fertility rate sits around 0.97 — well under half the ~2.1 replacement rate, one of the lowest in the world. Fewer young people enter the base each year. Second, the support ratio — working-age people per elderly person — is falling hard; working-age citizens (aged 20–64) dropped from 64.5% of citizens in 2015 to 59.8% in 2025, and the ratio is commonly projected to fall below 2 by 2050, down from around 5 a generation ago. Treat that 2050 support-ratio figure as a widely-cited projection, not a settled fact — projections that far out move.

The term you'll hear is "super-aged," usually defined as 21%+ aged 65. By the citizen measure Singapore is essentially there already (20.7% in 2025); by the resident measure it crosses 21% a few years later. So "super-aged Singapore" is a 2025–2030 fact depending on which circle you count — not a distant scenario.

## The global frame

Singapore is early, not unique. Population ageing is a worldwide megatrend, and putting our numbers next to the world's shows both how far along we are and where the analogues live.

Roughly 830 million people were aged 65+ globally in 2024 — about 10.2% of the ~8.2 billion world population. The UN's projections (*World Population Prospects 2024*) put that near 1.6 billion by 2050, around one in six people. The global 65+ share roughly doubled over the last fifty years and is projected to roughly double again over the next fifty.

The regional pattern matters more than the global average. Europe and North America have long carried the highest elderly shares (high-teens to low-20s percent), but East and Southeast Asia are catching up fastest — Japan, South Korea, and Hong Kong are projected to approach 40% elderly by 2050. Singapore is the most aged society in Southeast Asia by a clear margin; no other ASEAN country is close. These global and regional figures come from the research brief that seeded this entry (citing UN WPP 2024 and UNFPA); I've verified the Singapore numbers against primary sources but not each global one — treat them as well-sourced background, not audited.

The practical reading: a companionship solution that works in Singapore has a very large addressable world behind it, and the places to watch for prior art and partnership are Japan and South Korea, who hit these ratios first.

## What confused me / pitfalls

The resident-versus-citizen split is the big one. The rest of this section is smaller traps.

Don't quote a 65+ count against the total population. 6.11 million is the total; 789,580 is residents 65+. Dividing one by the other gives ≈12.9%, a ratio of nothing useful — elderly residents over a denominator stuffed with a million-plus non-residents. If you need "elderly people in Singapore," it's ~790,000 and the matching denominator is the ~4.2M resident population.

"Ageing" is two things, and they need different solutions. A rising elderly share can come from the top growing or the bottom shrinking. Singapore has both — but the TFR-0.97 bottom-shrink is the part that makes it structural; you can't immigrate or incentivise your way out of it quickly. The 80+ tail growing 60% in a decade is the part that drives acute-care demand. A loneliness/companionship intervention is mostly aimed at the 65–80 band; the 80+ surge is a different and heavier problem.

The support ratio is a headline, not a mechanism. "Fewer than 2 working-age per elderly by 2050" is striking and roughly true, but it's a national accounting figure — it says nothing about whether a specific elderly person has someone to talk to. Don't let the macro number stand in for the lived problem; that's what the [[interview-round-1-findings|interviews]] are for.

Projections are not measurements. The 2025 figures are counts. The 2030 and 2050 figures are projections, and the further out they run the more they're assumptions about fertility and migration policy. Quote 2025 numbers as fact; quote 2050 numbers as "projected."

## Connects to

This entry is the demographic backbone for [[eldercare]] — whose Singapore-funnel figures were reconciled against these verified numbers on 2026-05-25 (the earlier "~1.1 million" estimate was wrong and has been corrected). It sits alongside [[interview-round-1-findings]] as the other half of the evidence base: this is the *scale* of the problem, the interviews are its *texture*. The structural drivers point at a future entry, [[demographic-transition]], on why low fertility plus longevity produces this shape everywhere. The Japan/Korea comparison wants its own entry, [[ageing-in-japan-and-korea]], since they are the closest thing we have to a view of Singapore's 2040. And the support-ratio thread connects to [[caregiver-burnout]] — fewer working-age people per elderly person is the same fact, read from the caregiver's side.

## Proposed sibling / child entries

- [[demographic-transition]] — why low fertility plus rising longevity drives the elderly share up everywhere; the general mechanism behind these Singapore numbers.
- [[ageing-in-japan-and-korea]] — the societies that hit these ratios first; what they tried, what worked, what to borrow.
- [[singapore-old-age-support-ratio]] — the working-age-per-elderly figure, its projection, and why it's a macro number that shouldn't be mistaken for the lived problem.
- [[the-80-plus-surge]] — the fastest-growing cohort, and why it's an acute-care problem distinct from companionship.
- [[loneliness-prevalence-singapore]] — the still-missing number: how many of these ~790,000 are actually lonely. The interviews give texture; we still need a defensible rate.

---

Sources — Singapore figures: Singapore Department of Statistics, *Population Trends 2025*; National Population and Talent Division, *Population in Brief 2025*. Global figures carried from the research brief's UN World Population Prospects 2024 and UNFPA citations, not independently audited. Entry created 2026-05-25 from a research brief left in the evidence folder.
