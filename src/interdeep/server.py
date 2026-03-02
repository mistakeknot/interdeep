"""interdeep MCP server — content extraction and research orchestration tools."""

import asyncio
import json
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logger = logging.getLogger("interdeep")
app = Server("interdeep")


def _ok(data: dict) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _err(msg: str) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps({"error": msg}))]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return []


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    return _err(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def cli_main():
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
