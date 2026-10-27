#!/usr/bin/env bash
# Read-only; use the authenticated local CLI. Cross-platform Python is also usable.
set -euo pipefail
python3 "$(dirname "$0")/azure_preflight.py" "$@"
