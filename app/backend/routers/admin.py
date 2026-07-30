"""M-ADMIN · approvals, manual matching, quality. Automated matching lands here later."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .. import db, security

router = APIRouter(prefix="/admin", tags=["admin"])

class AssignIn(BaseModel):
    kaki_id: str

class ApproveIn(BaseModel):
    role: str | None = None   # optionally set/override role on approval

def _admin(user):
    security.approved_user(user)
    security.require_role(user, "admin")
    return user

@router.get("/overview")
def overview(user=Depends(security.current_user)):
    _admin(user)
    def count(sql, params=None):
        return db.q(sql, params)[0]["c"]
    return {
        "pending_users":  count("SELECT count(*) c FROM users  WHERE status = 'pending'"),
        "open_requests":  count("SELECT count(*) c FROM visits WHERE status = 'requested'"),
        "active_visits":  count("SELECT count(*) c FROM visits WHERE status IN ('assigned','accepted','in_progress')"),
        "completed":      count("SELECT count(*) c FROM visits WHERE status = 'completed'"),
        "care_notes":     count("SELECT count(*) c FROM care_notes"),
    }

@router.get("/pending-users")
def pending_users(user=Depends(security.current_user)):
    _admin(user)
    return db.q("SELECT id, email, name, phone, role, status, created_at FROM users WHERE status = 'pending' ORDER BY created_at")

@router.get("/users")
def all_users(user=Depends(security.current_user)):
    _admin(user)
    rows = db.q("SELECT id, email, name, phone, role, status, created_at FROM users ORDER BY created_at")
    for r in rows:
        if r["role"] == "kaki":
            p = db.one("SELECT * FROM kaki_profiles WHERE user_id = ?", [r["id"]]) or {}
            r["kaki"] = {"services": db.uj(p.get("services")), "languages": db.uj(p.get("languages")),
                         "area": p.get("area"), "tier": p.get("tier", 1)}
    return rows

@router.post("/users/{uid}/approve")
def approve(uid: str, body: ApproveIn, user=Depends(security.current_user)):
    _admin(user)
    target = db.one("SELECT * FROM users WHERE id = ?", [uid])
    if not target:
        raise HTTPException(404, "User not found")
    role = body.role or target["role"] or "caregiver"
    db.run("UPDATE users SET status = 'approved', role = ? WHERE id = ?", [role, uid])
    if role == "kaki" and not db.one("SELECT 1 FROM kaki_profiles WHERE user_id = ?", [uid]):
        db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [uid])
    db.audit(user["email"], "user_approved", f"{target['email']} as {role}")
    return {"ok": True}

@router.post("/users/{uid}/suspend")
def suspend(uid: str, user=Depends(security.current_user)):
    _admin(user)
    if uid == user["id"]:
        raise HTTPException(400, "You can't suspend yourself")
    db.run("UPDATE users SET status = 'suspended' WHERE id = ?", [uid])
    db.audit(user["email"], "user_suspended", uid)
    return {"ok": True}

@router.get("/kakis")
def kakis(user=Depends(security.current_user)):
    """Approved kakis, for the manual-matching picker."""
    _admin(user)
    rows = db.q("""SELECT u.id, u.name, u.email, u.phone FROM users u
                   WHERE u.role = 'kaki' AND u.status = 'approved' ORDER BY u.name""")
    for r in rows:
        p = db.one("SELECT * FROM kaki_profiles WHERE user_id = ?", [r["id"]]) or {}
        r["services"] = db.uj(p.get("services"))
        r["languages"] = db.uj(p.get("languages"))
        r["active"] = db.q("SELECT count(*) c FROM visits WHERE kaki_id = ? AND status IN ('assigned','accepted','in_progress')", [r["id"]])[0]["c"]
        r["done_with"] = {}  # visits completed per household — consistency signal
        for row in db.q("""SELECT household_id, count(*) c FROM visits
                           WHERE kaki_id = ? AND status = 'completed' GROUP BY household_id""", [r["id"]]):
            r["done_with"][row["household_id"]] = row["c"]
    return rows

@router.post("/visits/{vid}/assign")
def assign(vid: str, body: AssignIn, user=Depends(security.current_user)):
    """Manual matching, v1. Automated scoring will replace ONLY this endpoint's logic."""
    _admin(user)
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if v["status"] not in ("requested", "assigned"):
        raise HTTPException(400, f"Visit is {v['status']}")
    kaki = db.one("SELECT * FROM users WHERE id = ? AND role = 'kaki' AND status = 'approved'", [body.kaki_id])
    if not kaki:
        raise HTTPException(400, "Not an approved kaki")
    db.run("UPDATE visits SET kaki_id = ?, status = 'assigned', assigned_at = current_timestamp WHERE id = ?",
           [body.kaki_id, vid])
    db.audit(user["email"], "visit_assigned", f"{vid} -> {kaki['email']}")
    return {"ok": True}

@router.get("/quality")
def quality(user=Depends(security.current_user)):
    _admin(user)
    reports = db.q("""SELECT r.*, v.service, v.date, v.caregiver_id, v.kaki_id, v.household_id
                      FROM visit_reports r JOIN visits v ON v.id = r.visit_id
                      ORDER BY r.created_at DESC LIMIT 50""")
    notes = db.q("SELECT * FROM care_notes ORDER BY created_at DESC LIMIT 50")
    for x in reports:
        x["chips"] = db.uj(x.get("chips"))
    for n in notes:
        n["chips"] = db.uj(n.get("chips"))
    return {"reports": reports, "notes": notes}
