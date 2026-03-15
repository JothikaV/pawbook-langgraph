"""
shared/mcp_server_base.py
FastAPI MCP (Model Context Protocol) server base class.
Implements JSON-RPC 2.0 protocol over HTTP.
"""
import json
import inspect
from typing import Any, Dict, Callable, Awaitable
from fastapi import FastAPI, Request
from pydantic import BaseModel

class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] | None = None
    id: str | int | None = None


def create_mcp_app(server_name: str, version: str, tools_registry: Dict[str, Dict[str, Any]]) -> FastAPI:
    """
    Create a FastAPI MCP server.

    tools_registry format:
    {
        "tool_name": {
            "description": "...",
            "inputSchema": {...},  # JSON Schema
            "handler": async_function_or_sync_function
        }
    }
    """
    app = FastAPI(title=server_name)

    @app.get("/")
    async def server_info():
        """GET / returns server metadata."""
        return {
            "mcp": True,
            "name": server_name,
            "version": version,
            "tools": [
                {
                    "name": tool_name,
                    "description": meta["description"],
                    "inputSchema": meta.get("inputSchema", {}),
                }
                for tool_name, meta in tools_registry.items()
            ],
        }

    @app.post("/mcp")
    async def mcp_handler(req: JsonRpcRequest):
        """POST /mcp handles JSON-RPC 2.0 requests."""
        method = req.method
        params = req.params or {}
        request_id = req.id

        try:
            # Initialize
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": server_name, "version": version},
                }

            # List tools
            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": tool_name,
                            "description": meta["description"],
                            "inputSchema": meta.get("inputSchema", {}),
                        }
                        for tool_name, meta in tools_registry.items()
                    ]
                }

            # Call a tool
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})

                if tool_name not in tools_registry:
                    return {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": f"Tool '{tool_name}' not found",
                        },
                        "id": request_id,
                    }

                handler = tools_registry[tool_name]["handler"]

                # Call handler (async or sync)
                if inspect.iscoroutinefunction(handler):
                    tool_result = await handler(**tool_args)
                else:
                    tool_result = handler(**tool_args)

                # Wrap result in MCP content format
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(tool_result, indent=2, default=str),
                        }
                    ],
                    "isError": False,
                }

            # Notifications/initialized
            elif method == "notifications/initialized":
                result = {}

            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found",
                    },
                    "id": request_id,
                }

            # Success response
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id,
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
                "id": request_id,
            }

    return app
