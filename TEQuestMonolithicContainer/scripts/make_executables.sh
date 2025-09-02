#!/usr/bin/env bash
set -euo pipefail

# Make helper scripts executable for local runs (Docker sets this via image layer by default)
chmod +x ./entrypoint.sh || true
