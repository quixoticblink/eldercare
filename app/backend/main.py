"""M-CORE · app factory. Wiring only — no business logic."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from . import config, db
from .routers import auth, users, care, visits, admin, chat

app = FastAPI(title="Kakis", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth.router, users.router, care.router, visits.router, admin.router, chat.router):
    app.include_router(r, prefix="/api")

@app.get("/api/health")
def health():
    return {"ok": True, "dev_mode": config.DEV_MODE}

db.connect()  # init schema on boot

# Serve the frontend from the same VM (single-box deployment).
# For the Vercel split, deploy frontend/ separately and set API_BASE there.
_frontend = Path(__file__).resolve().parent.parent / "frontend"
if _frontend.exists():
    app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="frontend")
