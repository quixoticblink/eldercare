"""M-USERS · profiles and kaki preferences."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .. import db, security

router = APIRouter(prefix="/users", tags=["users"])

class ProfileIn(BaseModel):
    name: str | None = None
    phone: str | None = None
    services: list[str] | None = None
    languages: list[str] | None = None
    area: str | None = None

@router.put("/me")
def update_me(body: ProfileIn, user=Depends(security.current_user)):
    if body.name is not None:
        db.run("UPDATE users SET name = ? WHERE id = ?", [body.name, user["id"]])
    if body.phone is not None:
        db.run("UPDATE users SET phone = ? WHERE id = ?", [body.phone, user["id"]])
    if user["role"] == "kaki":
        if not db.one("SELECT 1 FROM kaki_profiles WHERE user_id = ?", [user["id"]]):
            db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [user["id"]])
        if body.services is not None:
            db.run("UPDATE kaki_profiles SET services = ? WHERE user_id = ?", [db.j(body.services), user["id"]])
        if body.languages is not None:
            db.run("UPDATE kaki_profiles SET languages = ? WHERE user_id = ?", [db.j(body.languages), user["id"]])
        if body.area is not None:
            db.run("UPDATE kaki_profiles SET area = ? WHERE user_id = ?", [body.area, user["id"]])
    return get_me_profile(user)

@router.get("/me/profile")
def get_me_profile(user=Depends(security.current_user)):
    out = {k: user.get(k) for k in ("id", "email", "name", "phone", "role", "status")}
    if user["role"] == "kaki":
        p = db.one("SELECT * FROM kaki_profiles WHERE user_id = ?", [user["id"]]) or {}
        out["kaki"] = {"services": db.uj(p.get("services")), "languages": db.uj(p.get("languages")),
                       "area": p.get("area", "Pasir Ris"), "tier": p.get("tier", 1)}
    return out
