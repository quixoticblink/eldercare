# Kakis — code quality and security audit

**Standard:** ISO/IEC 5055:2021 *Automated Source Code Quality Measures*
(Security, Reliability, Performance Efficiency, Maintainability)
**Scope:** `app/backend`, `app/frontend`, `app/deploy`, and the running EC2 host
**Date:** 9 August 2026 · **Version audited:** v1.5 · **Auditor:** automated review + live probing

---

## What this is, and what it is not

Every finding below was **verified against the running system**, not inferred
from reading code — endpoints were called, headers inspected, file permissions
listed, limits exercised. Fixes were re-verified the same way.

This is **not** a certification. ISO 5055 is a measurement standard for
automated source-code analysis; a conformance claim requires an accredited
tool and assessor. What follows is a structured self-assessment against its
four measures, using CWE identifiers from the same weakness taxonomy the
standard draws on.

It also does not cover: penetration testing, dependency CVE scanning, threat
modelling of the physical visit workflow, or PDPA legal review — the last of
which matters, because this system stores health data on Singapore residents.

---

## Summary

| Measure | Before | After | Residual |
|---|---|---|---|
| Security | 2 high, 3 medium | 0 high, 0 medium open | 3 accepted, documented |
| Reliability | 1 high (fixed earlier), 1 medium | 0 open | Restore untested |
| Performance Efficiency | No issues at pilot scale | — | Single-writer ceiling |
| Maintainability | 1 medium | 0 open | Inline handlers block strict CSP |

**Verdict: fit for a supervised field pilot.** Not yet fit for unsupervised
public launch — see *Before scale*.

---

## Security

### Fixed — HIGH · Unlimited authentication attempts
`CWE-307` improper restriction of excessive authentication attempts,
`CWE-770` allocation of resources without limits

`/auth/request-code` and `/auth/verify` had no throttling of any kind. Two
concrete consequences, not theoretical ones:

- Every code request sends a real SMS. With Twilio now billing per message, an
  attacker could run up the pilot's bill and simultaneously harass a
  caregiver's phone, indefinitely.
- A 6-digit code is only strong if guesses are limited. Unlimited attempts
  inside the 10-minute validity window is a practical account-takeover path —
  and an admin account is reachable this way.

**Fix:** `services/ratelimit.py`, a DB-backed sliding window. 5 code requests
per identifier per 15 min, 20 per source IP per 15 min, 5 failed verifications
before lockout. Backed by the database rather than process memory on purpose —
an in-memory limiter resets on every deploy, which is security theatre. A
successful sign-in clears the counters so an honest user who fumbles digits is
not stranded, and every lockout message offers the coordinator's phone number
as a human route out. Failed attempts now write `login_failed` to `audit_log`.

*Verified live:* 6th consecutive request returns `429`.

### Fixed — MEDIUM · Public API documentation
`CWE-200` exposure of sensitive information to an unauthorised actor

`/api/docs` and `/api/openapi.json` returned `200` to anyone, publishing every
endpoint, field and admin route — a map of the attack surface.

**Fix:** both disabled unless `API_DOCS=1`. *Verified live:* now `404`.

### Fixed — MEDIUM · Missing HTTP security headers
`CWE-1021` improper restriction of rendered UI layers, `CWE-693` protection
mechanism failure

No HSTS, framing, MIME-sniffing, referrer or CSP controls. The approve and
assign buttons were clickjackable.

**Fix:** in `deploy/Caddyfile` — HSTS (1 year, includeSubDomains),
`X-Frame-Options: DENY`, `nosniff`, `strict-origin-when-cross-origin`,
`Permissions-Policy` denying geolocation/mic/camera/payment, a whitelist CSP
with `frame-ancestors 'none'`, and the `Server` header removed.
*Verified live:* all six present.

### Fixed — MEDIUM · Health data world-readable
`CWE-732` incorrect permission assignment for critical resource

`kakis.duckdb` was `0644` and `backups/` was `0755` with `0644` files. That
database holds **medications, mobility limitations, home addresses and
emergency contacts** for elderly residents. Any second local account could read
it, as could any process running as another user.

**Fix:** database `0600`, backups directory `0700`, snapshots `0600`. The
systemd unit sets `UMask=0077` so newly created files inherit this, and the
backup script sets `umask 077` rather than relying on a later `chmod`.
*Verified live.*

### Fixed — MEDIUM · Application listening on all interfaces
`CWE-319` cleartext transmission of sensitive information

uvicorn bound `0.0.0.0:8000`. Only the security group stood between the
internet and the app served **unencrypted**, bypassing Caddy and TLS entirely —
one rule change away from exposure.

**Fix:** bound to `127.0.0.1`, with `--proxy-headers` and
`--forwarded-allow-ips=127.0.0.1`. *Verified live:* `ss` shows loopback only.

### Hardened — service account privileges
The systemd unit now sets `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=full`,
`ProtectHome=read-only` with an explicit `ReadWritePaths`,
`ProtectKernelTunables`, `ProtectControlGroups` and `RestrictSUIDSGID`.

### Examined and found sound
- **`CWE-89` SQL injection** — all queries parameterised. The two f-string
  queries interpolate column names from internal literals, never input.
- **`CWE-79` XSS** — the frontend escapes via `UI.esc`, and `UI.appbar`
  escapes internally. Remaining unescaped interpolations are numbers, enums
  and internal IDs.
- **`CWE-352` CSRF** — not applicable: bearer token in a header, not a cookie.
- **`CWE-613` session expiration** — suspending a user takes effect on their
  next request; `approved_user()` re-reads status per call rather than trusting
  the token.
- **`CWE-522` credential protection** — `.env` is `0600`; `JWT_SECRET` is a
  32-byte random value; no secrets in git (`.gitignore` verified).
- **Authorisation** — every admin route passes through `_admin()`; kakis cannot
  read the visit start code.

### Accepted risks — documented, not fixed

**User enumeration (`CWE-204`).** `/auth/request-code` returns `known`, which
reveals whether an address is registered. This is inherent to skipping the
name/role step for returning users. Acceptable while accounts require
coordinator approval; revisit if signup ever opens up.

**`unsafe-inline` in the CSP.** The views use inline `onclick` handlers and
style attributes, so a strict CSP would break the app. The current policy still
blocks external scripts, framing and form hijacking. Removing `unsafe-inline`
means refactoring the frontend to attach listeners in code — noted here rather
than done silently.

**Trusting `X-Forwarded-For`.** The per-IP limit reads a header that only Caddy
should set. Safe because nothing reaches uvicorn except via loopback; if the
app is ever exposed directly the IP limit becomes spoofable. The
per-identifier limit does not depend on it.

---

## Reliability

**Fixed earlier — HIGH · DuckDB WAL replay crash-loop.** The v1.1 migration
`ALTER TABLE visits ADD COLUMN ... DEFAULT ''` left a write-ahead-log entry
that DuckDB 1.5.5 could not replay after an unclean shutdown. The service came
up once, then crash-looped on every restart. A reboot would have taken the
pilot down permanently. Fixed with a `CHECKPOINT` after schema init; verified
across four restarts and a `SIGKILL`.

**Fixed — MEDIUM · Unpinned dependencies (`CWE-1104`).** `requirements.txt`
used `>=`, so builds were not reproducible — which is exactly how DuckDB 1.5.5
and its WAL bug arrived unreviewed. Now pinned to the tested versions.

**Sound:** notification and auto-match failures are caught and logged rather
than rolling back the assignment or booking that triggered them; the
assumptions file is written via atomic replace so a crash mid-write cannot
leave the app with unreadable pricing; DB access is serialised through a lock,
matching DuckDB's single-writer model.

**Open:** **backups have never been restore-tested.** Snapshots are written
nightly and permissions are now correct, but an unrestored backup is a hope,
not a backup.

---

## Performance efficiency

No issues at pilot scale. Two structural ceilings worth naming:

- **DuckDB is single-writer**, and all access is serialised behind one lock.
  Fine for a Pasir Ris pilot; it will not survive concurrent load.
- **The admin matching screen issues one roster request per open visit.** Fine
  at tens of visits, quadratic-feeling at hundreds.

Neither warrants change now — flagged so they are chosen deliberately later.

---

## Maintainability

Module boundaries in `SPEC.md` are respected: routers never import each other,
shared logic sits in `services/`, and the frontend never calls `fetch` outside
`api.js`. Money and time constants live in exactly one place
(`assumptions.json`) with provenance per figure. The 148-assertion smoke test
covers the full lifecycle and now isolates itself from live pricing.

**Remaining:** inline event handlers block a strict CSP (above); most pricing
in `assumptions.json` is still marked `PLACEHOLDER`.

---

## Before scale

Ordered by what would hurt most:

1. **Restore-test a backup.** Untested backup, unknown recovery.
2. **PDPA review.** This stores health data on Singapore residents. Consent,
   retention, breach notification and a data-deletion route are legal
   obligations, not features. There is currently no user-facing deletion path.
3. **Confirm the pricing.** Most figures are `PLACEHOLDER`; the 54% subsidy and
   14% top-up are illustrative and appear on screens families see.
4. **Dependency CVE scanning** in CI now that versions are pinned.
5. **Off-box backups.** Snapshots sit on the same instance as the database;
   losing the instance loses both.
6. **Remove `unsafe-inline`** by refactoring inline handlers.
7. **Independent penetration test** before unsupervised public launch.
