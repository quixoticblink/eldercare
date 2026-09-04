#!/usr/bin/env bash
# The crash that only appeared on the second boot (kakis-app.md): a migration
# that leaves a WAL entry DuckDB cannot replay after an unclean stop. Boot on a
# fresh DB, do a write, SIGKILL, boot again, and again from a clean stop.
set -u
: > /tmp/sb-server.log
cd "$(dirname "$0")/../.."
DB=/tmp/kakis-second-boot.duckdb
rm -f "$DB" "$DB.wal"
PY=".venv/bin/python"; [ -x "$PY" ] || PY=python3
boot() {
  DB_PATH="$DB" DEV_MODE=1 ADMIN_EMAILS=admin@sb.test PORT=8102 \
    "$PY" -m uvicorn backend.main:app --host 127.0.0.1 --port 8102 --log-level error >>/tmp/sb-server.log 2>&1 &
  echo $!
}
wait_health() {
  for i in $(seq 1 40); do
    curl -sf http://127.0.0.1:8102/api/health >/dev/null && return 0
    sleep 0.25
  done
  return 1
}
lsof -ti tcp:8102 | xargs -r kill -9 2>/dev/null || true
P=$(boot); wait_health || { echo "FIRST BOOT FAILED"; kill -9 $P; exit 1; }
curl -s -X POST http://127.0.0.1:8102/api/auth/request-code -H 'Content-Type: application/json' -d '{"identifier":"admin@sb.test"}' >/dev/null
kill -9 $P; sleep 0.5
P=$(boot); wait_health || { echo "SECOND BOOT (after SIGKILL) FAILED"; exit 1; }
kill -15 $P; sleep 0.5
P=$(boot); wait_health || { echo "THIRD BOOT (after clean stop) FAILED"; exit 1; }
kill -15 $P
echo "SECOND-BOOT OK"
grep -i "error\|exception" /tmp/sb-server.log | head -5
