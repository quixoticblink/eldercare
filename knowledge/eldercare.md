---
title: Eldercare
aliases: [elder care, aging society, senior care]
prereqs: []
status: draft
last_updated: 2026-05-25
---

ok so eldercare looks like a social-services problem from the outside — old people need help, you build homes and hire caregivers and set up subsidies — and the moment you sit with it for a few hours you realize it's a demographics-meets-technology problem wearing a social-services costume. The world's old-age dependency ratio is doing something it has literally never done before in human history, and most of the existing eldercare infrastructure was designed for the previous demographic shape: lots of young adults per elderly person, big multi-generational families, somebody at home during the day. Those preconditions are breaking simultaneously. The interesting question isn't "how do we do more of what we already do, just at larger scale" — it's: what was the old system actually providing for old people, and which of those functions do we have to rebuild from scratch now that the old scaffolding is gone?

## A tiny worked example: the Singapore funnel

Smallest concrete version of the problem. Singapore, total population 6.11M (2025). How many are 65+ depends on which population you count: 18.8% of *residents* (citizens plus PRs, about 790,000 people) or 20.7% of *citizens* alone — see [[evidence/elderly-population-stat]] for why one country reports two numbers. Use the resident figure as the working number. Either way it's a fast climb: the resident share was 11.8% as recently as 2015, and citizens aged 65+ are projected to pass one in four by 2030. Now zoom in further. Of those ~790,000 elderly residents, somewhere around 70,000 live alone — call it roughly 9%, which sounds modest until you remember that's 70,000 individual households. Zoom one more time. Survey work in Singapore (Duke-NUS, NCSS, various academic panels) keeps finding that 30–50% of community-dwelling elderly report feeling lonely "often" or "sometimes" — the number moves around a lot depending on the instrument (UCLA-3 vs. single-item vs. de Jong Gierveld). I'm going to round hard and say: on the order of 30,000 people in one small city-state, today, who would tell you on a survey that they are lonely most of the time. That's roughly the capacity of the National Stadium.

The reason that funnel matters is that the problem isn't diffuse and abstract — it concentrates. The "population aging" framing makes it sound like everyone's a little worse off. The funnel says: no, there's a specific identifiable subpopulation that is severely worse off, and you can probably name them by postal code.

## Factoring eldercare into its parts

Here's the decomposition I keep coming back to. Eldercare is not one function, it's at least four functions that the old system used to bundle together inside a family:

1. Physical care. ADLs — bathing, toileting, mobility, medication adherence. This is the part everyone visualizes when they hear "eldercare." It's also the part that scales worst with technology, because bodies are stubbornly physical.
2. Instrumental support. Groceries, transport, bills, navigating the medical system. Logistics. This part is, in principle, very automatable — except the user is often the person least able to use the automation.
3. Companionship / social. Someone to talk to, eat with, be present with. Existence-of-witness. This is the part our team kept circling back to and I think it's correct that this is where the leverage is — partly because the unit economics of human companionship are catastrophic (a caregiver-hour costs $20–40, you'd want 4–8 of those a day, do the math) and partly because it generalizes globally in a way that physical care doesn't.
4. Cognitive / identity work. The thing where someone remembers your stories with you, knows what your grandchildren are named, asks how the surgery went. This one is subtle and easy to miss in a product spec but I suspect it's doing more of the heavy lifting than people realize.

Most products in the eldercare space pick one of these four and pretend the others don't exist. That's fine — focus is good — but it's useful to know which one you're picking and what you're outsourcing to the rest of the ecosystem.

## A probe: what if only #3 were the focus

This isn't a product proposal — we're observation-first this week, not solutioning — but it's a useful thought experiment for understanding how the four functions are entangled. Imagine, hypothetically, that companionship could be delivered in isolation. The marginal cost of an extra hour of conversation, if it could somehow reach the person, is essentially zero. That's the whole reason this function looks like the leverage point.

The moment you try to deliver it, though, you trip over function #2. The recipient can't install anything. They don't have a smartphone, or they have one but their kids set it up and they can't read the screen. So whatever ends up delivering companionship has to be installed, maintained, and recovered when it breaks, inside homes where there often isn't a tech-literate person nearby.

The thing that took me a while to see: companionship may be the highest-leverage bullet of the four, but you can't isolate it cleanly from instrumental support — the interface to it lives inside the instrumental-support layer. That's a structural fact about the problem, not a comment on any particular solution. It's the kind of observation that should shape the [[empathy-map-singapore-elderly]] before it shapes any product.

## What confused me / pitfalls

A few things I had wrong at first.

The "Singapore is unique" trap. It's tempting to look at Singapore's specific aging trajectory and assume the solution is Singapore-shaped. It isn't. Japan, South Korea, Italy, Germany, much of China — all heading to similar or worse dependency ratios in the next 15–20 years. The takeaway about global scalability is real, but "build in Singapore" is mostly a validation argument (small, English-speaking, well-instrumented, government supportive) — not a thesis about the problem being Singapore-specific.

The companionship-is-fake-care trap. There's a school of thought that says putting an AI between a lonely elderly person and a real human relationship is dystopian. I find this less convincing the more I think about it — the counterfactual is not "a real human relationship that would otherwise happen," it's "nothing, or daytime TV." But it's a real critique and you should be able to argue against it in your own head, not just dismiss it. See [[companionship-vs-care]].

The partnership-is-easy trap. The existing partnership opportunities (NCSS, healthcare startups, various government initiatives) are real, but they tend to come with a particular shape: pilot programs of 50–200 elderly, 6–12 month timelines, lots of demos for stakeholders, slow procurement. They are great for validation and terrible for the actual scaling step. Don't confuse a successful NCSS pilot with product–market fit.

The "elderly are tech-averse" folklore. This is half-true and the wrong half is more important than the right half. Yes, current 75+ year-olds in Singapore mostly aren't comfortable with apps. But every year, the cohort aging into "elderly" is more digital-native than the year before. The product window where you have to assume zero digital literacy is closing, and the window where you can assume basic smartphone competence is opening. Build for who they are in 2030, not 2020.

The loneliness-statistic citation chain. I'll flag that a lot of the loneliness numbers in the Singapore eldercare conversation get passed around without people checking the source. The 1-in-3 / 1-in-2 figures come from a small handful of studies and they don't always measure the same thing — sometimes "felt lonely in the past week," sometimes "score above threshold on UCLA-3," sometimes a single self-report item. If you're going to use these numbers in a deck, pull the original instruments and check. I haven't audited them carefully and I'm not confident which one to trust.

## Connects to

The natural next entry is [[elderly-loneliness]], which factors out the specific phenomenon that this entry treats as one function among four. Adjacent to that is [[companionship-vs-care]] — the conceptual argument for why companionship deserves to be treated as a first-class need rather than a luxury on top of care. The demographics piece, why this is happening now and everywhere at once, belongs in [[demographic-transition]] and its local variant [[singapore-aging-population]]. On the solution side, [[ai-companions-for-elderly]] is the obvious child entry, and it should pair with [[hardware-form-factors-for-elderly]] for the instrumental-layer problem described above. Finally, [[caregiver-burnout]] is worth a stub because it's a parallel problem with the same demographic root cause, and many eldercare products end up implicitly trying to serve both the elderly person and the family caregiver — often without realizing they're shipping two products.

## Proposed sibling / child entries

- [[elderly-loneliness]] — stats, instruments (UCLA-3, de Jong Gierveld), what loneliness actually predicts (mortality, cognitive decline), and the Singapore numbers with sources properly chased down.
- [[companionship-vs-care]] — the conceptual distinction between attending to someone's social/identity needs and their physical/instrumental needs, and why bundling them confuses product strategy.
- [[ai-companions-for-elderly]] — the design space for LLM-mediated companionship products: what works, what fails, what's still open.
- [[demographic-transition]] — the global aging picture; why the dependency ratio is doing something unprecedented; the math of it.
- [[caregiver-burnout]] — the other half of the eldercare problem; family caregivers as a hidden labor force on the brink of collapse.

---

*2026-05-25: reconciled the Singapore-funnel figures against [[evidence/elderly-population-stat]] — the earlier "population ~5.9M / ~19% / ~1.1M elderly" estimates were rough and wrong; corrected to the verified 6.11M total, 18.8% of residents (~790,000), 20.7% of citizens.*
