"""Structured markdown report compilation with citations."""

from datetime import datetime, timezone


def compile_markdown_report(
    title: str,
    findings: list[dict],
    sources: list[dict],
    query: str = "",
    metadata: dict | None = None,
) -> str:
    """Compile findings and sources into a structured markdown report."""
    meta = metadata or {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "---",
        f"title: \"{title}\"",
        f"date: {now}",
        f"query: \"{query}\"",
        f"sources_count: {len(sources)}",
        f"findings_count: {len(findings)}",
    ]
    if meta:
        for k, v in meta.items():
            lines.append(f"{k}: {v}")
    lines.extend(["---", "", f"# {title}", ""])

    if query:
        lines.extend([f"> **Research query:** {query}", ""])

    for i, finding in enumerate(findings, 1):
        section_title = finding.get("title", f"Finding {i}")
        content = finding.get("content", "")
        confidence = finding.get("confidence", "")
        lines.append(f"## {section_title}")
        if confidence:
            lines.append(f"*Confidence: {confidence}*")
        lines.extend(["", content, ""])

    if sources:
        lines.extend(["---", "", "## Sources", ""])
        for i, source in enumerate(sources, 1):
            url = source.get("url", "")
            stitle = source.get("title", url)
            relevance = source.get("relevance", "")
            line = f"{i}. [{stitle}]({url})"
            if relevance:
                line += f" — *{relevance}*"
            lines.append(line)
        lines.append("")

    return "\n".join(lines)
