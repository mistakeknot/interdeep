# interdeep

Deep research plugin for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Extracts clean content from web pages and orchestrates multi-phase research sessions that produce structured markdown reports.

interdeep provides the content extraction backbone for research workflows. It pairs with companion plugins like [interject](https://github.com/mistakeknot/interject) (search) and [interknow](https://github.com/mistakeknot/interknow) (knowledge storage) for a complete research pipeline, but works standalone for extraction and report compilation.

## Installation

```bash
# Install from the Interverse marketplace
claude plugin install interdeep

# Install with browser extraction support (optional)
cd ~/.claude/plugins/interdeep && uv pip install -e ".[browser]" && playwright install chromium
```

## Usage

### Slash Command

```
/interdeep:research what are the best practices for MCP server design
/interdeep:research quick trafilatura vs readability comparison
/interdeep:research deep autonomous agent architectures and failure modes
```

### MCP Tools (programmatic)

The plugin exposes 4 MCP tools that any agent can call:

- **`extract_content`** — Extract clean text from a single URL
- **`extract_batch`** — Extract from multiple URLs concurrently
- **`compile_report`** — Compile findings into a structured markdown report
- **`research_status`** — Check extraction capabilities (trafilatura, Playwright availability)

## Architecture

```
src/interdeep/
  server.py                # FastMCP server — 4 tools
  extraction/
    trafilatura_ext.py     # Fast extraction via trafilatura
    playwright_ext.py      # Browser fallback for JS pages
    hybrid.py              # Router: trafilatura-first strategy
  reports/
    markdown.py            # Structured report compiler

skills/deep-research/      # 5-phase research orchestration protocol
agents/                    # research-planner, source-evaluator, report-compiler
commands/research.md       # /research slash command
```

## Design Decisions

- **Extraction + orchestration only** — interdeep does not own search. Search providers come from companion plugins (interject, interflux/exa).
- **trafilatura-first** — Fast path handles most pages. Playwright is an optional fallback for JavaScript-heavy sites, not a requirement.
- **Host-agent-as-brain** — MCP tools are stateless utilities. Research intelligence lives in the skill definition and agent prompts, executed by Claude as the host agent.
- **Graceful degradation** — Every component works standalone. Missing companion plugins reduce capability, they do not break the pipeline.

## License

MIT
