#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Starting TEQuest container..."

# Provide defaults if not set (useful for local dev)
: "${DJANGO_SETTINGS_MODULE:=config.settings}"
export DJANGO_SETTINGS_MODULE

# Wait for Postgres if DATABASE_URL references it
if [[ "${DATABASE_URL:-}" == postgres* ]]; then
  echo "[entrypoint] Waiting for database to be ready..."
  # Extract host and port using python to be robust
  python - <<'PYCODE'
import os, sys, time, socket
from urllib.parse import urlparse

url = os.getenv("DATABASE_URL")
if not url:
    sys.exit(0)

p = urlparse(url)
host, port = p.hostname or "db", p.port or 5432

for i in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"[entrypoint] DB reachable at {host}:{port}")
            sys.exit(0)
    except OSError:
        print(f"[entrypoint] Waiting for DB at {host}:{port}... ({i+1}/60)")
        time.sleep(2)
print("[entrypoint] ERROR: Database not reachable within timeout", file=sys.stderr)
sys.exit(1)
PYCODE
fi

echo "[entrypoint] Applying migrations..."
python manage.py migrate --noinput || { echo "[entrypoint] migrate failed"; exit 1; }

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput || echo "[entrypoint] collectstatic had warnings or failed (continuing)."

echo "[entrypoint] Ensuring superuser (if ADMIN_* env vars provided)..."
python manage.py ensure_superuser || echo "[entrypoint] ensure_superuser not executed or failed (continuing)."

echo "[entrypoint] Launching app: $*"
exec "$@"
