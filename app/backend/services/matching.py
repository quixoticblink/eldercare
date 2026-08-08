"""M-ADMIN · scoring, assignment and optional auto-matching.

One assignment path, used by both the coordinator's manual pick and the
automatic matcher, so the two can never drift apart in what they check or who
they notify.

Auto-matching is conservative on purpose. It assigns only kakis whose stated
availability actually covers the visit — never "unknown", never "unavailable".
A visit it cannot fill is left as `requested` for a human, which is the right
failure: a coordinator noticing an unmatched urgent request is recoverable,
someone arriving who never agreed to be there is not.
"""
from .. import db
from . import availability, notify

def _profile(uid: str) -> dict:
    return db.one("SELECT * FROM kaki_profiles WHERE user_id = ?", [uid]) or {}

def score(kaki: dict, visit: dict) -> dict:
    """Rank one kaki against one visit. Higher total is a better match."""
    uid = kaki["id"]
    p = _profile(uid)
    services = db.uj(p.get("services"))
    languages = db.uj(p.get("languages"))

    fit = availability.check(uid, visit.get("date"), visit.get("time_window"))
    history = db.q("""SELECT count(*) c FROM visits
                      WHERE kaki_id = ? AND household_id = ? AND status = 'completed'""",
                   [uid, visit["household_id"]])[0]["c"]
    active = db.q("""SELECT count(*) c FROM visits WHERE kaki_id = ?
                     AND status IN ('assigned','accepted','in_progress')""", [uid])[0]["c"]

    total = 0
    total += {"available": 100, "unknown": 0, "unavailable": -1000}[fit["state"]]
    total += min(history, 5) * 20          # continuity matters most after availability
    total += 15 if visit.get("language") in languages else 0
    total += 10 if visit.get("service") in services else 0
    total -= active * 5                    # spread the load
    return {"total": total, "fit": fit, "history": history, "active": active,
            "language_ok": visit.get("language") in languages,
            "service_ok": visit.get("service") in services}

def rank(visit: dict) -> list[dict]:
    kakis = db.q("""SELECT id, name, email, phone FROM users
                    WHERE role = 'kaki' AND status = 'approved'""")
    for k in kakis:
        k["score"] = score(k, visit)
    kakis.sort(key=lambda k: (-k["score"]["total"], (k["name"] or "").lower()))
    return kakis

def best_available(visit: dict) -> dict | None:
    """Top-scoring kaki whose availability positively covers the visit, else None."""
    for k in rank(visit):
        if k["score"]["fit"]["state"] == "available":
            return k
    return None

def assign(vid: str, kaki_id: str, actor: str, automatic: bool = False) -> dict:
    """The single assignment path. Returns a summary including who was notified."""
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise ValueError("Visit not found")
    if v["status"] not in ("requested", "assigned"):
        raise ValueError(f"Visit is {v['status']}")
    kaki = db.one("SELECT * FROM users WHERE id = ? AND role = 'kaki' AND status = 'approved'",
                  [kaki_id])
    if not kaki:
        raise ValueError("Not an approved kaki")

    db.run("""UPDATE visits SET kaki_id = ?, status = 'assigned', assigned_at = current_timestamp
              WHERE id = ?""", [kaki_id, vid])
    db.audit(actor, "visit_auto_assigned" if automatic else "visit_assigned",
             f"{vid} -> {kaki['email'] or kaki['phone']}")

    caregiver = db.one("SELECT * FROM users WHERE id = ?", [v["caregiver_id"]])
    household = db.one("SELECT * FROM households WHERE id = ?", [v["household_id"]]) or {}
    delivery = notify.visit_assigned(v, kaki, caregiver, household.get("senior_name", ""))

    return {"ok": True, "automatic": automatic,
            "assigned_to": {"id": kaki["id"], "name": kaki["name"],
                            "contact": kaki["email"] or kaki["phone"]},
            "fit": availability.check(kaki["id"], v.get("date"), v.get("time_window")),
            "notified": delivery}

def try_auto_assign(vid: str, actor: str = "auto-match") -> dict | None:
    """Assign the best available kaki, or return None and leave it for a human."""
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v or v["status"] != "requested":
        return None
    pick = best_available(v)
    if not pick:
        db.audit(actor, "auto_match_no_candidate", vid)
        return None
    return assign(vid, pick["id"], actor, automatic=True)

def sweep(actor: str = "auto-match") -> dict:
    """Fill every outstanding request that has an available kaki. Urgent first."""
    order = {"urgent": 0, "soon": 1, "planned": 2}
    pending = db.q("SELECT * FROM visits WHERE status = 'requested'")
    pending.sort(key=lambda v: order.get(v.get("tier"), 3))
    matched, unmatched = [], []
    for v in pending:
        result = try_auto_assign(v["id"], actor)
        (matched if result else unmatched).append({
            "visit_id": v["id"], "service": v.get("service"), "tier": v.get("tier"),
            "kaki": result["assigned_to"]["name"] if result else None})
    return {"matched": matched, "unmatched": unmatched,
            "counts": {"matched": len(matched), "unmatched": len(unmatched)}}
