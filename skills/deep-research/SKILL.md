---
name: deep-research
description: Orchestrate a multi-phase deep research session using MCP tools and companion plugins
user_invocable: true
argument-hint: "<research query>"
---

# /interdeep:deep-research

Orchestrate a deep research session: decompose a query, search multiple sources, extract and evaluate content, synthesize findings, and persist the result.

## Protocol

Execute these five phases in order. Adapt depth based on the mode (see Depth Modes below).

### Phase 1: Orient

1. Use the **research-planner** agent to decompose the query into sub-queries with source routing.
2. Review the planner output: `query_type`, `sub_queries` (each with `query`, `sources`, `priority`), `depth_recommendation`, `rationale`.
3. If the user did not specify a depth mode, use the planner's `depth_recommendation`.

### Phase 2: Search

For each sub-query, dispatch searches to the routed sources:

- **Web search** — call `interject_search` (interject plugin) or `web_search_exa` (interflux/exa plugin):
  ```
  mcp tool: interject_search
  args: { "query": "<sub_query>", "source": "exa", "max_results": 10 }
  ```
- **Academic** — call `interject_search` with `"source": "arxiv"`.
- **Knowledge base** — call `interknow_qmd__search` or `interknow_qmd__vector_search` (interknow plugin) for local knowledge.
- **Cached results** — check `intercache` if available to avoid redundant fetches.

Collect URLs and snippets from all search results.

### Phase 3: Extract

For each URL returned in Phase 2:

1. Call `extract_content` (interdeep MCP tool) for single URLs:
   ```
   mcp tool: extract_content
   args: { "url": "<url>", "include_metadata": true }
   ```
2. For batches (5+ URLs), use `extract_batch`:
   ```
   mcp tool: extract_batch
   args: { "urls": ["<url1>", "<url2>", ...], "max_concurrent": 5 }
   ```
3. Use the **source-evaluator** agent on each extraction result to score relevance and credibility.
4. Filter to sources where `include_in_report` is true.

### Phase 4: Synthesize

1. If interlens is available, call `detect_thinking_gaps` to identify blind spots:
   ```
   mcp tool: detect_thinking_gaps
   args: { "context": "<research summary so far>" }
   ```
2. If gaps are found and depth mode is `deep`, run additional searches targeting the gaps.
3. Pass evaluated findings to the **report-compiler** agent.
4. Alternatively, call `compile_report` (interdeep MCP tool) for a structured markdown report:
   ```
   mcp tool: compile_report
   args: {
     "title": "<report title>",
     "query": "<original query>",
     "findings": [...],
     "sources": [...]
   }
   ```
5. If intersynth is available, use it for additional synthesis passes.

### Phase 5: Persist

1. **Save to filesystem** — always write the report to a `research/` directory in the current working directory:
   - Create the `research/` directory if it doesn't exist.
   - Filename format: `research/YYYY-MM-DD-<slug>.md` where `<slug>` is a short kebab-case summary of the query (max 60 chars).
   - If a file with the same name already exists, append `-2`, `-3`, etc.
   - The saved file should include the full report with all sections from the Output Contract.
2. If interknow is available, also store the report for future retrieval:
   ```
   mcp tool: interknow_qmd__search
   ```
   (Check for duplicates before storing.)
3. Present the final report to the user, noting the saved file path.
4. Call `research_status` to confirm extraction capabilities used:
   ```
   mcp tool: research_status
   args: {}
   ```

## Depth Modes

| Mode | Sub-queries | Sources per query | Extract limit | Thinking gaps |
|------|-------------|-------------------|---------------|---------------|
| `quick` | 1-2 | 1-2 | 5 URLs | skip |
| `balanced` | 3-5 | 2-3 | 15 URLs | if available |
| `deep` | 5-10 | all available | 30+ URLs | required |

Default: `balanced` unless the planner recommends otherwise.

## Companion Plugins

| Plugin | Role | Required? |
|--------|------|-----------|
| interject | Search providers (Exa, arXiv, HN, GitHub) | recommended |
| interflux/exa | Alternative web search via Exa | optional |
| interknow | Knowledge base storage and retrieval | optional |
| intercache | Result caching to avoid redundant fetches | optional |
| interlens | Thinking gap detection and lens analysis | optional |
| intersynth | Advanced synthesis passes | optional |

interdeep works standalone (extract + compile) but reaches full capability with companion plugins.

## Output Contract

The skill produces a markdown report with these sections:

1. **Executive Summary** — 2-3 sentence overview
2. **Key Findings** — organized by theme, each with confidence level
3. **Detailed Analysis** — full exploration of each theme
4. **Recommendations** — actionable next steps
5. **Sources** — bibliography with relevance annotations
6. **Methodology** — depth mode used, sources searched, extraction stats

The report is returned as a single markdown document in the chat.
