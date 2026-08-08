"""M-CORE · loads assumptions.json — the single source for every money/time number.

Nothing in the pricing or impact code may hardcode a rate, an hour estimate or a
subsidy percentage. They all come from app/assumptions.json so a coordinator can
change a figure and restart, with no code deploy and no developer.

The file is read once at import and cached; ASSUMPTIONS_PATH can point elsewhere
for tests.
"""
import json, os, pathlib

_DEFAULT = pathlib.Path(__file__).resolve().parent.parent / "assumptions.json"
PATH = pathlib.Path(os.environ.get("ASSUMPTIONS_PATH", _DEFAULT))

_cache = None

# Used only if assumptions.json is missing or unreadable — the app must still
# boot rather than 500 on every visit screen.
_FALLBACK = {
    "version": "fallback",
    "currency": "SGD",
    "services": {},
    "subsidies": {"community_care_fund_pct": {"value": 0.0},
                  "foundation_topup_pct": {"value": 0.0}},
    "kaki_payment": {"transport_allowance_per_visit": {"value": 0.0}},
    "time": {"default_hours_when_service_unknown": {"value": 2}},
    "disclaimer": {"short": "For illustration only",
                   "long": "Figures are pilot estimates for illustration only."},
}

def load(force: bool = False) -> dict:
    global _cache
    if _cache is None or force:
        try:
            _cache = json.loads(PATH.read_text())
        except Exception as e:
            print(f"[kakis] could not read {PATH}: {e} — using zeroed fallback")
            _cache = dict(_FALLBACK)
    return _cache

def _v(node, default=None):
    """Values are stored as {"value": x, "source": ...}; accept bare values too."""
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    return default if node is None else node

def service(name: str) -> dict | None:
    return load().get("services", {}).get(name)

def services() -> dict:
    return load().get("services", {})

def subsidy_pct(key: str) -> float:
    return float(_v(load().get("subsidies", {}).get(key), 0.0) or 0.0)

def transport_allowance() -> float:
    return float(_v(load().get("kaki_payment", {}).get("transport_allowance_per_visit"), 0.0) or 0.0)

def default_hours() -> int:
    return int(_v(load().get("time", {}).get("default_hours_when_service_unknown"), 2) or 2)

def half_day_windows() -> dict:
    w = load().get("time", {}).get("half_day_windows", {})
    return {"morning": w.get("morning", "08:00–13:00"), "afternoon": w.get("afternoon", "13:00–18:00")}

def disclaimer() -> dict:
    return load().get("disclaimer", _FALLBACK["disclaimer"])

def public() -> dict:
    """The whole file, for the admin assumptions screen."""
    return load()

def save(data: dict) -> dict:
    """Write the file back and refresh the cache. Used by the admin rate editor
    so assumptions.json stays the single source of truth rather than the DB
    holding a second, silently diverging copy of the same numbers.

    Written via a temp file and atomic replace: a crash mid-write would
    otherwise leave the app with no readable pricing at all."""
    tmp = PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, PATH)
    global _cache
    _cache = data
    return _cache
