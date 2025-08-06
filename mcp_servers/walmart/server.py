import contextlib
import json
import logging
import os

from collections.abc import AsyncIterator
from typing import List

import click
import uvicorn
import mcp.types as types

from dotenv import load_dotenv
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from tools import (
    auth_token_context,
    walmart_product_search,
    walmart_store_search,
    walmart_category_search
)

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

WALMART_MCP_SERVER_PORT = int(os.getenv("WALMART_MCP_SERVER_PORT", "5000"))

@click.command()
@click.option("--port", default=WALMART_MCP_SERVER_PORT, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses for StreamableHTTP instead of SSE streams",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create the MCP server instance
    app = Server("walmart-mcp-server")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="walmart_product_search",
                description="""
                Search for Walmart products.

                Typical use: search for products by query, with optional filters for price, category, availability, and sorting.
                """,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Required. The product search query."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results to return (max 50, default 10)."
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Zero-based offset for pagination."
                        },
                        "sort": {
                            "type": "string",
                            "enum": ["relevance", "price_low", "price_high", "rating", "newest"],
                            "description": "Sort order for results."
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Minimum price filter."
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price filter."
                        },
                        "in_stock": {
                            "type": "boolean",
                            "description": "Filter for in-stock items only."
                        },
                        "category_id": {
                            "type": "string",
                            "description": "Filter by specific category ID."
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="walmart_store_search",
                description="""
                Search for Walmart stores near a location.

                Typical use: find Walmart stores by zip code, city, or coordinates.
                """,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Required. Location to search (zip code, city, or coordinates)."
                        },
                        "radius": {
                            "type": "integer",
                            "description": "Search radius in miles (default 25)."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of stores to return (max 20, default 10)."
                        }
                    },
                    "required": ["location"]
                }
            ),
            types.Tool(
                name="walmart_category_search",
                description="""
                Search for Walmart product categories.

                Typical use: browse categories or find specific category information.
                """,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Optional. Category name to search for."
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "Optional. Parent category ID to get subcategories."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of categories to return (max 50, default 20)."
                        }
                    }
                }
            )
        ]

    @app.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        
        try:
            if name == "walmart_product_search":
                result = await walmart_product_search(**arguments)
            elif name == "walmart_store_search":
                result = await walmart_store_search(**arguments)
            elif name == "walmart_category_search":
                result = await walmart_category_search(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": str(e)}, indent=2)
            )]

    # Create Starlette app
    app = Starlette(
        routes=[
            Route("/", lambda request: Response("Walmart MCP Server")),
            Mount("/mcp", app),
        ]
    )

    async def handle_sse(request):
        """Handle Server-Sent Events."""
        async def event_stream():
            async with SseServerTransport() as (read, write):
                async for chunk in read():
                    yield f"data: {chunk}\n\n"
        
        return Response(event_stream(), media_type="text/event-stream")

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        """Handle StreamableHTTP requests."""
        async with StreamableHTTPSessionManager(
            scope, receive, send, json_response=json_response
        ) as session:
            async with SseServerTransport() as (read, write):
                async for chunk in read():
                    await session.send(chunk)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        yield

    app = Starlette(
        routes=[
            Route("/", lambda request: Response("Walmart MCP Server")),
            Route("/sse", handle_sse),
            Mount("/mcp", app),
        ],
        lifespan=lifespan,
    )

    uvicorn.run(app, host="0.0.0.0", port=port)
    return 0

if __name__ == "__main__":
    main() 