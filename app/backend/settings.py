"""M-CORE · coordinator-editable settings, stored in the DB.

Distinct from config.py (deployment env vars, needs a restart) and
assumptions.json (money and time figures). This is the small set of switches a
coordinator flips from the admin panel while the app is running.

Every automation default is OFF. Auto-approval and auto-matching remove a human
from decisions about who enters a vulnerable person's home, so they are opt-in
choices someone makes deliberately, never a default anyone inherits.
"""
import json
from . import db

DEFAULTS = {
    "auto_approve_kaki":      False,
    "auto_approve_caregiver": False,
    "auto_match":             False,
    "paynow_type":            "uen",     # uen | mobile
    "paynow_value":           "",
    "paynow_name":            "",
}

BOOL_KEYS = {"auto_approve_kaki", "auto_approve_caregiver", "auto_match"}

def all() -> dict:
    out = dict(DEFAULTS)
    for row in db.q("SELECT key, value FROM settings"):
        if row["key"] not in DEFAULTS:
            continue
        try:
            out[row["key"]] = json.loads(row["value"])
        except Exception:
            pass
    return out

def get(key: str):
    return all().get(key, DEFAULTS.get(key))

def set_many(values: dict, actor: str = "") -> dict:
    changed = {}
    for key, raw in (values or {}).items():
        if key not in DEFAULTS:
            continue                      # ignore unknown keys rather than store junk
        value = bool(raw) if key in BOOL_KEYS else ("" if raw is None else str(raw)).strip()
        db.run("DELETE FROM settings WHERE key = ?", [key])
        db.run("INSERT INTO settings(key, value) VALUES (?,?)", [key, json.dumps(value)])
        changed[key] = value
    if changed and actor:
        db.audit(actor, "settings_changed", json.dumps(changed))
    return all()

def paynow() -> dict:
    s = all()
    return {"type": s["paynow_type"], "value": s["paynow_value"],
            "name": s["paynow_name"], "configured": bool(s["paynow_value"])}
