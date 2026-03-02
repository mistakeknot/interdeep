#!/usr/bin/env bash
set -euo pipefail
if command -v ic &>/dev/null; then
    exec ic publish "${1:---patch}"
else
    echo "ic not available — use interbump.sh" >&2
    exit 1
fi
