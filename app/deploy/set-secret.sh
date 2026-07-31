#!/bin/bash
# Set one value in the Kakis .env without it ever touching shell history.
#
#   sudo /home/kakis/eldercare/app/deploy/set-secret.sh RESEND_API_KEY
#
# Prompts silently for the value, rewrites the key in place (or appends it),
# keeps the file at mode 600 owned by kakis, and restarts the service.
# Passing the value as an argument is deliberately NOT supported — that is how
# secrets end up in ~/.bash_history and in `ps` output.
set -euo pipefail

ENV_FILE=/home/kakis/eldercare/app/.env
KEY="${1:-}"

if [ -z "$KEY" ]; then
  echo "usage: $0 KEY_NAME" >&2
  echo "  e.g. $0 RESEND_API_KEY" >&2
  exit 1
fi
if [ ! -f "$ENV_FILE" ]; then
  echo "no .env at $ENV_FILE" >&2
  exit 1
fi

printf 'Value for %s (input hidden): ' "$KEY" >&2
read -rs VALUE
echo >&2
if [ -z "$VALUE" ]; then
  echo "empty value — nothing changed" >&2
  exit 1
fi

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
if grep -q "^${KEY}=" "$ENV_FILE"; then
  # Rewrite the existing line. Done in awk so the value is never expanded by
  # the shell and never appears in a sed expression.
  KEY="$KEY" VALUE="$VALUE" awk '
    BEGIN { k = ENVIRON["KEY"]; v = ENVIRON["VALUE"] }
    index($0, k "=") == 1 { print k "=" v; next }
    { print }
  ' "$ENV_FILE" > "$TMP"
else
  cp "$ENV_FILE" "$TMP"
  KEY="$KEY" VALUE="$VALUE" awk 'BEGIN { print ENVIRON["KEY"] "=" ENVIRON["VALUE"] }' >> "$TMP"
fi

cat "$TMP" > "$ENV_FILE"
chown kakis:kakis "$ENV_FILE"
chmod 600 "$ENV_FILE"

echo "$KEY updated. Restarting kakis…" >&2
systemctl restart kakis
sleep 5
systemctl is-active kakis
echo "Now run the preflight check:" >&2
echo "  sudo -u kakis /home/kakis/eldercare/app/.venv/bin/python /home/kakis/eldercare/app/deploy/preflight.py" >&2
