# interdeep Philosophy

## Purpose

Deep research plugin for Claude Code. Extracts clean content from web pages and orchestrates multi-phase research sessions that compose extraction, search, evaluation, and synthesis into structured reports.

## North Star

Maximize research quality per token spent. Every extraction, every search query, every synthesis pass should contribute meaningfully to the final report. Avoid redundant fetches, avoid low-quality sources, avoid verbose intermediate processing.

## Working Priorities

1. Extraction quality — clean, complete content from diverse page types
2. Orchestration clarity — the research protocol should be legible and debuggable
3. Composition over coupling — work well with companion plugins, depend on none

## Brainstorming Doctrine

1. Start from outcomes and failure modes, not implementation details.
2. Generate at least three options: conservative, balanced, and aggressive.
3. Explicitly call out assumptions, unknowns, and dependency risk across modules.
4. Prefer ideas that improve clarity, reversibility, and operational visibility.

## Planning Doctrine

1. Convert selected direction into small, testable, reversible slices.
2. Define acceptance criteria, verification steps, and rollback path for each slice.
3. Sequence dependencies explicitly and keep integration contracts narrow.
4. Reserve optimization work until correctness and reliability are proven.

## Decision Filters

- Does this improve extraction quality or coverage for real-world pages?
- Does this reduce tokens spent without reducing research quality?
- Is the orchestration protocol still legible after this change?
- Can this work standalone (no companion plugins) while being better with them?
- Does this maintain the stateless MCP tool / intelligent skill boundary?

## Evidence Base

- Brainstorms analyzed: 0
- Plans analyzed: 0
- Source confidence: inferred (no local brainstorm/plan corpus found)
- Representative artifacts: none yet. Build this corpus over time under `docs/brainstorms/` and `docs/plans/`.
