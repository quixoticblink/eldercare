#!/usr/bin/env bash
# Full verification: smoke (backend, TestClient) then the Playwright suite.
# Writes /tmp/check.out; poll it. Never claim green without reading it.
cd "$(dirname "$0")/../.."
{
  echo "== smoke"
  .venv/bin/python backend/tests/smoke.py > /tmp/smoke.log 2>&1
  s=$?
  tail -1 /tmp/smoke.log
  [ $s -ne 0 ] && grep -B2 -A12 "Traceback\|AssertionError" /tmp/smoke.log | tail -30
  echo "SMOKE_EXIT=$s"
  echo "== e2e"
  tests/e2e/run.sh "$@"
  echo "DONE"
} > /tmp/check.out 2>&1
