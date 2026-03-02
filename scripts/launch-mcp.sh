#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if ! command -v uv &>/dev/null; then
    echo "uv not found — interdeep MCP server disabled." >&2
    exit 0
fi

if ! uv run --directory "$PROJECT_ROOT" python -c "import trafilatura" 2>/dev/null; then
    echo "trafilatura not installed — running uv sync first..." >&2
    uv sync --directory "$PROJECT_ROOT" 2>&1 >&2
fi

exec uv run --directory "$PROJECT_ROOT" interdeep-mcp "$@"
