import os, sys
os.environ["DB_PATH"] = "/tmp/kakis-test.duckdb"
os.environ["DEV_MODE"] = "1"
os.environ["ADMIN_EMAILS"] = "admin@kakis.sg"
if os.path.exists("/tmp/kakis-test.duckdb"): os.remove("/tmp/kakis-test.duckdb")
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from backend.main import app
from backend import config
c = TestClient(app)

def request_code(identifier):
    r = c.post("/api/auth/request-code", json={"identifier": identifier})
    assert r.status_code == 200, r.text
    return r.json()

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
assert visit["status"] == "requested" and visit["otp_code"]
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

# caregiver DOES see the otp
cv = c.get(f"/api/visits/{vid}", headers=ch).json()
otp = cv["otp_code"]; assert otp and cv["status"] == "accepted" and cv["kaki"]["name"] == "Tan Bee Lian"

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

print("ALL SMOKE TESTS PASSED ✓  (v1.2 — 52 assertions)")
