"""Export every table of a Kakis DuckDB file to CSV, one file per table.

Run on the box as the app user, against a *copy* of a backup (the live file cannot
be opened while the service holds it). Copy the .duckdb backup AND its .wal backup
side by side as kakis.duckdb / kakis.duckdb.wal so the last un-checkpointed rows
are replayed; the script opens the copy read-write for that reason, so never point
it at the live file or the backup itself:

    sudo -u kakis mkdir -p /home/kakis/export
    sudo -u kakis cp /home/kakis/kakis.duckdb.bak-<ts>     /home/kakis/export/kakis.duckdb
    sudo -u kakis cp /home/kakis/kakis.duckdb.wal.bak-<ts> /home/kakis/export/kakis.duckdb.wal
    sudo -u kakis /home/kakis/eldercare/app/.venv/bin/python \
        /home/kakis/eldercare/app/deploy/export-csv.py \
        /home/kakis/export/kakis.duckdb /home/kakis/export/csv

Then `scp` the csv directory down and turn it into a workbook locally. Photo and
certificate data URLs are dropped (they are base64 blobs, not data); the row
keeps a length instead.
"""
import sys, duckdb, os

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
c = duckdb.connect(src)
tables = [r[0] for r in c.execute(
    "select table_name from information_schema.tables where table_schema='main' order by 1").fetchall()]
BLOBS = {("users", "photo"), ("kaki_certificates", "data")}
for t in tables:
    cols = [r[0] for r in c.execute(
        f"select column_name from information_schema.columns where table_name='{t}' order by ordinal_position").fetchall()]
    sel = ", ".join(f"length({col}) as {col}_bytes" if (t, col) in BLOBS else col for col in cols)
    n = c.execute(f"select count(*) from {t}").fetchone()[0]
    c.execute(f"copy (select {sel} from {t}) to '{out}/{t}.csv' (header, delimiter ',')")
    print(f"{t}\t{n}")
