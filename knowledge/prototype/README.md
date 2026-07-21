---
title: Prototype
status: active
last_updated: 2026-07-11
---

Woke up on 2026-07-11, ahead of the 2026-08-20 SGLN prototype milestone. Working name: **Kakis** (provisional — Singlish for trusted companions).

What's here:

- **`kakis-prototype.html`** — the interactive mobile-app prototype, now at **v2** (built to `kakis-prototype-spec.md` after the team feedback round). 36 screens, four modules behind a "Who needs help today?" landing: the caregiver flow (service-first → three urgency tiers → triggers → match with backup → confirm & pay → track → report), a low-density elderly self-book mode, the respite giver's full lifecycle (sign-up with OTP + mocked Singpass consent → preferences → training → visits with OTP start/end → impact with PayNow → profile), and the ops console (Today, onboarding queue, two-level matching, categorised quality + archive). Every screen's demo-notes panel cites the spec section and evidence behind it.
- **`kakis-design-brief.md`** — the research-synthesis bridge between the evidence base and the prototype. Ten findings → ten design requirements (R1–R10). Read this first if you're wondering *why* a screen looks the way it does.
- **`kakis-prototype-spec.md`** — now at **v2**: the post-feedback build target. Integrates the three team reviews (Lara/Aditi on caregiver + elderly self-book, Shobhit/Aditi on respite giver, Zheng Wei/Aditi on admin) — each block records v1, the feedback, and the v2 target, with a priority register (P0/P1/ops/tension) and the open questions for Vanguard. The v1 screen mirror lives in git history. The prototype rebuild follows this document.
- **`kakis-prototype-spec.md`** — the complete written mirror of the prototype: every screen, every element, every interaction, with a `> FEEDBACK:` line under each block. This is the feedback surface — annotate it, and the prototype gets updated to match.

Deliberate scope cuts, documented in the brief: no real matching algorithm, no payments, senior-facing surface out of scope (the caregiver is the buyer — R6), agent behaviours scripted.

The rubric line this feeds: *"Human centricity of the solution (not just slides)"* — the prototype runs, and each design choice traces to a human in `humans/` or a constraint in `strategy/`.

Next for this folder: pressure-test against Vanguard's six crisis triggers before 2026-08-20; test sessions with real caregivers; a print/voice artifact concept for the senior.
