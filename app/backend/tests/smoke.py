import os, sys, shutil, tempfile
os.environ["DB_PATH"] = "/tmp/kakis-test.duckdb"
os.environ["DEV_MODE"] = "1"
os.environ["ADMIN_EMAILS"] = "admin@kakis.sg"
if os.path.exists("/tmp/kakis-test.duckdb"): os.remove("/tmp/kakis-test.duckdb")

# The rate-editing tests write assumptions.json. Point the app at a throwaway
# copy so running this on the server can never overwrite live pricing.
if not os.environ.get("ASSUMPTIONS_PATH"):
    _here = os.path.dirname(os.path.abspath(globals().get("__file__", "backend/tests/smoke.py")))
    _src = os.path.join(_here, "..", "..", "assumptions.json")
    if not os.path.exists(_src):
        _src = "assumptions.json"                 # run from app/
    _tmp = os.path.join(tempfile.mkdtemp(prefix="kakis-smoke-"), "assumptions.json")
    shutil.copyfile(_src, _tmp)
    os.environ["ASSUMPTIONS_PATH"] = _tmp

sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from backend.main import app
from backend import config, db
from backend.services import ratelimit as _rl
c = TestClient(app)

# v1.6 added a booking horizon (max_advance_days, default 30) and a past-date
# check. The fixtures below use fixed dates in early August 2026 so the weekday
# assertions stay readable; pin "now" to a Saturday just before them so those
# dates are neither past nor beyond the horizon, whatever day the suite runs.
from backend.routers import visits as _visits
import datetime as _dt
_PINNED_NOW = _dt.datetime(2026, 7, 25, 10, 0)     # Saturday
_visits._now = lambda: _PINNED_NOW

# Every request in this suite comes from the same TestClient address, so the
# per-IP cap would throttle the suite itself. Reset that one counter between
# calls; the per-identifier cap and the IP cap are both still asserted
# explicitly in the v1.5 section below.
def _unthrottle_ip():
    _rl.clear("request_code_ip", "testclient")

def request_code(identifier):
    _unthrottle_ip()
    r = c.post("/api/auth/request-code", json={"identifier": identifier})
    assert r.status_code == 200, r.text
    return r.json()

def reveal_start_code(vid, cg_headers, kaki_headers):
    """v1.6 identity both ways: the kaki shows a code, the caregiver enters it,
    and only then does the caregiver's start code appear."""
    kc = c.get(f"/api/visits/{vid}", headers=kaki_headers).json()["kaki_code"]
    r = c.post(f"/api/visits/{vid}/verify-kaki", json={"code": kc}, headers=cg_headers)
    assert r.status_code == 200, r.text
    return r.json()["otp_code"]

def login(identifier, role=None, name=None, **extra):
    req = request_code(identifier)
    r = c.post("/api/auth/verify",
               json={"identifier": identifier, "code": req["dev_code"], "role": role, "name": name, **extra})
    assert r.status_code == 200, r.text
    d = r.json()
    return {"Authorization": f"Bearer {d['token']}"}, d["user"]

# health
assert c.get("/api/health").json()["ok"]

# admin auto-approved
ah, admin = login("admin@kakis.sg", name="Wei Lin")
assert admin["role"] == "admin" and admin["status"] == "approved", admin

# caregiver signs up -> pending
ch, cg = login("priya@example.com", role="caregiver", name="Priya")
assert cg["status"] == "pending"
r = c.post("/api/visits", json={"service":"Chaperone","tier":"urgent","date":"today","window":"within the hour","language":"Tamil"}, headers=ch)
assert r.status_code == 403, "pending caregiver must be blocked: " + r.text

# kaki signs up -> pending
kh, kk = login("beelian@example.com", role="kaki", name="Tan Bee Lian")
assert kk["status"] == "pending"

# wrong OTP rejected
r = c.post("/api/auth/verify", json={"email":"x@example.com","code":"000000"})
assert r.status_code == 400

# admin approves both
pend = c.get("/api/admin/pending-users", headers=ah).json()
assert len(pend) == 2, pend
for p in pend:
    assert c.post(f"/api/admin/users/{p['id']}/approve", json={}, headers=ah).status_code == 200

# kaki sets profile
r = c.put("/api/users/me", json={"services":["Chaperone","Companionship"],"languages":["Tamil","English"],"phone":"+65 9111 1111"}, headers=kh)
assert r.status_code == 200 and "Chaperone" in r.json()["kaki"]["services"], r.text

# caregiver household + care plan
r = c.put("/api/care/household", json={"senior_name":"Mr Nathan","senior_age":78,"address":"Blk 415 Pasir Ris Dr 4"}, headers=ch)
assert r.status_code == 200, r.text
r = c.put("/api/care/plan", json={"meds":"Metformin 2pm daily","mobility":"Walks with a stick","languages":["Tamil"],"contacts":"Priya 9XXX","notes":"Introduce slowly"}, headers=ch)
assert r.status_code == 200 and r.json()["plan"]["meds"].startswith("Metformin")

# caregiver requests a visit (with a crisis trigger — v1.1)
r = c.post("/api/visits", json={"service":"Chaperone","tier":"urgent","date":"today","window":"within the hour","language":"Tamil","notes":"Helper left suddenly","trigger":"Helper left suddenly"}, headers=ch)
assert r.status_code == 200, r.text
visit = r.json(); vid = visit["id"]
assert visit["status"] == "requested" and "otp_code" not in visit   # v1.6: revealed only after the kaki is verified
assert visit["trigger"] == "Helper left suddenly"
assert visit["estimate"] and visit["estimate"]["base"] == 84 and visit["estimate"]["family_pays"] > 0
assert visit["times_together"] == 0

# locked service rejected
r = c.post("/api/visits", json={"service":"Medicine administration","tier":"urgent","date":"today","window":"now","language":"Tamil"}, headers=ch)
assert r.status_code == 400

# admin sees request + kaki list, assigns manually
kaks = c.get("/api/admin/kakis", headers=ah).json()
assert kaks and kaks[0]["name"] == "Tan Bee Lian"
r = c.post(f"/api/admin/visits/{vid}/assign", json={"kaki_id": kaks[0]["id"]}, headers=ah)
assert r.status_code == 200, r.text

# kaki sees it WITHOUT the otp, accepts
mine = c.get("/api/visits", headers=kh).json()
assert len(mine) == 1 and mine[0]["status"] == "assigned"
kv = c.get(f"/api/visits/{vid}", headers=kh).json()
assert "otp_code" not in kv, "kaki must not see the start code"
assert c.post(f"/api/visits/{vid}/accept", headers=kh).status_code == 200

# [B2·2] identity both ways. The caregiver does NOT see the start code yet —
# first the kaki shows their photo and a 4-digit kaki code, the caregiver
# enters it, and only then is the start code revealed.
cv = c.get(f"/api/visits/{vid}", headers=ch).json()
assert "otp_code" not in cv and cv["status"] == "accepted" and cv["kaki"]["name"] == "Tan Bee Lian"
assert cv["kaki_verified_at"] is None
kv = c.get(f"/api/visits/{vid}", headers=kh).json()
assert kv["kaki_code"] and len(kv["kaki_code"]) == 4 and "otp_code" not in kv, kv
assert "kaki_code" not in cv, "the caregiver must not be shown the kaki's code — they have to ask for it"
assert c.post(f"/api/visits/{vid}/verify-kaki", json={"code": "0000" if kv["kaki_code"] != "0000" else "1111"}, headers=ch).status_code == 400
assert c.post(f"/api/visits/{vid}/verify-kaki", json={"code": kv["kaki_code"]}, headers=kh).status_code == 403
otp = reveal_start_code(vid, ch, kh)
cv = c.get(f"/api/visits/{vid}", headers=ch).json()
assert cv["otp_code"] == otp and cv["kaki_verified_at"], cv
# the kaki's start code entry is unchanged — still never in their own responses
assert "otp_code" not in c.get(f"/api/visits/{vid}", headers=kh).json()

# start: wrong code fails, right code works
assert c.post(f"/api/visits/{vid}/start", json={"otp":"0000" if otp != "0000" else "1111"}, headers=kh).status_code == 400
assert c.post(f"/api/visits/{vid}/start", json={"otp": otp}, headers=kh).status_code == 200

# complete with report
r = c.post(f"/api/visits/{vid}/complete", json={"chips":["Went well","Meds taken"],"text":"Market trip, meds ticked.","meds_confirmed":True}, headers=kh)
assert r.status_code == 200 and r.json()["status"] == "completed"

# caregiver sees report + leaves private care note
cv = c.get(f"/api/visits/{vid}", headers=ch).json()
assert cv["report"]["meds_confirmed"] and "Went well" in cv["report"]["chips"]
assert c.post(f"/api/visits/{vid}/care-note", json={"chips":["All fine"],"text":"Papa was cheerful"}, headers=ch).status_code == 200

# times_together increments after completion (consistency signal — v1.1)
r = c.post("/api/visits", json={"service":"Wellness check","tier":"planned","date":"2026-08-01","window":"Morning 9–12","language":"Tamil"}, headers=ch)
v2 = r.json()
c.post(f"/api/admin/visits/{v2['id']}/assign", json={"kaki_id": kaks[0]["id"]}, headers=ah)
v2b = c.get(f"/api/visits/{v2['id']}", headers=ch).json()
assert v2b["times_together"] == 1, v2b["times_together"]

# admin quality + overview
qq = c.get("/api/admin/quality", headers=ah).json()
assert len(qq["reports"]) == 1 and len(qq["notes"]) == 1
ov = c.get("/api/admin/overview", headers=ah).json()
assert ov["completed"] == 1 and ov["pending_users"] == 0, ov

# chatbot fallback (no key)
r = c.post("/api/chat", json={"message":"how do I book a visit?"}, headers=ch)
assert r.status_code == 200 and "Book a visit" in r.json()["reply"] or "book" in r.json()["reply"].lower()

# role guard: kaki can't create visits, caregiver can't assign
assert c.post("/api/visits", json={"service":"Chaperone","tier":"soon","date":"today","window":"pm","language":"English"}, headers=kh).status_code == 403
assert c.post(f"/api/admin/visits/{vid}/assign", json={"kaki_id":"x"}, headers=ch).status_code == 403

# ---- v1.2 · sign in by email OR mobile -------------------------------------

# returning user is recognised, so the UI can skip the name/role questions
again = request_code("priya@example.com")
assert again["known"] is True and again["needs_profile"] is False, again
assert again["channel"] == "email"

# a brand-new identifier still needs the profile step
fresh = request_code("someone-new@example.com")
assert fresh["known"] is False and fresh["needs_profile"] is True, fresh

# phone numbers normalise to E.164 however they are typed
for typed in ("9123 4567", "+65 9123 4567", "6591234567", "91234567"):
    assert request_code(typed)["identifier"] == "+6591234567", typed

# sign up by mobile only — no email at all
ph, pu = login("9123 4567", role="kaki", name="Siti")
assert pu["phone"] == "+6591234567" and pu["status"] == "pending", pu
assert pu["email"] is None, "phone-only signup must not invent an email"
assert pu["phone_verified"] is True and pu["email_verified"] is False, pu

# second visit by the same number is a plain sign-in, no profile step
assert request_code("+6591234567")["needs_profile"] is False

# signing up by email while offering a mobile links both channels
eh, eu = login("dual@example.com", role="caregiver", name="Mei", contact_phone="8111 2222")
assert eu["phone"] == "+6581112222" and eu["email_verified"] is True
assert eu["phone_verified"] is False, "a captured number is not a verified one"

# ...and that same person can then come in through the mobile side
dh, du = login("+6581112222")
assert du["id"] == eu["id"], "email and mobile must reach the same account"
assert du["phone_verified"] is True, "signing in by SMS verifies the number"

# a number already linked to someone else is refused
req = request_code("clash@example.com")
r = c.post("/api/auth/verify", json={"identifier": "clash@example.com", "code": req["dev_code"],
                                     "role": "caregiver", "name": "Clash", "contact_phone": "8111 2222"})
assert r.status_code == 400 and "already linked" in r.json()["detail"], r.text

# admins can be recognised by mobile too
os.environ["ADMIN_PHONES"] = "+6599990000"
config.ADMIN_PHONES = ["+6599990000"]
_, pa = login("9999 0000", name="Coordinator")
assert pa["role"] == "admin" and pa["status"] == "approved", pa

# junk identifiers are rejected, not silently accepted
for junk in ("", "not-an-email", "12", "+"):
    assert c.post("/api/auth/request-code", json={"identifier": junk}).status_code == 400, junk

# legacy {"email": ...} callers still work
assert c.post("/api/auth/request-code", json={"email": "priya@example.com"}).status_code == 200

# ---- v1.3 · assumptions, availability, safer matching ----------------------

# every money figure traces back to assumptions.json, not hardcoded constants
asm = c.get("/api/admin/assumptions", headers=ah)
assert asm.status_code == 200, asm.text
A = asm.json()
assert "Chaperone" in A["services"] and A["services"]["Chaperone"]["hours"] == 3
assert "source" in A["services"]["Chaperone"], "every figure must state where it came from"
assert A["disclaimer"]["short"], "a disclaimer string must exist for the UI footer"
assert c.get("/api/admin/assumptions", headers=ch).status_code == 403, "assumptions are admin-only"

# the price stack is computed from that file
est = c.get(f"/api/visits/{vid}", headers=ch).json()["estimate"]
svc = A["services"]["Chaperone"]
assert est["base"] == svc["hours"] * svc["family_rate_per_hour"], est
assert est["kaki_fee"] == svc["hours"] * svc["kaki_rate_per_hour"], est
assert est["transport"] == A["kaki_payment"]["transport_allowance_per_visit"]["value"]
assert est["illustrative"] is True and est["disclaimer"], est

# --- kaki availability ---
av = c.get("/api/users/me/availability", headers=kh)
assert av.status_code == 200 and av.json()["any_set"] is False, av.text

r = c.put("/api/users/me/availability",
          json={"weekly": {"Tue": ["morning"], "Sat": ["morning", "afternoon"],
                           "Nonsense": ["morning"], "Wed": ["midnight"]},
                "note": "Weekends best"}, headers=kh)
assert r.status_code == 200, r.text
wk = r.json()["weekly"]
assert wk["Tue"] == ["morning"] and sorted(wk["Sat"]) == ["afternoon", "morning"], wk
assert "Nonsense" not in wk and wk["Wed"] == [], "bad day/half-day names must be dropped, not stored"
assert r.json()["any_set"] is True

# dated exceptions override the weekly pattern
r = c.post("/api/users/me/availability/exceptions",
           json={"date": "2026-08-04", "half_day": "all", "available": False, "note": "Away in JB"},
           headers=kh)
assert r.status_code == 200 and len(r.json()["exceptions"]) == 1, r.text
ex_id = r.json()["exceptions"][0]["id"]
assert c.post("/api/users/me/availability/exceptions",
              json={"date": "not-a-date"}, headers=kh).status_code == 400

# caregivers have no availability to set
assert c.get("/api/users/me/availability", headers=ch).status_code == 403

# --- availability drives the matching screen ---
from backend.services import availability as availmod
assert availmod.parse_date("2026-08-04").isoformat() == "2026-08-04"
assert availmod.half_day_for_window("14:00–17:00") == "afternoon"
assert availmod.half_day_for_window("morning visit") == "morning"
# 2026-08-04 is a Tuesday: normally a morning slot, but blocked by the exception
assert availmod.check(kk["id"], "2026-08-04", "09:00–11:00")["state"] == "unavailable"
# 2026-08-01 is a Saturday, both halves available
assert availmod.check(kk["id"], "2026-08-01", "09:00–11:00")["state"] == "available"
# Monday is not in the weekly pattern
assert availmod.check(kk["id"], "2026-08-03", "09:00–11:00")["state"] == "unavailable"

# a kaki who has never set availability is 'unknown', never 'unavailable' —
# otherwise the coordinator would silently stop offering them work
kh2, kk2 = login("newkaki@example.com", role="kaki", name="Fresh Kaki")
c.post(f"/api/admin/users/{kk2['id']}/approve", json={"role": "kaki"}, headers=ah)
assert availmod.check(kk2["id"], "2026-08-01", "09:00–11:00")["state"] == "unknown"

# roster is scored per visit and never hides anyone
r = c.post("/api/visits", json={"service":"Companionship","tier":"planned","date":"2026-08-01",
                                "window":"09:00–11:00","language":"English"}, headers=ch)
nvid = r.json()["id"]
roster = c.get(f"/api/admin/kakis?visit_id={nvid}", headers=ah).json()
assert len(roster) >= 2, "availability must sort, not filter"
assert roster[0]["fit"]["state"] == "available", [k["fit"] for k in roster]
assert all("fit" in k and "availability" in k for k in roster)

# assignment names who actually received it — the mis-assignment trap
r = c.post(f"/api/admin/visits/{nvid}/assign", json={"kaki_id": kk2["id"]}, headers=ah)
assert r.status_code == 200 and r.json()["assigned_to"]["id"] == kk2["id"], r.text
assert r.json()["assigned_to"]["name"] == "Fresh Kaki", r.json()
# ...and the right kaki sees it, the other does not
assert any(v["id"] == nvid for v in c.get("/api/visits", headers=kh2).json())
assert not any(v["id"] == nvid for v in c.get("/api/visits", headers=kh).json())

assert c.delete(f"/api/users/me/availability/exceptions/{ex_id}", headers=kh).json()["exceptions"] == []

# --- demo backdoor: on-screen codes for listed identifiers only --------------
os.environ["DEV_MODE"] = "0"
config.DEV_MODE = False
config.DEMO_IDENTIFIERS = ["+6598553704"]
config.ADMIN_PHONES = ["+6598553704"]

# the demo number gets its code on screen even with DEV_MODE off
r = c.post("/api/auth/request-code", json={"identifier": "9855 3704"}).json()
assert r["demo"] is True and r.get("dev_code"), r
# ...and it lands as an admin, approved, ready to match
r2 = c.post("/api/auth/verify", json={"identifier": "+6598553704", "code": r["dev_code"], "name": "Demo Admin"})
demo = r2.json()["user"]
assert demo["role"] == "admin" and demo["status"] == "approved", demo
assert demo["email"] is None, "demo admin is phone-only, separate from the email admin"
dh = {"Authorization": "Bearer " + r2.json()["token"]}
assert c.get("/api/admin/pending-users", headers=dh).status_code == 200, "demo admin must be able to approve"
assert c.get("/api/admin/assumptions", headers=dh).status_code == 200

# nobody else leaks a code — this is an allowlist, not a global switch
other = c.post("/api/auth/request-code", json={"identifier": "+6591112222"}).json()
assert "dev_code" not in other and not other.get("demo"), other
mail = c.post("/api/auth/request-code", json={"identifier": "priya@gmail.com"}).json()
assert "dev_code" not in mail and not mail.get("demo"), mail

# emptying the list closes the door immediately
config.DEMO_IDENTIFIERS = []
shut = c.post("/api/auth/request-code", json={"identifier": "9855 3704"}).json()
assert "dev_code" not in shut and not shut.get("demo"), shut

# --- SMS provider switch: sns <-> twilio without a code change ---------------
from backend.services import sms as smsmod
config.DEV_MODE = True          # so a failed send still returns a usable code
config.SMS_ENABLED = True

# an unknown provider must fail safe, never silently pretend to have sent
config.SMS_PROVIDER = "carrier-pigeon"
out = smsmod.send_otp_sms("+6591234567", "123456")
assert out["sent"] is False and out["dev_code"] == "123456", out

# twilio selected but unconfigured: reports not-sent rather than raising
config.SMS_PROVIDER = "twilio"
config.TWILIO_ACCOUNT_SID = ""
config.TWILIO_AUTH_TOKEN = ""
out = smsmod.send_otp_sms("+6591234567", "123456")
assert out["sent"] is False and out["dev_code"] == "123456", out

# both providers are wired to the same contract
assert set(smsmod._PROVIDERS) == {"sns", "twilio"}

# with SMS off entirely, the dev path still yields a code
config.SMS_ENABLED = False
assert smsmod.send_otp_sms("+6591234567", "123456")["dev_code"] == "123456"
config.SMS_PROVIDER = "sns"

# ---- v1.4 · notifications, automation toggles, pricing, PayNow -------------
from backend import settings as st
from backend.services import notify, matching

# every automation is off by default — nobody inherits it
base = c.get("/api/admin/settings", headers=ah).json()
assert base["auto_approve_kaki"] is False and base["auto_approve_caregiver"] is False
assert base["auto_match"] is False, base
assert c.get("/api/admin/settings", headers=ch).status_code == 403, "settings are admin-only"

# --- notification routing follows how the person signed in ---
assert notify.channel_for({"phone": "+6591234567", "phone_verified": True}) == "sms"
assert notify.channel_for({"email": "a@b.com", "email_verified": True}) == "email"
# verified channel wins over an unverified one
assert notify.channel_for({"phone": "+65911", "phone_verified": False,
                           "email": "a@b.com", "email_verified": True}) == "email"
# a captured-but-unverified number is still better than nothing
assert notify.channel_for({"phone": "+65911", "phone_verified": False}) == "sms"
assert notify.channel_for({}) is None
# a user with no contact route must not raise
assert notify.notify({}, "s", "t")["sent"] is False

# assignment notifies both sides and never breaks the assign
r = c.post("/api/visits", json={"service":"Companionship","tier":"planned","date":"2026-08-01",
                                "window":"09:00–11:00","language":"English"}, headers=ch).json()
res = c.post(f"/api/admin/visits/{r['id']}/assign", json={"kaki_id": kk2["id"]}, headers=ah).json()
assert "notified" in res and set(res["notified"]) == {"kaki", "caregiver"}, res
assert res["notified"]["kaki"]["channel"] in ("sms", "email"), res

# --- auto-approval ---
st.set_many({"auto_approve_caregiver": True}, "test")
_, newcg = login("autocg@example.com", role="caregiver", name="Auto CG")
assert newcg["status"] == "approved", "auto-approve caregiver should skip the queue"
_, newkk = login("autokk@example.com", role="kaki", name="Auto KK")
assert newkk["status"] == "pending", "kaki toggle is separate and still off"
st.set_many({"auto_approve_caregiver": False}, "test")

# --- auto-matching only ever picks a genuinely available kaki ---
# kk (Tan Bee Lian) is available Sat; give the fresh kaki no availability at all
sat = {"service":"Companionship","tier":"planned","date":"2026-08-01",
       "window":"09:00–11:00","language":"English"}
st.set_many({"auto_match": True}, "test")
auto = c.post("/api/visits", json=sat, headers=ch).json()
assert auto["status"] == "assigned", "auto-match should have filled a Saturday slot"
assert auto["kaki"]["id"] == kk["id"], auto["kaki"]

# a Monday nobody covers must stay for a human rather than be forced on someone
mon = dict(sat, date="2026-08-03")
left = c.post("/api/visits", json=mon, headers=ch).json()
assert left["status"] == "requested" and not left.get("kaki"), left
st.set_many({"auto_match": False}, "test")

# booking with the toggle off leaves the request alone
off = c.post("/api/visits", json=sat, headers=ch).json()
assert off["status"] == "requested", off

# the manual sweep works regardless of the toggle, urgent first
sweep = c.post("/api/admin/auto-match", headers=ah).json()
assert sweep["counts"]["matched"] >= 1, sweep
assert all(m["kaki"] for m in sweep["matched"]), sweep

# --- pricing editable from the admin panel, written to assumptions.json ---
r = c.put("/api/admin/assumptions/services",
          json={"services": {"Companionship": {"family_rate_per_hour": 30, "kaki_rate_per_hour": 14}}},
          headers=ah)
assert r.status_code == 200, r.text
svc = r.json()["services"]["Companionship"]
assert svc["family_rate_per_hour"] == 30 and svc["kaki_rate_per_hour"] == 14
assert "coordinator" in svc["source"].lower(), svc["source"]
# ...and it immediately drives new estimates
newv = c.post("/api/visits", json=dict(sat, date="2026-08-08"), headers=ch).json()
assert newv["estimate"]["base"] == svc["hours"] * 30, newv["estimate"]
# junk and unknown services are rejected, not silently written
assert c.put("/api/admin/assumptions/services",
             json={"services": {"Nope": {"hours": 1}}}, headers=ah).status_code == 400
assert c.put("/api/admin/assumptions/services",
             json={"services": {"Companionship": {"hours": -3}}}, headers=ah).status_code == 400
assert c.put("/api/admin/assumptions/services",
             json={"services": {"Companionship": {"hours": 2}}}, headers=ch).status_code == 403

# --- PayNow ---
r = c.put("/api/admin/settings", json={"paynow_type": "uen", "paynow_value": "202512345K",
                                       "paynow_name": "Vanguard Healthcare"}, headers=ah).json()
assert r["paynow_value"] == "202512345K" and r["paynow_name"] == "Vanguard Healthcare"
assert c.put("/api/admin/settings", json={"paynow_type": "carrier-pigeon"},
             headers=ah).status_code == 400
# caregivers get it in their app config, without needing admin rights
cfg = c.get("/api/auth/me", headers=ch).json()["config"]
assert cfg["paynow"]["configured"] is True and cfg["paynow"]["value"] == "202512345K", cfg["paynow"]
# unknown setting keys are ignored rather than stored
st.set_many({"totally_made_up": "x"}, "test")
assert "totally_made_up" not in st.all()

# ---- v1.5 · auth hardening (ISO 5055 security) -----------------------------
from backend.services import ratelimit

# unlimited code requests would let an attacker run up the SMS bill and hammer
# a caregiver's phone (CWE-770)
ratelimit.clear("request_code_identifier", "+6591234567")
limit, _ = ratelimit.LIMITS["request_code_identifier"]
for i in range(limit):
    _unthrottle_ip()
    assert c.post("/api/auth/request-code", json={"identifier": "9123 4567"}).status_code == 200, i
_unthrottle_ip()
blocked = c.post("/api/auth/request-code", json={"identifier": "9123 4567"})
assert blocked.status_code == 429, blocked.status_code
assert "coordinator" in blocked.json()["detail"], "lockout must offer a human route out"

# a different identifier is unaffected — the limit is per person, not global
_unthrottle_ip()
assert c.post("/api/auth/request-code", json={"identifier": "8222 3333"}).status_code == 200

# the per-IP cap catches an attacker cycling through many identifiers.
# It is deliberately loose — a room of people shares one address, and the
# tabletop exercise is fifteen-plus sign-ins from a single wifi.
ip_limit, _ = ratelimit.LIMITS["request_code_ip"]
assert ip_limit >= 100, f"per-IP cap {ip_limit} would lock out a room on one network"
ratelimit.clear("request_code_ip", "testclient")
for i in range(ip_limit):
    ratelimit.record("request_code_ip", "testclient")
spread = c.post("/api/auth/request-code", json={"identifier": "8777 6666"})
assert spread.status_code == 429, "per-IP cap should stop identifier-cycling"
_unthrottle_ip()

# unlimited guesses would make a 6-digit code walkable inside its 10-min window
ratelimit.clear("verify_failure", "+6582223333")
ratelimit.clear("request_code_identifier", "+6582223333")
vlimit, _ = ratelimit.LIMITS["verify_failure"]
for i in range(vlimit):
    _unthrottle_ip()
    r = c.post("/api/auth/verify", json={"identifier": "8222 3333", "code": "000000"})
    assert r.status_code == 400, (i, r.status_code)
locked = c.post("/api/auth/verify", json={"identifier": "8222 3333", "code": "000000"})
assert locked.status_code == 429, locked.status_code

# a real sign-in clears the counters, so a fumbled digit doesn't strand someone
ratelimit.clear("verify_failure", "+6582223333")
ratelimit.clear("request_code_identifier", "+6582223333")
_unthrottle_ip()
good = c.post("/api/auth/request-code", json={"identifier": "8222 3333"}).json()
ratelimit.record("verify_failure", "+6582223333")     # one earlier fumble
_vr = c.post("/api/auth/verify", json={"identifier": "8222 3333", "code": good.get("dev_code"),
                                       "role": "caregiver", "name": "Rate Test"})
assert _vr.status_code == 200, (good, _vr.status_code, _vr.text)
assert ratelimit.count("verify_failure", "+6582223333", 15) == 0, "success must reset the counter"

# failed attempts are auditable
assert db.q("SELECT count(*) c FROM audit_log WHERE action = 'login_failed'")[0]["c"] >= vlimit

# the interactive API docs must not be public once real care data is in the box
assert app.docs_url is None and app.openapi_url is None, "API docs should be off by default"

# ---- v1.5 · endpoints that had no coverage at all ---------------------------
# These were reachable in production but never exercised by a test, which is
# how a broken decline or cancel button reaches a caregiver unnoticed.

# a kaki can pass a visit back to the coordinator
dv = c.post("/api/visits", json={"service":"Wellness check","tier":"planned","date":"2026-08-01",
                                 "window":"09:00–11:00","language":"English"}, headers=ch).json()
c.post(f"/api/admin/visits/{dv['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah)
r = c.post(f"/api/visits/{dv['id']}/decline", headers=kh)
assert r.status_code == 200 and r.json()["status"] == "requested", r.text
assert r.json().get("kaki") is None, "declining must release the kaki, not keep them attached"

# a caregiver can cancel their own visit, and only their own
cv2 = c.post("/api/visits", json={"service":"Companionship","tier":"planned","date":"2026-08-01",
                                  "window":"09:00–11:00","language":"English"}, headers=ch).json()
assert c.post(f"/api/visits/{cv2['id']}/cancel", headers=kh).status_code == 403, "kaki must not cancel"
r = c.post(f"/api/visits/{cv2['id']}/cancel", headers=ch)
assert r.status_code == 200 and r.json()["status"] == "cancelled", r.text

# the full user list backs the admin roster screen
users = c.get("/api/admin/users", headers=ah).json()
assert any(u["role"] == "kaki" and "kaki" in u for u in users), "kaki rows must carry their profile"
assert c.get("/api/admin/users", headers=ch).status_code == 403

# suspend blocks immediately — a token issued before suspension must stop working
sus_h, sus_u = login("suspendme@example.com", role="caregiver", name="Suspend Me")
c.post(f"/api/admin/users/{sus_u['id']}/approve", json={}, headers=ah)
assert c.get("/api/care/household", headers=sus_h).status_code in (200, 404)
assert c.post(f"/api/admin/users/{sus_u['id']}/suspend", headers=ah).status_code == 200
assert c.post("/api/visits", json={"service":"Companionship","tier":"planned","date":"2026-08-01",
                                   "window":"09:00–11:00","language":"English"},
              headers=sus_h).status_code == 403, "suspension must take effect on the existing session"
# an admin cannot lock themselves out
assert c.post(f"/api/admin/users/{admin['id']}/suspend", headers=ah).status_code == 400

# profile round-trips, and a kaki's availability rides along with it
prof = c.get("/api/users/me/profile", headers=kh).json()
assert prof["role"] == "kaki" and "availability" in prof["kaki"], prof

# the help bot answers. Without a key it serves the built-in guide; with one it
# reaches the provider. Either way it must never return an empty reply.
for q in ["How do I book a visit?", "What is the start code?", "When am I approved?"]:
    rep = c.post("/api/chat", json={"message": q}, headers=ch)
    assert rep.status_code == 200 and len(rep.json()["reply"]) > 20, (q, rep.text)
# it holds a conversation rather than treating each turn as the first
rep = c.post("/api/chat", json={"message": "and what if I cancel?",
                                "history": [{"role": "user", "content": "how do I book?"},
                                            {"role": "assistant", "content": "Home then Book a visit."}]},
             headers=ch)
assert rep.status_code == 200 and rep.json()["reply"], rep.text
# Signed OUT it must still answer — the help button is on the sign-in screen,
# and "how do I sign in?" is exactly what a confused caregiver asks there.
# This returned 401 in production; the error text told them nothing.
anon = c.post("/api/chat", json={"message": "how do I sign in?"})
assert anon.status_code == 200, anon.text
assert anon.json()["source"] == "guide", "signed-out help must not call a paid provider"
assert "code" in anon.json()["reply"].lower(), anon.json()["reply"]
# an invalid or expired token degrades to the guide rather than erroring
bad = c.post("/api/chat", json={"message": "how do I book?"},
             headers={"Authorization": "Bearer not-a-real-token"})
assert bad.status_code == 200 and bad.json()["source"] == "guide", bad.text
# signed in, it reaches the assistant path
assert c.post("/api/chat", json={"message": "how do I book?"}, headers=ch).json()["source"] == "assistant"

# ---- v1.6 · Buckets 1 and 2 after the August feedback round ----------------
# Each block below is one feature from knowledge/prototype/feature-buckets-2026-09-04.md.
# [B1·4] a same-day window that has already passed is refused, whatever the tier.
# Seniors saw "Today, 2–5pm" offered for an urgent visit at 6pm on 21 Aug.
assert _visits.window_end_hour("Today, 9am–12") == 12 and _visits.window_end_hour("Afternoon 2–5") == 17
assert _visits.window_end_hour("Today, 6–9pm") == 21 and _visits.window_end_hour("Within the hour") is None
_visits._now = lambda: _dt.datetime(2026, 7, 25, 18, 30)
late = c.post("/api/visits", json={"service": "Companionship", "tier": "urgent", "date": "today",
                                   "window": "Today, 2–5pm", "language": "English"}, headers=ch)
assert late.status_code == 400 and "passed" in late.json()["detail"], late.text
ok_win = c.post("/api/visits", json={"service": "Companionship", "tier": "urgent", "date": "today",
                                     "window": "Today, 6–9pm", "language": "English"}, headers=ch)
assert ok_win.status_code == 200, ok_win.text
# "within the hour" is always fine — it is relative to now
assert c.post("/api/visits", json={"service": "Companionship", "tier": "urgent", "date": "today",
                                   "window": "Within the hour", "language": "English"}, headers=ch).status_code == 200
# a window on a future date is never "passed"
assert c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-10",
                                   "window": "Afternoon 2–5", "language": "English"}, headers=ch).status_code == 200
_visits._now = lambda: _PINNED_NOW

# [B1·5] the caregiver hears when the kaki confirms, passes back, or cancels.
# On 21 Aug caregivers refreshed the page to find out. Record every outbound
# message instead of sending it.
from backend.services import emailer as _em, sms as _sms, notify as _notify
_sent = []
_orig_email, _orig_sms = _em.send_email, _sms.send_sms
_em.send_email = lambda to, subject, html: (_sent.append(("email", to, subject, html)) or True)
_sms.send_sms = lambda to, text: (_sent.append(("sms", to, "", text)) or True)

def _texts_to(identifier):
    return [m[2] + " " + m[3] for m in _sent if m[1] == identifier]

v16 = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-11",
                                  "window": "Afternoon 2–5", "language": "English"}, headers=ch).json()
_sent.clear()
assert c.post(f"/api/admin/visits/{v16['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
assert any("matched" in t.lower() for t in _texts_to("priya@example.com")), _sent
_sent.clear()
assert c.post(f"/api/visits/{v16['id']}/decline", headers=kh).status_code == 200
assert any("passed" in t.lower() and "back" in t.lower() for t in _texts_to("priya@example.com")), _sent
# re-assign, accept: caregiver told the kaki confirmed
assert c.post(f"/api/admin/visits/{v16['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
_sent.clear()
assert c.post(f"/api/visits/{v16['id']}/accept", headers=kh).status_code == 200
assert any("confirmed" in t.lower() for t in _texts_to("priya@example.com")), _sent
# caregiver cancels: the kaki is told
_sent.clear()
assert c.post(f"/api/visits/{v16['id']}/cancel", headers=ch).status_code == 200
assert any("cancel" in t.lower() for t in _texts_to("beelian@example.com")), _sent
# nothing was sent to the wrong side
assert not _texts_to("priya@example.com"), _sent

# [B1·6] the kaki's assignment message says the hours and what the task is.
# "when kaki receive a request, they should know the hours as well" — 21 Aug.
v16b = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-12",
                                   "window": "Morning 9–12", "language": "English"}, headers=ch).json()
_sent.clear()
assert c.post(f"/api/admin/visits/{v16b['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
_kaki_msgs = _texts_to("beelian@example.com")
assert _kaki_msgs, _sent
_m = " ".join(_kaki_msgs)
assert "Companionship" in _m and "2026-08-12" in _m, _m
assert "2 hr" in _m, "hours missing from the kaki's message: " + _m
assert "Conversation" in _m, "task description missing from the kaki's message: " + _m
assert c.post(f"/api/visits/{v16b['id']}/cancel", headers=ch).status_code == 200
# the help guide answers the 'do I keep the app open' question
_g = c.post("/api/chat", json={"message": "do I need to keep the app open?"}).json()
assert "open" in _g["reply"].lower() and "message" in _g["reply"].lower(), _g

# [B1·7] "I'm on my way" — the cheapest possible ETA. Asked for by all three
# 21 Aug sources and by NCSS.
v16c = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-13",
                                   "window": "Morning 9–12", "language": "English"}, headers=ch).json()
assert c.post(f"/api/admin/visits/{v16c['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
# not before accepting
assert c.post(f"/api/visits/{v16c['id']}/on-the-way", headers=kh).status_code == 400
assert c.post(f"/api/visits/{v16c['id']}/accept", headers=kh).status_code == 200
_sent.clear()
otw = c.post(f"/api/visits/{v16c['id']}/on-the-way", headers=kh)
assert otw.status_code == 200 and otw.json()["on_way_at"], otw.text
assert any("on the way" in t.lower() or "on their way" in t.lower() for t in _texts_to("priya@example.com")), _sent
# the caregiver's view carries it; the caregiver cannot press it
assert c.get(f"/api/visits/{v16c['id']}", headers=ch).json()["on_way_at"]
# the kaki never receives the start code, on ANY response — review finding B1
assert "otp_code" not in otw.json(), otw.json().keys()
assert all("otp_code" not in v for v in c.get("/api/visits", headers=kh).json())
assert "otp_code" not in c.post(f"/api/visits/{v16c['id']}/on-the-way", headers=kh).json()
assert c.post(f"/api/visits/{v16c['id']}/on-the-way", headers=ch).status_code == 403
assert c.post(f"/api/visits/{v16c['id']}/cancel", headers=ch).status_code == 200

# [B1·8] languages: Cantonese exists, a visit can carry several, matching
# credits any overlap, and the care plan's languages are what the booking
# starts from (asked for on 21 Aug and by NCSS on 18 Aug).
assert "Cantonese" in config.LANGUAGES
assert "Cantonese" in c.get("/api/auth/me", headers=ch).json()["config"]["languages"]
v16d = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-14",
                                   "window": "Morning 9–12", "languages": ["Cantonese", "Mandarin"]}, headers=ch)
assert v16d.status_code == 200, v16d.text
v16d = v16d.json()
assert v16d["languages"] == ["Cantonese", "Mandarin"] and v16d["language"] == "Cantonese", v16d
# a kaki who speaks only Mandarin still counts as a language match
assert c.put("/api/users/me", json={"languages": ["Mandarin"]}, headers=kh).status_code == 200
_roster = c.get(f"/api/admin/kakis?visit_id={v16d['id']}", headers=ah).json()
_me = next(r for r in _roster if r["id"] == kk["id"])
assert _me["language_ok"] is True, _me
from backend.services import matching as _matching
assert _matching.score({"id": kk["id"]}, db.one("SELECT * FROM visits WHERE id = ?", [v16d["id"]]))["language_ok"]
# the legacy single 'language' field still works on its own
assert c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-14",
                                   "window": "Morning 9–12", "language": "Hokkien"}, headers=ch).json()["languages"] == ["Hokkien"]
assert c.post(f"/api/visits/{v16d['id']}/cancel", headers=ch).status_code == 200

# [B1·9] care plan: bedridden as a mobility option; emergency contact split
# into name / relationship / phone (NCSS 2.6). Caregivers can edit their own
# name and phone (NCSS 2.1).
_plan = c.put("/api/care/plan", json={"meds": "Metformin 2pm", "mobility": "Bedridden", "languages": ["Tamil"],
                                      "contact_name": "Ravi", "contact_relationship": "Son", "contact_phone": "9111 2222",
                                      "notes": ""}, headers=ch)
assert _plan.status_code == 200, _plan.text
_pl = _plan.json()["plan"]
assert _pl["mobility"] == "Bedridden" and _pl["contact_name"] == "Ravi" and _pl["contact_relationship"] == "Son"
assert _pl["contact_phone"] == "+6591112222", _pl        # normalised to E.164 like every other number
assert c.put("/api/care/plan", json={"contact_phone": "not a number"}, headers=ch).status_code == 400
_prof = c.put("/api/users/me", json={"name": "Priya Nathan", "phone": "9333 4444"}, headers=ch)
assert _prof.status_code == 200 and _prof.json()["name"] == "Priya Nathan", _prof.text
assert c.get("/api/auth/me", headers=ch).json()["user"]["name"] == "Priya Nathan"
assert _prof.json()["phone"] == "+6593334444", _prof.json()
# a phone-only account cannot retype its own sign-in number (it would lock them out)
assert c.put("/api/users/me", json={"phone": "9555 6666"}, headers=ph).status_code == 400
assert c.get("/api/auth/me", headers=ph).json()["user"]["phone"] == "+6591234567"
# a changed number on an email account is stored unverified until a code is used on it
assert c.get("/api/auth/me", headers=ch).json()["user"]["phone_verified"] is False
# a number that belongs to someone else is refused (the kaki's number was set in v1.2 tests)
assert c.put("/api/users/me", json={"phone": "9123 4567"}, headers=ch).status_code == 400

# [B1·10] "Other — tell us" on the trigger step (NCSS 2.20) and a horizon on
# how far ahead a planned visit can be booked (NCSS 2.15), as a setting.
assert c.get("/api/admin/settings", headers=ah).json()["max_advance_days"] == 30
assert c.get("/api/auth/me", headers=ch).json()["config"]["max_advance_days"] == 30
assert c.put("/api/admin/settings", json={"max_advance_days": 7}, headers=ah).json()["max_advance_days"] == 7
assert c.put("/api/admin/settings", json={"max_advance_days": 0}, headers=ah).status_code == 400
_far = (_PINNED_NOW.date() + _dt.timedelta(days=10)).isoformat()
_near = (_PINNED_NOW.date() + _dt.timedelta(days=5)).isoformat()
_r = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": _far,
                                 "window": "Morning 9–12", "language": "English"}, headers=ch)
assert _r.status_code == 400 and "7 days" in _r.json()["detail"], _r.text
_r = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": _near,
                                 "window": "Morning 9–12", "language": "English", "trigger": "Other: cataract op"}, headers=ch)
assert _r.status_code == 200 and _r.json()["trigger"] == "Other: cataract op", _r.text
assert c.post(f"/api/visits/{_r.json()['id']}/cancel", headers=ch).status_code == 200
assert c.put("/api/admin/settings", json={"max_advance_days": 30}, headers=ah).json()["max_advance_days"] == 30

# [B1·11] the emergency contact hears when a visit starts and ends
# (facilitators' feedback, 21 Aug). Priya's plan has Ravi on +6591112222 from B1·9.
v16e = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-15",
                                   "window": "Morning 9–12", "language": "English"}, headers=ch).json()
assert c.post(f"/api/admin/visits/{v16e['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
assert c.post(f"/api/visits/{v16e['id']}/accept", headers=kh).status_code == 200
_otp16 = reveal_start_code(v16e["id"], ch, kh)
_sent.clear()
assert c.post(f"/api/visits/{v16e['id']}/start", json={"otp": _otp16}, headers=kh).status_code == 200
_ravi = [m for m in _sent if m[1] == "+6591112222"]
assert _ravi and "started" in _ravi[0][3].lower() and "Tan Bee Lian" in _ravi[0][3], _sent
_sent.clear()
assert c.post(f"/api/visits/{v16e['id']}/complete", json={"chips": ["Went well"], "text": "ok"}, headers=kh).status_code == 200
_ravi = [m for m in _sent if m[1] == "+6591112222"]
assert _ravi and "finished" in _ravi[0][3].lower(), _sent
# no contact on file → nothing sent, nothing breaks
assert c.put("/api/care/plan", json={"meds": "Metformin 2pm", "mobility": "Bedridden", "languages": ["Tamil"]}, headers=ch).status_code == 200
v16f = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-15",
                                   "window": "Morning 9–12", "language": "English"}, headers=ch).json()
assert c.post(f"/api/admin/visits/{v16f['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
assert c.post(f"/api/visits/{v16f['id']}/accept", headers=kh).status_code == 200
_sent.clear()
assert c.post(f"/api/visits/{v16f['id']}/start", json={"otp": reveal_start_code(v16f["id"], ch, kh)}, headers=kh).status_code == 200
assert not [m for m in _sent if m[1] == "+6591112222"]
assert c.post(f"/api/visits/{v16f['id']}/complete", json={"chips": [], "text": "ok"}, headers=kh).status_code == 200

# ---- Bucket 2 --------------------------------------------------------------
# [B2·1] exact start and end in 30-minute steps; hours prorated to the half
# hour at the same rate, minimum 1 hour; kaki availability by day and hours.
_svc = c.get("/api/admin/assumptions", headers=ah).json()["services"]["Companionship"]   # rates were edited above
_r = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                 "start_time": "09:30", "end_time": "11:30", "language": "English"}, headers=ch)
assert _r.status_code == 200, _r.text
_v = _r.json()
assert _v["hours"] == 2.0 and _v["window"] == "09:30–11:30", _v
assert _v["estimate"]["hours"] == 2.0 and _v["estimate"]["base"] == 2.0 * _svc["family_rate_per_hour"], _v["estimate"]
assert _v["estimate"]["kaki_fee"] == 2.0 * _svc["kaki_rate_per_hour"]
_r = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                 "start_time": "10:00", "end_time": "10:30", "language": "English"}, headers=ch)
assert _r.status_code == 200 and _r.json()["hours"] == 1.0, _r.text   # half an hour is charged as the 1-hour minimum
_r = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                 "start_time": "10:00", "end_time": "12:30", "language": "English"}, headers=ch)
assert _r.status_code == 200 and _r.json()["hours"] == 2.5, _r.text
assert c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                   "start_time": "11:00", "end_time": "10:00", "language": "English"}, headers=ch).status_code == 400
assert c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                   "start_time": "10:10", "end_time": "12:00", "language": "English"}, headers=ch).status_code == 400
# without times, the service default still applies
_r = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                 "window": "Morning 9–12", "language": "English"}, headers=ch).json()
assert _r["hours"] == _svc["hours"], _r
# a same-day exact window that has ended is refused (the after-5pm rule, now to the minute)
_visits._now = lambda: _dt.datetime(2026, 7, 25, 11, 40)
assert c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-07-25",
                                   "start_time": "09:30", "end_time": "11:30", "language": "English"}, headers=ch).status_code == 400
_visits._now = lambda: _PINNED_NOW

# kaki availability by hours; the half-day API still works and the two agree
_r = c.put("/api/users/me/availability",
           json={"weekly": {"Tue": {"from": "09:00", "to": "12:00"}, "Sat": {"from": "08:00", "to": "18:00"}}}, headers=kh)
assert _r.status_code == 200, _r.text
assert _r.json()["weekly_hours"]["Tue"] == {"from": "09:00", "to": "12:00"}, _r.json()
assert _r.json()["weekly"]["Tue"] == ["morning"] and sorted(_r.json()["weekly"]["Sat"]) == ["afternoon", "morning"]
assert _r.json()["weekly_hours"]["Wed"] is None
assert c.put("/api/users/me/availability", json={"weekly": {"Tue": {"from": "09:10", "to": "12:00"}}}, headers=kh).status_code == 400
assert c.put("/api/users/me/availability", json={"weekly": {"Tue": {"from": "12:00", "to": "09:00"}}}, headers=kh).status_code == 400
# 2026-08-18 is a Tuesday
assert availmod.check(kk["id"], "2026-08-18", "09:30–11:30")["state"] == "available"
_fit = availmod.check(kk["id"], "2026-08-18", "11:30–13:30")
assert _fit["state"] == "unavailable" and "09:00" in _fit["why"], _fit
assert availmod.check(kk["id"], "2026-08-18", "Morning 9–12")["state"] == "available"     # legacy windows still map
assert availmod.check(kk["id"], "2026-08-19", "09:30–11:30")["state"] == "unavailable"     # Wednesday: nothing set
# legacy half-day storage still reads as hours
db.run("UPDATE kaki_profiles SET weekly_slots = ? WHERE user_id = ?", ['{"Thu": ["afternoon"]}', kk["id"]])
assert availmod.weekly_hours(kk["id"])["Thu"] == {"from": "13:00", "to": "18:00"}, availmod.weekly_hours(kk["id"])
assert availmod.check(kk["id"], "2026-08-20", "14:00–16:00")["state"] == "available"
db.run("UPDATE kaki_profiles SET weekly_slots = ? WHERE user_id = ?", ['{"Tue": {"from": "09:00", "to": "12:00"}, "Sat": {"from": "08:00", "to": "18:00"}}', kk["id"]])

# [B2·2] the kaki's photo: uploaded on the profile, shown to the caregiver on
# the visit (every 21 Aug source, and NCSS 3.1). Base64 in the database, capped.
import base64 as _b64
_png = "data:image/png;base64," + _b64.b64encode(b"\x89PNG\r\n\x1a\n" + b"0" * 200).decode()
assert c.put("/api/users/me/photo", json={"data_url": _png}, headers=kh).status_code == 200
assert c.get("/api/users/me/profile", headers=kh).json()["photo"] == _png
_big = "data:image/jpeg;base64," + _b64.b64encode(b"\xff\xd8" + b"0" * (260 * 1024)).decode()
assert c.put("/api/users/me/photo", json={"data_url": _big}, headers=kh).status_code == 413
assert c.put("/api/users/me/photo", json={"data_url": "data:text/html;base64,PGI+"}, headers=kh).status_code == 400
assert c.put("/api/users/me/photo", json={"data_url": _png}, headers=ch).status_code == 403   # caregivers have no kaki photo
v16g = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-19",
                                   "start_time": "09:00", "end_time": "11:00", "language": "English"}, headers=ch).json()
assert c.post(f"/api/admin/visits/{v16g['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
assert c.get(f"/api/visits/{v16g['id']}", headers=ch).json()["kaki"]["photo"] == _png
# a fresh assignment gets a fresh kaki code; declining clears it
_kc1 = c.get(f"/api/visits/{v16g['id']}", headers=kh).json()["kaki_code"]
assert c.post(f"/api/visits/{v16g['id']}/decline", headers=kh).status_code == 200
assert c.post(f"/api/admin/visits/{v16g['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
assert c.get(f"/api/visits/{v16g['id']}", headers=ch).json()["kaki_verified_at"] is None
assert c.post(f"/api/visits/{v16g['id']}/cancel", headers=ch).status_code == 200
assert c.put("/api/users/me/photo", json={"data_url": ""}, headers=kh).status_code == 200   # remove

# [B2·3] gender preference: on the kaki profile, on the request, sorts the
# coordinator's roster, and gates auto-match. "May not want a man to visit" —
# every 21 Aug source, and NCSS.
assert c.put("/api/users/me", json={"gender": "female"}, headers=kh).status_code == 200      # Bee Lian
assert c.get("/api/users/me/profile", headers=kh).json()["kaki"]["gender"] == "female"
assert c.put("/api/users/me", json={"gender": "other-thing"}, headers=kh).status_code == 400
kh_m, kk_m = login("boon@example.com", role="kaki", name="Wong Boon")
assert c.post(f"/api/admin/users/{kk_m['id']}/approve", json={"role": "kaki"}, headers=ah).status_code == 200
kh_m, kk_m = login("boon@example.com")
assert c.put("/api/users/me", json={"gender": "male", "services": ["Companionship"], "languages": ["English"]}, headers=kh_m).status_code == 200
# 2026-08-18 is a Tuesday; Boon is available all day, Bee Lian 09:00–12:00 (set in B2·1)
assert c.put("/api/users/me/availability", json={"weekly": {"Tue": {"from": "08:00", "to": "20:00"}}}, headers=kh_m).status_code == 200
_r = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                 "start_time": "09:30", "end_time": "11:30", "language": "English",
                                 "kaki_gender_pref": "female"}, headers=ch)
assert _r.status_code == 200 and _r.json()["kaki_gender_pref"] == "female", _r.text
_vg = _r.json()
assert c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                   "start_time": "09:30", "end_time": "11:30", "language": "English",
                                   "kaki_gender_pref": "robot"}, headers=ch).status_code == 400
_roster = c.get(f"/api/admin/kakis?visit_id={_vg['id']}", headers=ah).json()
_bl = next(r for r in _roster if r["id"] == kk["id"]); _bn = next(r for r in _roster if r["id"] == kk_m["id"])
assert _bl["gender"] == "female" and _bl["gender_ok"] is True and _bn["gender_ok"] is False, (_bl, _bn)
assert _roster.index(_bl) < _roster.index(_bn), "a matching preference sorts first"
assert _bn in _roster, "sorts, never filters — the coordinator can still assign against the preference"
_ranked = _matching.rank(db.one("SELECT * FROM visits WHERE id = ?", [_vg["id"]]))
assert _ranked[0]["id"] == kk["id"] and _ranked[0]["score"]["gender_ok"] is True
# auto-match never assigns against a stated preference, even if the only available kaki mismatches
_vg2 = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                   "start_time": "14:00", "end_time": "16:00", "language": "English",
                                   "kaki_gender_pref": "female"}, headers=ch).json()   # Bee Lian off in the afternoon; Boon free
assert _matching.best_available(db.one("SELECT * FROM visits WHERE id = ?", [_vg2["id"]])) is None
_vg3 = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                   "start_time": "14:00", "end_time": "16:00", "language": "English"}, headers=ch).json()
assert _matching.best_available(db.one("SELECT * FROM visits WHERE id = ?", [_vg3["id"]]))["id"] == kk_m["id"]
for _x in (_vg, _vg2, _vg3):
    assert c.post(f"/api/visits/{_x['id']}/cancel", headers=ch).status_code == 200

# [B2·4] "ask for the same person again" — 21 Aug. Homage calls it continuity.
# Priya's household has completed visits with Bee Lian by now.
_past = c.get("/api/visits/past-kakis", headers=ch)
assert _past.status_code == 200, _past.text
_pk = next((k for k in _past.json() if k["id"] == kk["id"]), None)
assert _pk and _pk["times"] >= 1 and _pk["name"] == "Tan Bee Lian" and "photo" in _pk, _past.json()
assert c.get("/api/visits/past-kakis", headers=kh).status_code == 403
_r = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                 "start_time": "09:30", "end_time": "11:30", "language": "English",
                                 "preferred_kaki_id": kk["id"]}, headers=ch)
assert _r.status_code == 200 and _r.json()["preferred_kaki"]["name"] == "Tan Bee Lian", _r.text
_vp = _r.json()
# a kaki you have never had cannot be "requested again"
assert c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                   "start_time": "09:30", "end_time": "11:30", "language": "English",
                                   "preferred_kaki_id": "nobody"}, headers=ch).status_code == 400
_roster = c.get(f"/api/admin/kakis?visit_id={_vp['id']}", headers=ah).json()
assert _roster[0]["id"] == kk["id"] and _roster[0]["preferred"] is True, _roster[0]
assert _matching.rank(db.one("SELECT * FROM visits WHERE id = ?", [_vp["id"]]))[0]["id"] == kk["id"]
# auto-match honours it when the preferred kaki is available (Tue 09:00–12:00: yes)
assert _matching.best_available(db.one("SELECT * FROM visits WHERE id = ?", [_vp["id"]]))["id"] == kk["id"]
assert c.post(f"/api/visits/{_vp['id']}/cancel", headers=ch).status_code == 200

# [B2·5] the kaki sees what the task needs. Household help: name, address,
# task, mobility, emergency contact — not age, meds or the family's notes.
# Every other service: the full care plan. (21 Aug: "may not need to know the
# age of the elderly if doing household chores".)
assert c.put("/api/care/plan", json={"meds": "Metformin 2pm", "mobility": "Bedridden", "languages": ["Tamil"],
                                     "contact_name": "Ravi", "contact_relationship": "Son", "contact_phone": "9111 2222",
                                     "notes": "Gets anxious with new faces"}, headers=ch).status_code == 200
assert c.put("/api/users/me", json={"services": ["Companionship", "Household help", "Chaperone"]}, headers=kh).status_code == 200
def _kaki_view(service):
    v = c.post("/api/visits", json={"service": service, "tier": "planned", "date": "2026-08-18",
                                    "start_time": "09:30", "end_time": "10:30", "language": "English"}, headers=ch).json()
    assert c.post(f"/api/admin/visits/{v['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
    out = c.get(f"/api/visits/{v['id']}", headers=kh).json()
    return v["id"], out
_hid, _hh = _kaki_view("Household help")
assert _hh["senior_name"] == "Mr Nathan" and _hh["address"], _hh
assert _hh["senior_age"] is None and _hh["minimised"] is True, _hh
assert _hh["care_plan"]["meds"] is None and _hh["care_plan"]["notes"] is None, _hh["care_plan"]
assert _hh["care_plan"]["mobility"] == "Bedridden" and _hh["care_plan"]["contact_phone"] == "+6591112222", _hh["care_plan"]
# the caregiver and the coordinator still see everything on the same visit
assert c.get(f"/api/visits/{_hid}", headers=ch).json()["senior_age"] == 78
assert c.get(f"/api/visits/{_hid}", headers=ah).json()["care_plan"]["meds"] == "Metformin 2pm"
_cid, _cc = _kaki_view("Companionship")
assert _cc["senior_age"] == 78 and _cc["minimised"] is False and _cc["care_plan"]["meds"] == "Metformin 2pm", _cc
# the list view is minimised the same way
assert next(v for v in c.get("/api/visits", headers=kh).json() if v["id"] == _hid)["senior_age"] is None
for _x in (_hid, _cid):
    assert c.post(f"/api/visits/{_x}/cancel", headers=ch).status_code == 200

# [B2·6] cancellation is a lifecycle, not a pre-arrival button. Either side,
# after accept and after start, with a reason and who-cancelled recorded.
# Compensation stays a policy question for Vanguard/NCSS.
def _booked_and_accepted():
    v = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                    "start_time": "09:30", "end_time": "10:30", "language": "English"}, headers=ch).json()
    assert c.post(f"/api/admin/visits/{v['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
    assert c.post(f"/api/visits/{v['id']}/accept", headers=kh).status_code == 200
    return v["id"]
# kaki cancels an accepted visit → back to 'requested', kaki cleared, reason kept, caregiver told
_x = _booked_and_accepted(); _sent.clear()
assert c.post(f"/api/visits/{_x}/cancel", json={}, headers=kh).status_code == 400          # a reason is required from the kaki
_r = c.post(f"/api/visits/{_x}/cancel", json={"reason": "Fever"}, headers=kh)
assert _r.status_code == 200 and _r.json()["status"] == "requested" and _r.json()["kaki"] is None, _r.text
_row = db.one("SELECT * FROM visits WHERE id = ?", [_x])
assert _row["cancelled_by"] == "kaki" and _row["cancel_reason"] == "Fever" and _row["kaki_id"] is None, _row
assert any("Fever" in t and "cancel" in t.lower() for t in _texts_to("priya@example.com")), _sent
assert c.get(f"/api/visits/{_x}", headers=ch).json()["last_cancellation"]["by"] == "kaki"
# the same visit can be re-matched and the old kaki code is gone
assert c.post(f"/api/admin/visits/{_x}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
assert c.post(f"/api/visits/{_x}/cancel", json={"reason": "Change of plan"}, headers=ch).status_code == 200
# caregiver cancels mid-visit → 'cancelled', who and why recorded, kaki told
_y = _booked_and_accepted()
assert c.post(f"/api/visits/{_y}/start", json={"otp": reveal_start_code(_y, ch, kh)}, headers=kh).status_code == 200
_sent.clear()
_r = c.post(f"/api/visits/{_y}/cancel", json={"reason": "Feeling unwell, please go"}, headers=ch)
assert _r.status_code == 200 and _r.json()["status"] == "cancelled", _r.text
_row = db.one("SELECT * FROM visits WHERE id = ?", [_y])
assert _row["cancelled_by"] == "caregiver" and "unwell" in _row["cancel_reason"] and _row["cancelled_at"], _row
assert any("cancel" in t.lower() for t in _texts_to("beelian@example.com")), _sent
# kaki cancels mid-visit → 'cancelled' with reason; the coordinator sees it in quality
_z = _booked_and_accepted()
assert c.post(f"/api/visits/{_z}/start", json={"otp": reveal_start_code(_z, ch, kh)}, headers=kh).status_code == 200
assert c.post(f"/api/visits/{_z}/cancel", json={"reason": "Family asked me to leave early"}, headers=kh).status_code == 200
assert db.one("SELECT status, cancelled_by FROM visits WHERE id = ?", [_z]) == {"status": "cancelled", "cancelled_by": "kaki"}
_q = c.get("/api/admin/quality", headers=ah).json()
assert any(x["id"] == _z for x in _q["cancellations"]), _q.keys()
# nobody can cancel a completed or an already-cancelled visit
assert c.post(f"/api/visits/{_hid}/cancel", json={"reason": "x"}, headers=ch).status_code == 400   # cancelled above
assert c.post(f"/api/visits/{v16e['id']}/cancel", json={"reason": "x"}, headers=ch).status_code == 400   # completed in B1·11
assert c.post(f"/api/visits/{v16e['id']}/cancel", json={"reason": "x"}, headers=ah).status_code == 400
# admin can cancel with a reason
_w = _booked_and_accepted()
assert c.post(f"/api/visits/{_w}/cancel", json={"reason": "Coordinator: kaki reassigned"}, headers=ah).status_code == 200
assert db.one("SELECT cancelled_by FROM visits WHERE id = ?", [_w])["cancelled_by"] == "admin"

# [B2·7] certificates on the kaki profile, visible to the coordinator at
# approval (NCSS 1.5; committed to Vanguard on Aug 3). Certification gates
# supply; the app has to carry the evidence.
_pdf = "data:application/pdf;base64," + _b64.b64encode(b"%PDF-1.4 fake " + b"0" * 300).decode()
_r = c.post("/api/users/me/certificates", json={"name": "CPR + AED", "issuer": "St. Luke's Hospital",
                                                "expires": "2027-03-31", "file_name": "cpr.pdf", "data_url": _pdf}, headers=kh)
assert _r.status_code == 200, _r.text
_certs = _r.json()
assert len(_certs) == 1 and _certs[0]["name"] == "CPR + AED" and _certs[0]["mime"] == "application/pdf", _certs
assert "data_url" not in _certs[0], "lists carry metadata only, never the file"
_cid = _certs[0]["id"]
assert c.get("/api/users/me/certificates", headers=kh).json()[0]["id"] == _cid
assert c.post("/api/users/me/certificates", json={"name": "x", "file_name": "x.exe", "data_url": "data:application/octet-stream;base64,AAAA"}, headers=kh).status_code == 400
_huge = "data:application/pdf;base64," + _b64.b64encode(b"0" * (1100 * 1024)).decode()
assert c.post("/api/users/me/certificates", json={"name": "big", "file_name": "big.pdf", "data_url": _huge}, headers=kh).status_code == 413
assert c.post("/api/users/me/certificates", json={"name": "x", "file_name": "x.pdf", "data_url": _pdf}, headers=ch).status_code == 403
# the coordinator sees it on the kaki's record and can open the file
_admin_list = c.get(f"/api/admin/users/{kk['id']}/certificates", headers=ah)
assert _admin_list.status_code == 200 and _admin_list.json()[0]["name"] == "CPR + AED", _admin_list.text
_file = c.get(f"/api/admin/users/{kk['id']}/certificates/{_cid}/file", headers=ah)
assert _file.status_code == 200 and _file.json()["data_url"] == _pdf
assert c.get(f"/api/admin/users/{kk['id']}/certificates/{_cid}/file", headers=ch).status_code == 403
# pending users carry their certificate count, so approval can see who is evidenced
kh_p, kk_p = login("newkaki@example.com", role="kaki", name="Lim Ah Seng")
assert c.post("/api/users/me/certificates", json={"name": "Mobility assistance", "issuer": "Vanguard", "file_name": "m.png",
                                                  "data_url": "data:image/png;base64," + _b64.b64encode(b"\x89PNG" + b"0" * 50).decode()}, headers=kh_p).status_code == 200
# (auto-approve for kakis was switched on by the v1.4 tests above, so this one is not pending;
#  the count is on both the pending list and the everyone list)
_everyone = next(u for u in c.get("/api/admin/users", headers=ah).json() if u["id"] == kk_p["id"])
assert _everyone["kaki"]["certificates"] == 1, _everyone
assert all("certificates" in u for u in c.get("/api/admin/pending-users", headers=ah).json())
# a kaki can remove their own, nobody else's
assert c.delete(f"/api/users/me/certificates/{_cid}", headers=kh_p).status_code == 404
assert c.delete(f"/api/users/me/certificates/{_cid}", headers=kh).status_code == 200
assert c.get("/api/users/me/certificates", headers=kh).json() == []

# ---- Bucket 2 review fixes --------------------------------------------------
# a blank or non-numeric kaki code never verifies; five wrong guesses lock the door check
_rv = _booked_and_accepted()
assert c.post(f"/api/visits/{_rv}/verify-kaki", json={"code": "   "}, headers=ch).status_code == 400
_kc = c.get(f"/api/visits/{_rv}", headers=kh).json()["kaki_code"]
_wrong = "0000" if _kc != "0000" else "1111"
for _i in range(5):
    assert c.post(f"/api/visits/{_rv}/verify-kaki", json={"code": _wrong}, headers=ch).status_code == 400
assert c.post(f"/api/visits/{_rv}/verify-kaki", json={"code": _kc}, headers=ch).status_code == 429
_rl.clear("visit_code", _rv)
assert c.post(f"/api/visits/{_rv}/verify-kaki", json={"code": _kc}, headers=ch).status_code == 200
_otp_rv = c.get(f"/api/visits/{_rv}", headers=ch).json()["otp_code"]
for _i in range(5):
    assert c.post(f"/api/visits/{_rv}/start", json={"otp": "0000" if _otp_rv != "0000" else "1111"}, headers=kh).status_code == 400
assert c.post(f"/api/visits/{_rv}/start", json={"otp": _otp_rv}, headers=kh).status_code == 429
_rl.clear("visit_code", _rv)
assert c.post(f"/api/visits/{_rv}/start", json={"otp": _otp_rv}, headers=kh).status_code == 200
assert c.post(f"/api/visits/{_rv}/complete", json={"chips": [], "text": "ok"}, headers=kh).status_code == 200
# an email body never carries raw HTML from a cancellation reason
_rx = _booked_and_accepted(); _sent.clear()
assert c.post(f"/api/visits/{_rx}/cancel", json={"reason": "<a href='x'>click</a>"}, headers=kh).status_code == 200
_body = " ".join(m[3] for m in _sent if m[0] == "email" and m[1] == "priya@example.com")
assert "&lt;a" in _body and "<a href" not in _body, _body
# a suspended kaki cannot upload; a kaki has at most 10 certificates
_ph_sus = c.post(f"/api/admin/users/{kk_p['id']}/suspend", headers=ah); assert _ph_sus.status_code == 200
assert c.put("/api/users/me/photo", json={"data_url": _png}, headers=kh_p).status_code == 403
assert c.post("/api/users/me/certificates", json={"name": "x", "file_name": "x.pdf", "data_url": _pdf}, headers=kh_p).status_code == 403
for _i in range(10):
    assert c.post("/api/users/me/certificates", json={"name": f"c{_i}", "file_name": "c.pdf", "data_url": _pdf}, headers=kh).status_code == 200
assert c.post("/api/users/me/certificates", json={"name": "one too many", "file_name": "c.pdf", "data_url": _pdf}, headers=kh).status_code == 400
# an "extra slot" exception must contain the visit, not merely touch it
assert c.put("/api/users/me/availability", json={"weekly": {"Mon": {"from": "09:00", "to": "12:00"}}}, headers=kh).status_code == 200
assert c.post("/api/users/me/availability/exceptions", json={"date": "2026-08-18", "half_day": "morning", "available": True}, headers=kh).status_code == 200
assert availmod.check(kk["id"], "2026-08-18", "09:00–11:00")["state"] == "available"
assert availmod.check(kk["id"], "2026-08-18", "12:30–14:30")["state"] == "unavailable"
db.run("UPDATE kaki_profiles SET weekly_slots = ? WHERE user_id = ?", ['{"Tue": {"from": "09:00", "to": "12:00"}, "Sat": {"from": "08:00", "to": "18:00"}}', kk["id"]])
# cross-ownership: a caregiver cannot cancel or verify someone else's visit
ch2, cg2 = login("hong@example.com", role="caregiver", name="Hong Hang")
assert c.post(f"/api/admin/users/{cg2['id']}/approve", json={"role": "caregiver"}, headers=ah).status_code == 200
ch2, cg2 = login("hong@example.com")
_ry = _booked_and_accepted()
assert c.post(f"/api/visits/{_ry}/cancel", json={"reason": "not mine"}, headers=ch2).status_code == 403
assert c.post(f"/api/visits/{_ry}/verify-kaki", json={"code": "1234"}, headers=ch2).status_code == 403
assert c.post(f"/api/visits/{_ry}/cancel", json={"reason": "done"}, headers=ch).status_code == 200

# ---- v1.7: language ----------------------------------------------------------
# users.lang round-trips; only en and zh are accepted; /auth/me carries it so a
# second phone follows the person, not the browser.
assert c.get("/api/users/me/profile", headers=kh).json().get("lang", "") in ("", "en")
assert c.put("/api/users/me", json={"lang": "zh"}, headers=kh).status_code == 200
assert c.get("/api/users/me/profile", headers=kh).json()["lang"] == "zh"
assert c.get("/api/auth/me", headers=kh).json()["user"]["lang"] == "zh"
assert c.put("/api/users/me", json={"lang": "fr"}, headers=kh).status_code == 400
assert c.put("/api/users/me", json={"lang": "en"}, headers=kh).status_code == 200
assert c.get("/api/users/me/profile", headers=kh).json()["lang"] == "en"
# senior-facing errors carry a stable code next to the English detail; the
# frontend maps the code, the coordinator and the logs still read the sentence
_req = request_code("beelian@example.com")
_bad = c.post("/api/auth/verify", json={"identifier": "beelian@example.com", "code": "000000"})
assert _bad.status_code == 400 and _bad.json()["error"] == "code_wrong" and "Wrong code" in _bad.json()["detail"], _bad.text
_rl.clear("verify_failure", "beelian@example.com")
kh, kk = login("beelian@example.com")
_rz = _booked_and_accepted()
_bad = c.post(f"/api/visits/{_rz}/start", json={"otp": "abcd"}, headers=kh)   # never a real code
assert _bad.status_code == 400 and _bad.json()["error"] == "start_code_wrong", _bad.text
_rl.clear("visit_code", _rz)
_bad = c.post(f"/api/visits/{_rz}/verify-kaki", json={"code": "0000" if c.get(f"/api/visits/{_rz}", headers=kh).json()["kaki_code"] != "0000" else "1111"}, headers=ch)
assert _bad.status_code == 400 and _bad.json()["error"] == "kaki_code_wrong", _bad.text
_rl.clear("visit_code", _rz)
assert c.post(f"/api/visits/{_rz}/cancel", json={"reason": "done"}, headers=ch).status_code == 200
# notifications follow the recipient's language: a zh kaki gets Chinese, the
# en caregiver on the same visit gets English, and the audit log stays English
assert c.put("/api/users/me", json={"lang": "zh"}, headers=kh).status_code == 200
_vz = c.post("/api/visits", json={"service": "Companionship", "tier": "planned", "date": "2026-08-18",
                                  "start_time": "09:00", "end_time": "11:00", "languages": ["Mandarin"]}, headers=ch).json()
_sent.clear()
assert c.post(f"/api/admin/visits/{_vz['id']}/assign", json={"kaki_id": kk["id"]}, headers=ah).status_code == 200
_kz = " ".join(_texts_to("beelian@example.com")); _cz = " ".join(_texts_to("priya@example.com"))
assert "探访" in _kz and "2026-08-18" in _kz and "Companionship" in _kz and "2 小时" in _kz, _kz
assert "Open the app" not in _kz and "personal-care" not in _kz, _kz
_vv = c.get(f"/api/visits/{_vz['id']}", headers=kh).json()
assert _vv["kaki_code"] and _vv["kaki_code"] not in _cz and "otp_code" not in _vv, _vv   # §9.5 holds in messages too
assert "matched" in _cz.lower() and not any("一" <= ch_ <= "鿿" for ch_ in _cz), _cz
_aud = db.q("SELECT detail FROM audit_log WHERE action = 'notified' ORDER BY ts DESC LIMIT 2")
assert _aud and all(not any("一" <= ch_ <= "鿿" for ch_ in (r["detail"] or "")) for r in _aud), _aud
_sent.clear()
assert c.post(f"/api/visits/{_vz['id']}/accept", headers=kh).status_code == 200
assert any("confirmed" in t.lower() for t in _texts_to("priya@example.com")), _sent
_sent.clear()
assert c.post(f"/api/visits/{_vz['id']}/cancel", json={"reason": "plans changed"}, headers=ch).status_code == 200
_kz = " ".join(_texts_to("beelian@example.com"))
assert "取消" in _kz and "plans changed" in _kz, _kz          # reason is the caregiver's words, untranslated
assert c.put("/api/users/me", json={"lang": "en"}, headers=kh).status_code == 200
# the help bot answers in the language of the question
_zq = c.post("/api/chat", json={"message": "什么是开始码？"}, headers=ch).json()["reply"]
assert "开始码" in _zq and "start code" not in _zq.lower(), _zq
_zq = c.post("/api/chat", json={"message": "怎样登录？"}).json()["reply"]          # signed out: the guide
assert "验证码" in _zq, _zq
_eq = c.post("/api/chat", json={"message": "what is the start code?"}, headers=ch).json()["reply"]
assert not any("一" <= ch_ <= "鿿" for ch_ in _eq), _eq

# Count the assertions from the source rather than hardcoding a number. Four
# separate docs had four different figures because the banner was a string
# somebody had to remember to bump. This one cannot go stale.
_n = sum(1 for _line in open(os.path.abspath(__file__), encoding="utf-8")
         if _line.lstrip().startswith("assert "))
print(f"ALL SMOKE TESTS PASSED ✓  (v1.7 — {_n} assertions)")
