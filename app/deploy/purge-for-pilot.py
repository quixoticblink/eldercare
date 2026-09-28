"""Wipe every person and every interaction from a Kakis DuckDB, keeping only the
named admins and the coordinator settings. Used once, before the pilot went live.

    sudo systemctl stop kakis
    sudo -u kakis cp /home/kakis/kakis.duckdb     /home/kakis/kakis.duckdb.bak-prepilot-<ts>
    sudo -u kakis cp /home/kakis/kakis.duckdb.wal /home/kakis/kakis.duckdb.wal.bak-prepilot-<ts>   # if present
    sudo -u kakis /home/kakis/eldercare/app/.venv/bin/python deploy/purge-for-pilot.py \
        /home/kakis/kakis.duckdb "abhishekkaul@gmail.com|+6598553704|Abhishek" "pureum.yim@grabtaxi.com|+6585234343|Lara"
    sudo systemctl start kakis

Each admin argument is email|phone|name. An existing row with that email is kept
and updated (role admin, approved, phone set, both channels verified); a missing
one is created. Everything else goes: users, kaki profiles, households, care
plans, visits, reports, notes, certificates, availability exceptions, sign-in
codes, rate-limit counters and the audit log. `settings` (auto-approve flags,
booking window) is kept. Also put the same emails/phones in ADMIN_EMAILS /
ADMIN_PHONES in .env so the admin flag survives a re-sign-in.
"""
import sys, uuid, datetime, duckdb

db = sys.argv[1]
admins = []
for a in sys.argv[2:]:
    email, phone, name = (a.split("|") + ["", ""])[:3]
    admins.append((email.strip().lower(), phone.strip(), name.strip()))
if not admins:
    sys.exit("refusing to purge with no admins to keep")

c = duckdb.connect(db)
before = {t: c.execute(f"select count(*) from {t}").fetchone()[0]
          for (t,) in c.execute("select table_name from information_schema.tables where table_schema='main' order by 1").fetchall()}

WIPE = ["kaki_certificates", "availability_exceptions", "care_notes", "visit_reports", "visits",
        "care_plans", "households", "kaki_profiles", "otp_codes", "auth_attempts", "audit_log"]
c.execute("begin")
for t in WIPE:
    c.execute(f"delete from {t}")
keep = [e for e, _, _ in admins]
c.execute(f"delete from users where lower(coalesce(email,'')) not in ({','.join('?'*len(keep))})", keep)
for email, phone, name in admins:
    row = c.execute("select id from users where lower(email)=?", [email]).fetchone()
    if row:
        c.execute("""update users set role='admin', status='approved', phone=?, name=coalesce(nullif(?,''), name),
                     email_verified=true, phone_verified=true, photo='', lang='' where id=?""", [phone, name, row[0]])
    else:
        c.execute("""insert into users(id,email,name,phone,role,status,created_at,email_verified,phone_verified,photo,lang)
                     values (?,?,?,?,'admin','approved',current_timestamp,true,true,'','')""",
                  [uuid.uuid4().hex[:12], email, name, phone])
c.execute("insert into audit_log(actor, action, detail) values ('system', 'purge_for_pilot', ?)",
          [f"wiped all users/interactions; kept admins {', '.join(keep)}; previous counts {before}"])
c.execute("commit")
c.execute("checkpoint")

after = {t: c.execute(f"select count(*) from {t}").fetchone()[0] for t in before}
w = max(len(t) for t in before)
print(f"{'table':<{w}}  before  after")
for t in before:
    print(f"{t:<{w}}  {before[t]:>6}  {after[t]:>5}")
print()
for r in c.execute("select email, phone, name, role, status from users order by email").fetchall():
    print("kept:", r)
