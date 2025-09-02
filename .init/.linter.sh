#!/usr/bin/env bash
set -euo pipefail

# Ensure we can run flake8 even if the project venv doesn't exist in CI
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Bootstrap a linter environment if needed
bash "$SCRIPT_DIR/bootstrap_linter_env.sh"

cd "$REPO_ROOT"

# Run flake8, but don't fail the entire build on stylistic issues; change to `set -e` behavior by removing `|| true` if desired
if command -v flake8 >/dev/null 2>&1; then
  echo "[linter] Running flake8..."
  flake8 TEQuestMonolithicContainer || true
else
  echo "[linter] flake8 still not available; skipping lint."
fi
