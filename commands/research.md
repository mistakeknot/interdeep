---
name: research
description: "Start a deep research session on a topic"
user_invocable: true
argument-hint: "[quick|balanced|deep] <research query>"
---

# /interdeep:research

Start a deep research session. This command invokes the `deep-research` skill with optional depth control.

## Usage

```
/interdeep:research <query>
/interdeep:research quick <query>
/interdeep:research balanced <query>
/interdeep:research deep <query>
```

## Examples

```
/interdeep:research what are the best practices for MCP server design in 2026
/interdeep:research quick trafilatura vs readability comparison
/interdeep:research deep autonomous agent architectures and their failure modes
/interdeep:research balanced recent advances in retrieval-augmented generation
```

## Behavior

1. Parse the first argument as a depth mode if it matches `quick`, `balanced`, or `deep`. Otherwise treat the entire argument as the query and use `balanced` as default.
2. Invoke the `deep-research` skill with the parsed query and depth mode.
3. The skill handles the full research pipeline: orient, search, extract, synthesize, persist.
4. Returns a structured markdown report in the chat.

## Depth Modes

- **quick** — Fast answer. 1-2 sub-queries, 5 URL limit. Best for factual lookups.
- **balanced** — Standard research. 3-5 sub-queries, 15 URL limit. Good for most topics.
- **deep** — Thorough investigation. 5-10 sub-queries, 30+ URLs, thinking gap analysis. Use for complex or high-stakes topics.
