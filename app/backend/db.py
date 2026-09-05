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
      identifier TEXT, channel TEXT, code TEXT, expires TIMESTAMP);
    CREATE TABLE IF NOT EXISTS audit_log(
      ts TIMESTAMP DEFAULT current_timestamp, actor TEXT, action TEXT, detail TEXT);
    """)
    # v1.1 migrations (safe on fresh and existing DBs)
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS crisis_trigger TEXT DEFAULT ''")

    # v1.2 migrations — sign in by email OR mobile.
    # Which channels a person has actually proved they control. Email-era rows
    # are backfilled as email-verified since that was the only way in.
    c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE")
    c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE")
    c.execute("UPDATE users SET email_verified = TRUE WHERE email IS NOT NULL AND email <> '' AND email_verified IS NOT TRUE")
    # otp_codes was keyed on `email`; it is now keyed on the generic identifier.
    # The rows are throwaway (codes expire in minutes), so reshaping by drop and
    # recreate is safe and avoids a fragile column rename.
    otp_cols = {r[0] for r in c.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'otp_codes'").fetchall()}
    if "email" in otp_cols:
        c.execute("DROP TABLE otp_codes")
        c.execute("CREATE TABLE otp_codes(identifier TEXT, channel TEXT, code TEXT, expires TIMESTAMP)")
    # An empty-string email would collide under the UNIQUE constraint the moment
    # a second phone-only account appeared; NULL is the only safe "no email".
    c.execute("UPDATE users SET email = NULL WHERE email = ''")

    # v1.3 · kaki availability, for matching.
    # Two layers: a recurring normal week, plus dated exceptions. Most kakis are
    # employed elsewhere, so "Tuesdays and Thursday afternoons, except I'm away
    # next week" is the shape that actually matches reality.
    #   weekly_slots — JSON {"Mon": ["morning"], "Sat": ["morning","afternoon"], ...}
    c.execute("ALTER TABLE kaki_profiles ADD COLUMN IF NOT EXISTS weekly_slots TEXT DEFAULT '{}'")
    c.execute("ALTER TABLE kaki_profiles ADD COLUMN IF NOT EXISTS availability_note TEXT DEFAULT ''")
    # v1.5 · rate limiting for the sign-in endpoints. DB-backed rather than
    # in-memory so the counters survive a restart — an in-process limiter is
    # reset by every deploy, which makes it security theatre.
    c.execute("""
    CREATE TABLE IF NOT EXISTS auth_attempts(
      kind TEXT, key TEXT, ts TIMESTAMP DEFAULT current_timestamp);
    """)

    # v1.4 · coordinator-editable settings (auto-approval, auto-matching, PayNow).
    # Key/value so a new switch needs no migration. Values are JSON-encoded.
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings(
      key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP DEFAULT current_timestamp);
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS availability_exceptions(
      id TEXT PRIMARY KEY, user_id TEXT, date TEXT,
      half_day TEXT,          -- 'morning' | 'afternoon' | 'all'
      available BOOLEAN,      -- FALSE = day off, TRUE = extra slot outside the weekly pattern
      note TEXT DEFAULT '');
    """)
    # v1.6 · after the August feedback round.
    # M-VISITS: the kaki taps "I'm on my way"; the caregiver sees when.
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS on_way_at TIMESTAMP")
    # M-VISITS: a visit may need more than one language; `language` stays as
    # the first of them for older screens and the matcher's display.
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS languages TEXT DEFAULT '[]'")
    # M-CARE: emergency contact as three fields, not one free-text line (NCSS 2.6).
    # The old `contacts` text stays for anything already typed there.
    c.execute("ALTER TABLE care_plans ADD COLUMN IF NOT EXISTS contact_name TEXT DEFAULT ''")
    c.execute("ALTER TABLE care_plans ADD COLUMN IF NOT EXISTS contact_relationship TEXT DEFAULT ''")
    c.execute("ALTER TABLE care_plans ADD COLUMN IF NOT EXISTS contact_phone TEXT DEFAULT ''")
    # M-VISITS: exact times in 30-minute steps; hours prorated to the half hour.
    # time_window keeps a "HH:MM–HH:MM" copy so older screens and the matcher read it.
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS start_time TEXT DEFAULT ''")
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS end_time TEXT DEFAULT ''")
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS hours DOUBLE")
    # M-USERS / M-VISITS: identity both ways. The kaki carries a photo and, per
    # visit, a 4-digit code the caregiver enters; only then is the caregiver's
    # own start code revealed. Photo is a data URL, capped in the endpoint.
    c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS photo TEXT DEFAULT ''")
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS kaki_code TEXT DEFAULT ''")
    c.execute("ALTER TABLE visits ADD COLUMN IF NOT EXISTS kaki_verified_at TIMESTAMP")

    # Fold the write-ahead log into the database file before serving traffic.
    # DuckDB can throw an InternalException replaying a WAL entry for
    # ADD COLUMN ... DEFAULT after an unclean shutdown (e.g. systemctl restart
    # mid-write), which makes the process crash-loop on boot. Checkpointing
    # here means there is never such an entry left to replay.
    try:
        c.execute("CHECKPOINT")
    except Exception:
        pass

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
