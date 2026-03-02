"""interdeep MCP server — content extraction and research orchestration tools."""

# Patch certifi to prefer system CA bundle when available.
# certifi ships only Mozilla's root store, which is missing some intermediates
# (e.g. SSL.com Transit CAs used by Cloudflare). trafilatura hardcodes
# certifi.where() in its PoolManager, so env vars don't help.
import os as _os
_sys_ca = "/etc/ssl/certs/ca-certificates.crt"
if _os.path.isfile(_sys_ca):
    import certifi
    certifi.where = lambda: _sys_ca

import asyncio
import json
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .extraction.hybrid import extract_hybrid_async, extract_batch_async
from .extraction.models import ExtractionResult
from .extraction import playwright_ext
from .reports.markdown import compile_markdown_report

logger = logging.getLogger("interdeep")
app = Server("interdeep")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok(data: dict) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _err(msg: str) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps({"error": msg}))]


def _result_to_dict(r: ExtractionResult) -> dict:
    return {
        "url": r.url,
        "title": r.title,
        "content": r.content,
        "method": r.method,
        "content_length": r.content_length,
        "extracted_at": r.extracted_at.isoformat(),
        "metadata": r.metadata,
    }


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="extract_content",
            description="Extract clean text/markdown content from a URL using trafilatura (fast) with optional Playwright fallback (JS-rendered pages).",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to extract content from.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Fetch timeout in seconds (default 10).",
                        "default": 10,
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="extract_batch",
            description="Extract content from multiple URLs concurrently. Returns a list of extraction results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to extract content from.",
                    },
                    "max_concurrent": {
                        "type": "integer",
                        "description": "Maximum concurrent extractions (default 5).",
                        "default": 5,
                    },
                },
                "required": ["urls"],
            },
        ),
        Tool(
            name="compile_report",
            description="Compile research findings and sources into a structured markdown report with citations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Report title.",
                    },
                    "query": {
                        "type": "string",
                        "description": "The original research query.",
                        "default": "",
                    },
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "content": {"type": "string"},
                                "confidence": {"type": "string"},
                            },
                        },
                        "description": "List of findings, each with title, content, and optional confidence.",
                    },
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"},
                                "title": {"type": "string"},
                                "relevance": {"type": "string"},
                            },
                        },
                        "description": "List of sources, each with url, title, and optional relevance.",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata key-value pairs for the report frontmatter.",
                    },
                },
                "required": ["title", "findings", "sources"],
            },
        ),
        Tool(
            name="research_status",
            description="Show extraction capabilities and companion plugin readiness.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

async def _handle_extract_content(arguments: dict) -> list[TextContent]:
    url = arguments.get("url", "")
    if not url:
        return _err("url is required")
    timeout = arguments.get("timeout", 10)
    try:
        result = await extract_hybrid_async(url=url, timeout=timeout)
        return _ok(_result_to_dict(result))
    except Exception as e:
        logger.exception("extract_content failed for %s", url)
        return _err(f"Extraction failed: {e}")


async def _handle_extract_batch(arguments: dict) -> list[TextContent]:
    urls = arguments.get("urls", [])
    if not urls:
        return _err("urls is required and must be non-empty")
    max_concurrent = arguments.get("max_concurrent", 5)
    try:
        results = await extract_batch_async(urls, max_concurrent=max_concurrent)
        return _ok({"results": [_result_to_dict(r) for r in results]})
    except Exception as e:
        logger.exception("extract_batch failed")
        return _err(f"Batch extraction failed: {e}")


async def _handle_compile_report(arguments: dict) -> list[TextContent]:
    title = arguments.get("title", "Untitled Report")
    query = arguments.get("query", "")
    findings = arguments.get("findings", [])
    sources = arguments.get("sources", [])
    metadata = arguments.get("metadata")
    try:
        report = compile_markdown_report(
            title=title,
            findings=findings,
            sources=sources,
            query=query,
            metadata=metadata,
        )
        return _ok({"report": report})
    except Exception as e:
        logger.exception("compile_report failed")
        return _err(f"Report compilation failed: {e}")


async def _handle_research_status(arguments: dict) -> list[TextContent]:
    trafilatura_available = False
    try:
        import trafilatura  # noqa: F401
        trafilatura_available = True
    except ImportError:
        pass

    pw_available = playwright_ext.is_available()

    return _ok({
        "extraction": {
            "trafilatura": trafilatura_available,
            "playwright": pw_available,
        },
        "tools": ["extract_content", "extract_batch", "compile_report", "research_status"],
        "version": "0.1.0",
    })


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_HANDLERS = {
    "extract_content": _handle_extract_content,
    "extract_batch": _handle_extract_batch,
    "compile_report": _handle_compile_report,
    "research_status": _handle_research_status,
}


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = _HANDLERS.get(name)
    if handler is None:
        return _err(f"Unknown tool: {name}")
    return await handler(arguments)


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def cli_main():
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
