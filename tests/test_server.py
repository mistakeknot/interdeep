"""Tests for MCP server tool registration."""

import pytest
import asyncio
from interdeep.server import list_tools, call_tool


@pytest.fixture
def tools():
    return asyncio.run(list_tools())


def test_tools_are_registered(tools):
    names = [t.name for t in tools]
    assert "extract_content" in names
    assert "extract_batch" in names
    assert "compile_report" in names
    assert "research_status" in names


def test_extract_content_has_schema(tools):
    tool = next(t for t in tools if t.name == "extract_content")
    assert "url" in tool.inputSchema["properties"]
    assert "url" in tool.inputSchema["required"]


def test_unknown_tool_returns_error():
    result = asyncio.run(call_tool("nonexistent", {}))
    text = result[0].text
    assert "error" in text.lower() or "unknown" in text.lower()


def test_compile_report_tool():
    import json
    result = asyncio.run(call_tool("compile_report", {
        "title": "Test Report",
        "query": "test query",
        "findings": [{"title": "Finding 1", "content": "Some content", "confidence": "high"}],
        "sources": [{"url": "https://example.com", "title": "Example", "relevance": "primary"}],
    }))
    data = json.loads(result[0].text)
    assert "report" in data
    assert "Test Report" in data["report"]
    assert "Finding 1" in data["report"]
    assert "example.com" in data["report"]


def test_research_status_tool():
    import json
    result = asyncio.run(call_tool("research_status", {}))
    data = json.loads(result[0].text)
    assert "extraction" in data
    assert data["extraction"]["trafilatura"] is True
