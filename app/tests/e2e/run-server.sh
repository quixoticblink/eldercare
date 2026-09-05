#!/usr/bin/env bash
# Starts a throwaway Kakis backend for the Playwright suite.
# Fresh DuckDB every run; assumptions.json copied so the rate-editing screens
# can never touch the real file. Sign-in codes come back in the API response
# (DEV_MODE=1) so tests read them without an SMS provider.
set -euo pipefail
cd "$(dirname "$0")/../.."

export DB_PATH="${E2E_DB_PATH:-/tmp/kakis-e2e.duckdb}"
export DEV_MODE=1
export ADMIN_EMAILS="admin@e2e.test"
export JWT_SECRET="e2e-not-secret"
export PORT="${E2E_PORT:-8100}"
export SMS_ENABLED=0
export TZ=Asia/Singapore
# Every spec seeds six accounts from one address; the production cap (200 per
# IP per 15 min) is asserted in smoke.py, not here.
export RATE_LIMIT_CODE_PER_IP=100000

rm -f "$DB_PATH" "$DB_PATH.wal"
TMP="$(mktemp -d /tmp/kakis-e2e-assumptions.XXXXXX)"
cp assumptions.json "$TMP/assumptions.json"
export ASSUMPTIONS_PATH="$TMP/assumptions.json"

PY=".venv/bin/python"
[ -x "$PY" ] || PY="python3"
exec "$PY" -m uvicorn backend.main:app --host 127.0.0.1 --port "$PORT" --log-level warning
