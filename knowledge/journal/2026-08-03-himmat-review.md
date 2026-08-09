---
title: "Himmat review — show, don't tell — 2026-08-03"
date: 2026-08-03
attendees: [Himmat (SGLN tech lead / mentor), Rebecca (programme side), Team 9]
medium: recorded call, ~48 minutes, live app demo then coaching
status: solid
last_updated: 2026-08-09
source: "(2026_08_03) SGLN Team 9 - Meeting with Himmat & Rebecca.docx"
---

> **Attribution caveat, same as the other Aug 3 file.** All 292 transcript lines are labelled
> "Lara PuReum Yim"; the diarisation failed identically. Attributions below are inferred from
> register and context — Himmat is identifiable because he is the one grading us, controlling
> the agenda and referencing "when I was training you". The ASR is bad: "respect" = respite,
> "micro shoppers" = micro-jobbers, "Bangor" = Vanguard, "quick scene canvas" = lean canvas.
> The recording is also **truncated mid-question** — the last line is Himmat starting to ask
> something about the caregiving page and the answer isn't in the file.

Second meeting of the day, and it pulled the opposite direction from the first. In the
morning Vanguard talked us out of a live pilot and into a
[[2026-08-03-ncss-vanguard|tabletop exercise]]. In the afternoon Himmat spent forty-eight
minutes telling us to put the real app in real hands as fast as physically possible.

Neither meeting knew about the other. That's the thing worth recording.

## He signed up during the demo

We showed the wireframes and then the live app — *"That one has a database and APIs backing
it, so that's a different operation. That's a… that's a live one."* — and he registered
himself on the spot: *"I've approved it as a caregiver. Can you sign up?"* … *"So now, Mr.
Himmat, you're okay."*

`himmat20@gmail.com` and `rebecca.rajakumar@gmail.com` are still in the production database
as approved caregivers. That's where they came from.

His verdict on why that mattered: *"Explain it to me. I've already played around with it. I
go straight in. That's the advantage."*

## The method, in one line

> *"in design, we always say **show, don't tell. Give it to them earlier, the better. The
> feedback is so much more powerful when you give it to them earlier.**"*

Everything else follows from it. Send the wireframes to the cohort next week and save the
live app for the big day. Get it to people *"a week before or 3 days before, but give them a
few nights to sleep over."* Do UAT with *"dozens of people"* the week after National Day. Put
the working app in front of IMDA's Deputy CEO in early September, via Kiran. Roleplay the app
in the room rather than narrating it.

And a warning about the live demo that we should heed: *"he's probably gonna spend 2 min
looking at that while trying to listen to you. So it's gonna be a bit difficult for the
judging."*

## What he pushed back on

**The elderly don't use apps — visible on the first screen.** He caught it immediately:
*"even when I 1st the 1st page I saw that there was a caregiver, and I can say… when I see
elderly, they never use an app. So there's a gap there."* Still unresolved. In the app as
built, an elderly person cannot schedule for themselves; someone does it for them.

**Who approves whom is underspecified.** *"it's all controlled. It shouldn't happen. Control
means if somebody has to approve some people. Approve everyone?"* Fair — we have three
automation toggles and no written policy for when a coordinator should use them.

**Peer matching is not obvious.** The sharpest thing nobody else has said to us:
*"**who does old people want to hang out with?** Maybe sometimes we like to hang out with
young people. Sometimes you want to hang out with other old people. Sometimes you don't
know."* Our matching scores availability, language, service and history. It has no notion of
who anyone would actually enjoy.

**The idea isn't new.** *"I'm sure people have thought of this idea… **it just comes down to
whether you can execute this better than anyone else.** … Even if they copy you, as long as
you're faster than them."*

## Money, and the person who won't pay

He accepts Vanguard's $25–35/hr as the ceiling a platform can charge, and flatly rejects it
as what an elderly person will voluntarily hand over:

> *"**I don't think people will pay $35.** If you ask them, yes, you take them to take the
> wallet out. No."*
> *"**old people will never want to give any money away. So either the children do it.**"*

His answer is a third-party payer — *"this is where **Sugar Daddy** comes in"* — plus a
charity/pro-bono angle he says he undersold when teaching us, and student credits. His unit
economics observation is worth keeping: Vanguard charges $25–35 and pays micro-jobbers
$10–20, which he read as *"instead of 20% commission and grab… they're charging like 60%."*

⚠️ The pricing table we showed mixes units — one line is per hour, another is a flat fee, and
he says *"$35 a month"* at one point where the model is per hour. Worth fixing before it goes
in a deck. Also note the Vanguard population figure conflicts with itself in our own
material: 2,500 in one place, ~3,000 (24 centres × ~300) in another, and the speaker says
*"Was it?"* immediately after.

## On the presentation

The A+ was for the reframe, not the build: *"it's an A+, because you… **You reframe. That
means you challenge your first assumption.**"*

What he wants us to teach the room is the *evolution*, because other groups are stuck:
*"there are other people who get lost into this, what I call the **echo chamber**, where
everyone's sitting around the table, and they're not talking to customers."* Followed by his
refrain: *"**I always say the answer will emerge.**"*

Concrete instructions: replace explanation with one picture of the ecosystem; render the 15
meetings as a single ChatGPT-generated image and use it as evidence; **take the big numbers
but don't decompose them** (*"otherwise you'll take a lot of your 20 minutes, and everyone
will lap up that"*); build a lean canvas of top-3 customers, top-3 problems, top-3 solutions;
link every design decision back to an interview.

And **cut the commercial case** — wrong audience: *"why do you need to tell these guys the
commercial… it's more from a **product market fit** kind of. And that's why for me, **design
thinking is different from the full pitching**."*

Note the tension he leaves unresolved: strip the commercial story for the SGLN peers, then
send the same app to a government Deputy CEO to chase funding. Those are two different
pitches and the file never says which one 25 September is.

**Timing, corrected:** the 20-vs-25-vs-30 debate is about the **28 August rehearsal day**, not
Demo Day. Demo Day proper is *"less than 10 minutes in total."* The rehearsal lands at
*"30 min, 20 and 10. But please plan for 25"* — which does not add up, and the file's own
action list records it a third way. Everyone on the team presents a segment.

He also said the quiet part: *"I don't think you've spent a lot of time thinking about the
presentation, et cetera. You're busy solving this."*

## Two meetings, one day, opposite instructions

This is the entry's real content. Set the two Aug 3 sessions side by side:

| | Vanguard / NCSS, morning | Himmat, afternoon |
|---|---|---|
| **How to validate** | Tabletop, *"a very safe environment"*, 5 sets in a room | Real app, real users, *"the earlier the better"*, dozens of UAT interviews |
| **Binding constraint** | Supply — certification gates who can serve | Demand — willingness to pay; supply is four abundant pools |
| **Scope** | Narrow to chaperoning only | Wider — companionship, activities, and a stacked service model as the prize |
| **Success looks like** | *"lessen your administrative burden"* | Investable, PMF, IMDA funding, faster than copycats |

The word *tabletop* appears nowhere in the Himmat file; the words *administrative burden*
appear nowhere either. These aren't rebuttals, they're two parallel plans made the same day
by people who hadn't spoken.

We now have **two incompatible validation plans booked into the same window** — a facilitated
simulation the week of 17 Aug, and "dozens of UAT interviews" the week after National Day.
They are not obviously reconcilable and nobody owns the reconciliation.

My read, for what it's worth: Vanguard's caution is about *their* liability and *their*
staff, and it's legitimate — they carry the duty of care. Himmat's urgency is about learning
rate, and he's right that a tabletop with warm, failure-tolerant participants will not show
us cold-start friction. The honest resolution is probably both, sequenced: tabletop first
because it's what the partner will actually agree to, then real caregivers — but *ours*, not
Vanguard's, because that's the constraint Vanguard is protecting.

That's a decision the team has to make, not one that resolves itself.

## What's next

- Reconcile the two validation plans, explicitly, and tell both parties which one wins.
- UAT interviews week after National Day; iterate the **live app**, not the wireframes.
- Wireframes to the cohort next week; live app held for the big day.
- App to IMDA's Deputy CEO in early September via Kiran.
- Lean canvas 3/3/3; ecosystem picture; 15-meetings image.
- Fix the pricing table's mixed units and the conflicting Vanguard population figure.
- Decide which pitch 25 September is — design thinking, or funding.

*Connects to:* [[2026-08-03-ncss-vanguard]] · [[2026-07-20-masterclass]] ·
[[../prototype/kakis-app]] · [[../reframing/hmw-current]]
