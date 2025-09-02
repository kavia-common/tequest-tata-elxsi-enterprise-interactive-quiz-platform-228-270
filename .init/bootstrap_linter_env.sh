#!/usr/bin/env bash
set -euo pipefail

# This script creates a temporary virtual environment for linting if none exists
# and ensures flake8 is installed so .init/.linter.sh can execute successfully.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# If a project venv exists, prefer it
if [[ -d "venv" ]]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate" || true
fi

# Check if flake8 is available; if not, set up a temp venv
if ! command -v flake8 >/dev/null 2>&1; then
  echo "[bootstrap_linter_env] flake8 not found; creating a temporary venv..."
  python3 -m venv .lint-venv
  # shellcheck disable=SC1091
  source ".lint-venv/bin/activate"
  python -m pip install --upgrade pip
  pip install --no-cache-dir flake8
  echo "[bootstrap_linter_env] flake8 installed in .lint-venv"
fi

echo "[bootstrap_linter_env] Linter environment ready."
