---
title: "How Might We — current"
aliases: [HMW, the question]
status: solid
last_updated: 2026-05-19
based_on: hmw-2026-05-19-individual-exercise.md
---

ok so after the May 19 exercise — six individual HMWs from the five of us, mapped across WHO / DO / TO — the team converged on a single sentence. Here it is in plain English, the way it should read in a deck:

> **How might we help elderly in Singapore experience genuine daily connection, so that Singapore is brimming with elderly communities that are happy, mentally and physically healthy?**

That's the current HMW. It's not perfect, and we should keep beating on it, but it's the one we're working from this week.

## How we got here

Each of us wrote our own HMW first. The exercise generated six attempts (Zheng Wei wrote two). Across them:

- [AA — Aditi] Elderly in Singapore / feel less lonely / part of society, less healthcare burden
- [SS — Shobhit] Elderly not working, no kids/grandkids / feel connected with society / improve ageing experience, life expectancy
- [AK — Abhishek] Elderly staying alone (couple) / age with a close family member / age happily and with purpose
- [ZW — Zheng Wei] Socially isolated elderlies / experience genuine daily connection / feel seen, needed, and alive
- [ZW — Zheng Wei] Lonely elderlies / find meaningful companionship / live longer, healthier lives without dependency
- [LY — Lara] Elderly in Singapore (across all axes) / sense of belonging, assurance not left behind / Singapore brimming with elderly communities, happy, mentally/physically healthy

Two rows did most of the work for the final synthesis:

- The DO came from ZW's first attempt: "experience genuine daily connection."
- The TO came from LY: "Singapore is brimming with elderly communities that are happy, mentally/physically healthy."
- The WHO stayed general: "Elderly in Singapore."

## Why each component does its job

**The DO — "experience genuine daily connection."** This does three things at once. *Genuine* rules out hollow contact — chatbots that pretend to care, paid friendships that break when the contract ends, calls that aren't really mutual. *Daily* rules out one-off interventions; it says the rhythm matters. *Connection* is the thing actually being delivered — it's not a negation (less loneliness), not an abstraction (feel part of society), and not a transaction (find companionship). It's the positive, specific, lived experience.

The reason this beats the alternatives is that negations and outputs sit one layer below the actual thing people want. People don't want "less loneliness." Loneliness is the absence of connection; connection is what they're trying to get. Designing for the negation invites solutions that suppress the symptom (a noise machine, a TV show) instead of producing the thing.

**The TO — "Singapore brimming with elderly communities that are happy, mentally/physically healthy."** Notice that the other TOs we wrote tended to fit inside an individual life — "age happily" (AK), "live longer, healthier lives" (ZW), "feel seen and alive" (ZW). LY's TO pulls outcome up to societal scale. It's measurable at the level of communities, not individuals, and it implies a network effect — many such communities, many connected people. If the DO works at the level of one elderly person, the TO insists that the answer has to scale.

**The WHO — "elderly in Singapore."** We kept it general even though several of us narrowed it in our individual attempts. SS narrowed to "not working and living without kids/grandkids." AK to "staying alone (couple)." ZW to "socially isolated." Those narrowings are likely correct *as targeting decisions* — and we'll come back to them when we build empathy maps and personas — but we deliberately kept the WHO general at the HMW level so the question doesn't bake in a population assumption before we've talked to anyone.

## What this HMW does well

The DO + TO combination forces both individual and systemic thinking. You can't satisfy "genuine daily connection" with a one-off product feature, and you can't satisfy "brimming with communities" by helping one person. The HMW pulls toward solutions that work at two scales at once — which is exactly the kind of leverage we want.

It's also human-centric without being syrupy. "Genuine" is a hard word to fake. "Brimming" is aspirational without being saccharine. Compare to bland alternatives like "improve well-being for the elderly" — that phrasing wouldn't generate any specific ideas.

## What this HMW doesn't do well — be honest

**The WHO is vague.** "Elderly in Singapore" is ~1.1M people and they don't have one shape. Until we narrow (or until our empathy maps tell us how the WHO clusters), the HMW will tend to generate solutions that try to serve everyone and end up serving no one.

**"Genuine" is hard to operationalize.** We know what it isn't — an LLM pretending to be a grandson; a paid visit that ends when the hour ends. What it positively *is* will need to be sharpened, probably through what we observe in the empathy work. There's a real risk that "genuine" becomes a feel-good word we wave at any solution we end up liking.

**The leap from DO to TO is large.** Individual daily connection → Singapore brimming with communities is a theory-of-change with at least one missing middle step. Communities don't form just because individuals connect; they form because something is structurally encouraging clustering, repetition, and shared identity. We should write that middle step down before we believe the HMW. (Future entry: [[theory-of-change-connection-to-community]].)

**"Brimming" is rhetorical, not measurable.** Lovely word, no metric. At some point — not this week — we need a measurable proxy: "X% of Singaporean elderly report having Y or more meaningful weekly interactions" or similar.

## Devil's advocate seeds

Things a serious critic would say. We should each take one of these and argue it for a sprint:

1. The HMW treats companionship as the bottleneck, but the actual bottleneck for community formation in Singapore is *physical infrastructure* (HDB layouts, void deck use, senior activity center coverage) and *time* (working-age children unavailable), neither of which a software product can change. We'll build elegant software and nothing will change.

2. "Daily" is the wrong frequency. Real human connection has natural rhythms — weekly meals, monthly visits, seasonal celebrations — and forcing daily contact may degrade quality rather than enhance it.

3. "Elderly in Singapore" is a Western framing. In Asian family contexts, what elderly people experience is often grief about a value-shift that's already happened (children no longer co-resident, filial structures eroding). Addressing it as "loneliness" is treating a symptom.

4. We're missing a population. The HMW doesn't account for elderly with cognitive decline / dementia — for whom "experience genuine daily connection" is mechanically different and possibly impossible in the way we mean it.

5. The TO is unfalsifiable. "Brimming" can describe almost any outcome we observe, so we'll declare success regardless. We need a kill criterion — what would tell us we're failing?

## Open questions to chase this week

A few that should feed the empathy work:

- Which of the six individual HMWs do *actual elderly people* recognize as describing them? We've been writing from the outside in.
- Is "daily" what they actually want, or are they fine with less-than-daily?
- When they say "lonely" (or its equivalent in their language), what do they mean — absence of contact, absence of meaning, absence of role, all three?
- What's the difference between elderly who are isolated and *unhappy* about it, vs. isolated and *fine* with it?

## Connects to

[[hmw-2026-05-19-individual-exercise]] preserves the six original HMWs we synthesized from — the record of how this question evolved. [[devils-advocate]] is the entry where each of the five critiques above gets argued in earnest, by name. The empathy work in [[humans]] will be the main input to the next HMW iteration; expect the WHO to narrow once we've had three or four real conversations. The theory of change — how individual daily connection produces community-level flourishing — belongs in its own future entry, [[theory-of-change-connection-to-community]], because the HMW asserts that link without yet justifying it. [[eldercare]] is the broader problem-space overview this HMW sits inside.
