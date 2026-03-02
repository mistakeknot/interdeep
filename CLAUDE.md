# interdeep

> See `AGENTS.md` for full development guide.

## Overview

Deep research plugin — 4 MCP tools (`extract_content`, `extract_batch`, `compile_report`, `research_status`), 1 skill (`deep-research`), 3 agents (`research-planner`, `source-evaluator`, `report-compiler`), 1 command (`/research`). Python MCP server with trafilatura + optional Playwright extraction. Composes with interject (search), intersynth (synthesis), interknow (knowledge), intercache (caching), interlens (thinking gaps).

## Quick Commands

```bash
# Run tests
uv run pytest tests/test_extraction.py tests/test_server.py -q

# Run structural tests
cd tests && uv sync && uv run pytest -q && cd ..

# Start MCP server
uv run interdeep-mcp

# Check extraction capability
uv run python -c "from interdeep.extraction.hybrid import extract_hybrid; print(extract_hybrid(html='<p>test</p>', url='https://x.com'))"
```

## Key Files

- `src/interdeep/server.py` — MCP server entrypoint (FastMCP, 4 tools)
- `src/interdeep/extraction/` — Content extraction layer
  - `models.py` — ExtractionResult dataclass
  - `trafilatura_ext.py` — trafilatura wrapper
  - `playwright_ext.py` — Playwright fallback (optional)
  - `hybrid.py` — Router: trafilatura-first, Playwright fallback
- `src/interdeep/reports/markdown.py` — Report compilation
- `skills/deep-research/SKILL.md` — 5-phase research orchestration protocol
- `agents/` — research-planner, source-evaluator, report-compiler
- `commands/research.md` — `/research` slash command

## Design Decisions (Do Not Re-Ask)

- Plugin owns extraction + orchestration only; search providers are interject's responsibility
- trafilatura fast path + optional Playwright fallback (graceful degradation)
- Host-agent-as-brain: MCP tools are stateless, orchestration intelligence lives in SKILL.md
- GPT-Researcher is inspire + port-partially, not a dependency
- No LangChain dependency — direct MCP protocol

## Plugin Publishing

Use `/interpub:release <version>` or `scripts/bump-version.sh <version>`.
