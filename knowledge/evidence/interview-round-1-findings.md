---
title: "Interview round 1 — what six conversations told us"
aliases: [field findings, round 1 interviews]
status: draft
last_updated: 2026-05-25
based_on:
  - 2026-05-21-solution-provider-senior-tech
  - 2026-05-22-caregiver-dementia-grandmother
  - 2026-05-24-elderly-woman-living-with-family
  - 2026-05-25-elderly-gentleman-toa-payoh-aac
  - 2026-05-25-frontline-caretaker-old-age-home
  - 2026-05-25-elderly-resident-rc-centre
---

Between May 21 and 25 we ran our first round of field interviews — six conversations — and they are the first time the [[hmw-current|HMW]] met an actual person instead of a whiteboard. The short version: the conversations validated the *rhythm* half of our thinking and seriously complicated the *how*. The biggest single thing we learned came from the person with the most to gain from telling us the opposite.

## The sample — and why to be careful with it

Six interviews. Two were elderly people speaking for themselves, one was an elderly man interviewed in the field outside an Active Ageing Centre, one was a caregiver (grandchild of a woman with dementia), one was a frontline caretaker at an old age home, and one was the founder of a company building technology products for seniors. Conducted across five days, mostly by reaching whoever we could reach quickly.

That is a small, convenience-sampled n. We should not present any of what follows as a rate or a proportion — six people cannot tell you how common anything is. What six good conversations *can* do is surface mechanisms: the shapes loneliness takes, the ways interventions fail, the things people say when you ask them directly. Treat everything below as a hypothesis with a quote attached, not as a measured fact. The raw notes are in [[../humans/README|humans/]], one file per interview, and every claim here links back to one.

## Finding 1 — Loneliness is an empty calendar

The clearest definition came unprompted, from an elderly person with an otherwise full and well-organised life: loneliness is "when I wake up without any activities planned for the day" ([[2026-05-25-elderly-resident-rc-centre]]). Not the absence of people — the absence of *structure*. The same idea arrived from a completely different direction: the solution provider observed that elderly people struggle especially after losing their "forced structure" — school, work — the scaffolding that used to decide what the day was for ([[2026-05-21-solution-provider-senior-tech]]).

And the man in Toa Payoh is the positive control. He has rebuilt a structure for himself — coffee shop, Active Ageing Centre, four to five hours out of the house a day — and he is doing fine ([[2026-05-25-elderly-gentleman-toa-payoh-aac]]). Same city, same demographic, opposite outcome, and the difference is whether the day has a shape.

This validates the word *daily* in our HMW. It also reframes the target. The thing to deliver may be less "a companion" and more "a reason the day has structure."

## Finding 2 — AI companionship has a half-life

This is the finding to take most seriously, because of who said it. The founder we interviewed builds AI products for seniors — they have every commercial incentive to tell us AI companionship works. They told us the opposite. The affection is real at the start ("strong affection at the start and hyperengaged"), but users "figure out certain patterns and it becomes less personal," and "even with LLM etc., after many many interactions, they lose the feeling" ([[2026-05-21-solution-provider-senior-tech]]). Asked what the smallest meaningful change would be, they said: "someone they can talk/banter with every day — cannot be AI."

A second interview drew the same boundary from the other side. The caregiver of a woman with dementia said she was comfortable with an AI companion *only because* her grandmother's dementia meant she "can't tell between real or AI" ([[2026-05-22-caregiver-dementia-grandmother]]). The unspoken corollary: for a lucid person, the substitution is detectable, and once detected it stops working.

This doesn't kill a technology-mediated solution. But it says plainly that an AI-as-the-companion product is building on sand, and that any tech in this space probably has to route *toward* human connection rather than stand in for it. We've flagged this in [[devils-advocate]] and it should shape the next [[hmw-current|HMW]] iteration — though per the team's call we are recording the tension, not unilaterally rewriting the question.

## Finding 3 — The people who need connection most are gated by pride

Three interviews independently named pride. The solution provider described "people with very strong personalities" who "never learnt how to compromise." The caregiver said her grandmother had "too much pride to ask" and "a super strong personality, so nobody wanted to offer help." The Toa Payoh man named "pride / shyness" as what stops older folks reaching out to people they don't already know.

Stack that against Finding 1 and you get an uncomfortable shape: the elderly most at risk — the ones who've lost structure and won't construct new social ties — are often exactly the ones whose personality makes them hardest to reach. A solution that requires the user to opt in, admit a need, or accept help from a stranger is selecting against the people who need it most.

There's a quieter barrier in the same region: language. In institutional care, caretakers "don't even understand your language" ([[2026-05-21-solution-provider-senior-tech]]); in the community, Mandarin-only speakers can't connect with non-Mandarin volunteers ([[2026-05-25-elderly-gentleman-toa-payoh-aac]]). Pride and language both do the same thing — they shrink the set of people a given elderly person can actually connect with.

## Finding 4 — Connection flows through contribution, not just company

When the elderly woman living with her family was asked about a skill she hadn't had a chance to share, she said: "I teach cooking to grand children and makes me feel more connected" ([[2026-05-24-elderly-woman-living-with-family]]). Read that carefully — the connection came from *giving*, from being the one with something to offer, not from being visited or cared for. The same interview contains the counter-image: she lives inside a full multi-generational house and still "eat[s] alone."

This matters because most eldercare framing — including some of ours — casts the elderly person as a recipient. The data suggests the felt experience of connection is closer to having a role. It also explains Finding 5's "charity" problem: being helped positions you as needy; contributing positions you as useful, and only one of those feels like connection.

## Finding 5 — Consistency is the product; transient help doesn't count

"Consistency is the most important in whatever solutions" — the caregiver, flatly ([[2026-05-22-caregiver-dementia-grandmother]]). The frontline caretaker described the failure mode: volunteers "do for a limited period and go away" ([[2026-05-25-frontline-caretaker-old-age-home]]). The solution provider described the same decay inside a product — engagement that fades over months.

And there's the charity problem, stated by the elderly woman directly: she would take help from a non-family member "if really needed," but "it wont feel natural" ([[2026-05-24-elderly-woman-living-with-family]]). Put these together and a requirement emerges: the connection has to be durable *and* it has to not feel like a service being delivered to a needy recipient. Transient, programmatic, or charity-shaped help fails on one axis or the other. This is also where existing solutions fall short — not for lack of services but, in the solution provider's words, because "a caretaker may just be a caretaker but not one that provides care."

## Finding 6 — Family is the answer people want, and the one they can't get

What the grandmother with dementia wanted was not "a companion." She "Only asked for her son" ([[2026-05-22-caregiver-dementia-grandmother]]). The woman living with family wants "my children to look after me" ([[2026-05-24-elderly-woman-living-with-family]]). The RC-centre interviewee, resigned: "Children only come visit once in a while... it's part of life... nothing more to be done" ([[2026-05-25-elderly-resident-rc-centre]]).

Any solution is competing with a specific, named, irreplaceable person. That is a brutal benchmark, and it's worth being honest that we will usually lose to it. The realistic design question is not "how do we replace family" but "what is the best thing that is *not* family, and how do we keep it from feeling like a consolation prize." Finding 4 is probably the way through — contribution gives the elderly person a role that family visits don't, which is one of the few things a non-family solution can offer that family doesn't automatically provide.

## What this does to our thinking

The HMW survives the rhythm test. "Genuine daily connection" — the *daily* is strongly supported by Finding 1, and *genuine* now has teeth: Finding 2 tells us what fails the genuineness test (AI that gets found out) and Findings 4–6 tell us what passes it (a durable role, not a delivered service, not a charity visit, ideally something family-shaped without pretending to be family).

The HMW also took two real hits. The implicit assumption that this gets solved with a technology companion is weaker than it was a week ago. And the WHO — "elderly in Singapore" — is now visibly too broad: the man coping fine in Toa Payoh and the woman eating alone in a full house and the bed-bound residents at the old age home are not one population and will not be served by one solution. We are not rewriting the HMW here ([[devils-advocate]] holds the open tension), but the next iteration should narrow the WHO and drop any unstated assumption that the answer is an app.

## What's thin, and what's next

The honest gaps: only six interviews; the frontline-worker conversation was too short to lean on; we have no one with moderate-to-severe cognitive decline speaking for themselves (only via a caregiver); and we have nobody who is isolated *and* refuses contact — the pride-gated population from Finding 3 is, definitionally, the population that didn't answer our form. Next round should target a fuller frontline-worker interview, more elderly people living genuinely alone, and at least one attempt to reach someone in the pride-gated group, probably through a person they already trust rather than cold.

## Connects to

This entry is the synthesis; the six raw conversations live in [[../humans/README|humans/]] and should be read alongside it. It feeds directly into the empathy maps due for the May 26 deliverable — expect the WHO to split into two or three personas. [[hmw-current]] is the question these findings test; [[devils-advocate]] now carries the AI tension as a sharpened critique. The structural-loneliness idea in Finding 1 connects to [[../problem/README|the problem space]] and probably deserves its own entry, [[loneliness-as-loss-of-structure]]. The charity-versus-contribution distinction in Findings 4–6 wants an entry too — [[connection-through-contribution]].

## Proposed sibling / child entries

- [[loneliness-as-loss-of-structure]] — the reframe from Finding 1: loneliness as an empty calendar, and what the "forced structure" of work and school was actually doing.
- [[connection-through-contribution]] — Findings 4–6: why being useful beats being visited, and why "charity-shaped" help fails.
- [[ai-companionship-half-life]] — Finding 2 written up properly, with the solution provider's account and the dementia boundary case.
- [[empathy-map-coping-vs-struggling]] — the persona split the WHO needs: the Toa Payoh man vs. the silent sitters he describes.
- [[reaching-the-pride-gated]] — the access problem of Finding 3: how to reach elderly who won't admit a need or accept a stranger.
