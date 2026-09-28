"""Create (or promote) admin accounts directly in the DuckDB file, so they appear in
the console before the person has ever signed in. Stop the service first: the live
file cannot be opened while uvicorn holds it.

    sudo systemctl stop kakis
    sudo -u kakis /home/kakis/eldercare/app/.venv/bin/python deploy/add-admin.py \
        /home/kakis/kakis.duckdb "rusydi_yaakup@ncss.gov.sg||Rusydi Yaakup" "chermaine_teo@ncss.gov.sg||Chermaine Teo"
    sudo systemctl start kakis

Each argument is email|phone|name; phone may be empty. Existing rows with that
email are promoted to admin/approved and keep their other fields. Remember to add
the same emails to ADMIN_EMAILS in .env, otherwise nothing here is wrong but a
later re-creation would not be admin.
"""
import sys, uuid, duckdb

db, specs = sys.argv[1], sys.argv[2:]
if not specs:
    sys.exit("usage: add-admin.py <db> 'email|phone|name' ...")
c = duckdb.connect(db)
for s in specs:
    email, phone, name = (s.split("|") + ["", ""])[:3]
    email, phone, name = email.strip().lower(), phone.strip(), name.strip()
    row = c.execute("select id from users where lower(email)=?", [email]).fetchone()
    if row:
        c.execute("""update users set role='admin', status='approved', email_verified=true,
                     name=coalesce(nullif(?,''), name), phone=coalesce(nullif(?,''), phone) where id=?""",
                  [name, phone, row[0]])
        print("promoted:", email)
    else:
        c.execute("""insert into users(id,email,name,phone,role,status,created_at,email_verified,phone_verified,photo,lang)
                     values (?,?,?,?,'admin','approved',current_timestamp,true,?,'','')""",
                  [uuid.uuid4().hex[:12], email, name, phone, bool(phone)])
        print("created: ", email)
    c.execute("insert into audit_log(actor, action, detail) values ('system', 'admin_added', ?)", [email])
c.execute("checkpoint")
for r in c.execute("select email, phone, name, role, status from users order by email").fetchall():
    print(r)
