---
title: Prototype
status: active
last_updated: 2026-07-11
---

Woke up on 2026-07-11, ahead of the 2026-08-20 SGLN prototype milestone. Working name: **Kakis** (provisional — Singlish for trusted companions).

**Update 2026-08-09: the prototype became a running app.** [[kakis-app]] — deployed at
**https://singaporekakis.com**, three roles, real sign-in codes to real phones, a
database that persists. The HTML prototype below stays as the design record; the app is
now the thing people actually touch.

What's here:

- **`kakis-app.md`** — the live app: architecture, the design decisions worth
  remembering, and the three failures that cost real time (a crash that only appeared
  on the second boot, a "broken" matcher that was assigning correctly to the wrong
  person, and SMS that reported success while delivering nothing).
- **`kakis-prototype.html`** — the interactive mobile-app prototype, now at **v2** (built to `kakis-prototype-spec.md` after the team feedback round). 36 screens, four modules behind a "Who needs help today?" landing: the caregiver flow (service-first → three urgency tiers → triggers → match with backup → confirm & pay → track → report), a low-density elderly self-book mode, the respite giver's full lifecycle (sign-up with OTP + mocked Singpass consent → preferences → training → visits with OTP start/end → impact with PayNow → profile), and the ops console (Today, onboarding queue, two-level matching, categorised quality + archive). Every screen's demo-notes panel cites the spec section and evidence behind it.
- **`kakis-design-brief.md`** — the research-synthesis bridge between the evidence base and the prototype. Ten findings → ten design requirements (R1–R10). Read this first if you're wondering *why* a screen looks the way it does.
- **`kakis-build-plan.md`** — how the spec becomes a real app: design decisions (D1–D8), the recommended stack (Next.js PWA + Supabase SG + Claude-agent worker layer, WhatsApp-first notifications, deterministic matching with agents around it), a phased plan aligned to Aug 20 and the Q4 pilot, and how to run the Superpowers methodology on the build.
- **`kakis-prototype-spec.md`** — now at **v2**: the post-feedback build target. Integrates the three team reviews (Lara/Aditi on caregiver + elderly self-book, Shobhit/Aditi on respite giver, Zheng Wei/Aditi on admin) — each block records v1, the feedback, and the v2 target, with a priority register (P0/P1/ops/tension) and the open questions for Vanguard. The v1 screen mirror lives in git history. The prototype rebuild follows this document.
- **`kakis-prototype-spec.md`** — the complete written mirror of the prototype: every screen, every element, every interaction, with a `> FEEDBACK:` line under each block. This is the feedback surface — annotate it, and the prototype gets updated to match.

Deliberate scope cuts, documented in the brief: no real matching algorithm, no payments, senior-facing surface out of scope (the caregiver is the buyer — R6), agent behaviours scripted.

The rubric line this feeds: *"Human centricity of the solution (not just slides)"* — the prototype runs, and each design choice traces to a human in `humans/` or a constraint in `strategy/`.

Next for this folder: pressure-test against Vanguard's six crisis triggers before 2026-08-20; test sessions with real caregivers; a print/voice artifact concept for the senior.
