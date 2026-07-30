"""M-CORE · DuckDB connection, schema, tiny query helpers.

DuckDB is embedded and the Python connection is not thread-safe;
FastAPI sync endpoints run in a threadpool, so all access goes through
q()/one()/run() under a single lock. Fine at pilot scale.
"""
import duckdb, json, threading, uuid, datetime
from . import config

_lock = threading.Lock()
_con = None

def connect():
    global _con
    if _con is None:
        _con = duckdb.connect(config.DB_PATH)
        _init(_con)
    return _con

def _init(c):
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
      id TEXT PRIMARY KEY, email TEXT UNIQUE, name TEXT DEFAULT '', phone TEXT DEFAULT '',
      role TEXT DEFAULT '', status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT current_timestamp);
    CREATE TABLE IF NOT EXISTS kaki_profiles(
      user_id TEXT PRIMARY KEY, services TEXT DEFAULT '[]', languages TEXT DEFAULT '[]',
      area TEXT DEFAULT 'Pasir Ris', tier INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS households(
      id TEXT PRIMARY KEY, caregiver_id TEXT, senior_name TEXT, senior_age INTEGER,
      address TEXT DEFAULT '', created_at TIMESTAMP DEFAULT current_timestamp);
    CREATE TABLE IF NOT EXISTS care_plans(
      household_id TEXT PRIMARY KEY, meds TEXT DEFAULT '', mobility TEXT DEFAULT '',
      languages TEXT DEFAULT '[]', contacts TEXT DEFAULT '', notes TEXT DEFAULT '');
    CREATE TABLE IF NOT EXISTS visits(
      id TEXT PRIMARY KEY, household_id TEXT, caregiver_id TEXT, kaki_id TEXT,
      service TEXT, tier TEXT, date TEXT, time_window TEXT, language TEXT, notes TEXT DEFAULT '',
      status TEXT DEFAULT 'requested', otp_code TEXT,
      created_at TIMESTAMP DEFAULT current_timestamp,
      assigned_at TIMESTAMP, accepted_at TIMESTAMP, started_at TIMESTAMP, completed_at TIMESTAMP);
    CREATE TABLE IF NOT EXISTS visit_reports(
      visit_id TEXT PRIMARY KEY, chips TEXT DEFAULT '[]', text TEXT DEFAULT '',
      meds_confirmed BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT current_timestamp);
    CREATE TABLE IF NOT EXISTS care_notes(
      id TEXT PRIMARY KEY, household_id TEXT, visit_id TEXT, author_id TEXT,
      chips TEXT DEFAULT '[]', text TEXT DEFAULT '', created_at TIMESTAMP DEFAULT current_timestamp);
    CREATE TABLE IF NOT EXISTS otp_codes(
      email TEXT, code TEXT, expires TIMESTAMP);
    CREATE TABLE IF NOT EXISTS audit_log(
      ts TIMESTAMP DEFAULT current_timestamp, actor TEXT, action TEXT, detail TEXT);
    """)
    # v1.1 migrations (safe on fresh and existing DBs)
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS crisis_trigger TEXT DEFAULT ''")

def q(sql, params=None):
    """SELECT → list of dicts."""
    with _lock:
        cur = connect().execute(sql, params or [])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

def one(sql, params=None):
    rows = q(sql, params)
    return rows[0] if rows else None

def run(sql, params=None):
    with _lock:
        connect().execute(sql, params or [])

def new_id() -> str:
    return uuid.uuid4().hex[:12]

def now():
    return datetime.datetime.now()

def audit(actor: str, action: str, detail: str = ""):
    run("INSERT INTO audit_log(actor, action, detail) VALUES (?,?,?)", [actor, action, detail])

def j(x):
    return json.dumps(x or [])

def uj(s):
    try:
        return json.loads(s) if s else []
    except Exception:
        return []
