#!/usr/bin/env bash
# Run the Playwright suite (or a subset) with a clean port and a log file.
#   tests/e2e/run.sh                 # everything
#   tests/e2e/run.sh lifecycle       # one spec by name fragment
#   tests/e2e/run.sh -g "on the way" # grep by test title
cd "$(dirname "$0")/../.."
lsof -ti tcp:8100 | xargs -r kill -9 2>/dev/null || true
sleep 0.5
npx playwright test "$@" > /tmp/e2e.log 2>&1
code=$?
grep -E "✓|✘|passed|failed|flaky|Error:|Expected|Received|expect\(|Timeout|timed out" /tmp/e2e.log | head -60
echo "EXIT=$code"
exit $code
