"""M-CARE · household + care plan (one household per caregiver in v1)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .. import db, security

router = APIRouter(prefix="/care", tags=["care"])

class HouseholdIn(BaseModel):
    senior_name: str
    senior_age: int | None = None
    address: str | None = ""

class PlanIn(BaseModel):
    meds: str | None = ""
    mobility: str | None = ""          # Independent | Walks with a stick | Walking frame | Wheelchair | Bedridden
    languages: list[str] | None = None
    contacts: str | None = ""          # legacy free text
    contact_name: str | None = ""
    contact_relationship: str | None = ""
    contact_phone: str | None = ""     # normalised to E.164; used for start/finish messages
    notes: str | None = ""

def _caregiver(user):
    security.approved_user(user)
    security.require_role(user, "caregiver", "admin")
    return user

def get_household(caregiver_id: str):
    return db.one("SELECT * FROM households WHERE caregiver_id = ?", [caregiver_id])

@router.get("/household")
def household(user=Depends(security.current_user)):
    _caregiver(user)
    h = get_household(user["id"])
    if not h:
        return {"household": None, "plan": None}
    plan = db.one("SELECT * FROM care_plans WHERE household_id = ?", [h["id"]])
    if plan:
        plan["languages"] = db.uj(plan.get("languages"))
    return {"household": h, "plan": plan}

@router.put("/household")
def upsert_household(body: HouseholdIn, user=Depends(security.current_user)):
    _caregiver(user)
    h = get_household(user["id"])
    if h:
        db.run("UPDATE households SET senior_name=?, senior_age=?, address=? WHERE id=?",
               [body.senior_name, body.senior_age, body.address or "", h["id"]])
    else:
        hid = db.new_id()
        db.run("INSERT INTO households(id, caregiver_id, senior_name, senior_age, address) VALUES (?,?,?,?,?)",
               [hid, user["id"], body.senior_name, body.senior_age, body.address or ""])
        db.run("INSERT INTO care_plans(household_id) VALUES (?)", [hid])
    return household(user)

@router.put("/plan")
def upsert_plan(body: PlanIn, user=Depends(security.current_user)):
    _caregiver(user)
    h = get_household(user["id"])
    if not h:
        raise HTTPException(400, "Set up your household first")
    phone = (body.contact_phone or "").strip()
    if phone:
        try:
            phone = security.normalise_phone(phone)
        except ValueError as e:
            raise HTTPException(400, f"Emergency contact number: {e}")
    db.run("""UPDATE care_plans SET meds=?, mobility=?, languages=?, contacts=?, notes=?,
              contact_name=?, contact_relationship=?, contact_phone=?
              WHERE household_id=?""",
           [body.meds or "", body.mobility or "", db.j(body.languages), body.contacts or "",
            body.notes or "", (body.contact_name or "").strip(), (body.contact_relationship or "").strip(),
            phone, h["id"]])
    db.audit(user["email"], "care_plan_update", h["id"])
    return household(user)
