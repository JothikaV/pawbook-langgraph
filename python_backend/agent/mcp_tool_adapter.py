"""
agent/mcp_tool_adapter.py
Converts MCP tools to LangChain StructuredTools (synchronously).
Uses sync httpx client to avoid async/event loop conflicts with LangGraph.
"""
import json
import time
from typing import Any, Dict, List
from pydantic import BaseModel, create_model
from langchain_core.tools import StructuredTool
from shared.mcp_client import McpClient
from shared.logger import setup_logger

logger = setup_logger("MCPToolAdapter")


MCP_SERVERS = {
    "availability": "http://localhost:3101",
    "pricing": "http://localhost:3102",
    "booking": "http://localhost:3103",
    "notification": "http://localhost:3104",
}


def json_schema_to_pydantic(schema: Dict[str, Any], model_name: str) -> type[BaseModel]:
    """Convert JSON Schema to a Pydantic model."""
    if not schema or schema.get("type") != "object":
        return create_model(model_name)

    properties = schema.get("properties", {})
    required = schema.get("required", [])

    fields = {}
    for prop_name, prop_schema in properties.items():
        prop_type = prop_schema.get("type", "string")
        is_required = prop_name in required

        # Map JSON schema types to Python types
        if prop_type == "string":
            py_type = str
        elif prop_type in ("number", "integer"):
            py_type = int if prop_type == "integer" else float
        elif prop_type == "boolean":
            py_type = bool
        elif prop_type == "array":
            py_type = List[str]
        elif prop_type == "object":
            py_type = Dict[str, Any]
        else:
            py_type = str

        # Make optional if not required
        if is_required:
            fields[prop_name] = (py_type, ...)
        else:
            fields[prop_name] = (py_type, None)

    return create_model(model_name, **fields)


# Global clients dict to keep connections alive
_mcp_clients = {}

async def build_mcp_langchain_tools_async() -> Dict[str, Any]:
    """
    Discover MCP tools and wrap them as LangChain StructuredTools (async).
    Returns: {"langchain_tools": [...], "tool_metadata": {...}}
    """
    global _mcp_clients
    langchain_tools = []
    tool_metadata = {}

    logger.info("=== BUILDING MCP LANGCHAIN TOOLS ===")
    # Connect to each MCP server
    for server_name, server_url in MCP_SERVERS.items():
        logger.info(f"Connecting to {server_name} at {server_url}...")
        client = McpClient(server_url)
        _mcp_clients[server_name] = client  # Keep client alive globally

        try:
            # Initialize and list tools
            await client.initialize()
            logger.info(f"✅ Initialized {server_name}")

            tools_list = await client.list_tools()
            logger.info(f"✅ [MCP→LangChain] \"{server_name}\" — wrapping {len(tools_list)} tools")

            # Convert each MCP tool to LangChain StructuredTool
            for tool_info in tools_list:
                tool_name = tool_info.get("name")
                description = tool_info.get("description", "")
                input_schema = tool_info.get("inputSchema", {})

                # Create Pydantic model for args
                args_model = json_schema_to_pydantic(input_schema, f"{tool_name}_args")

                # Create synchronous wrapper that calls MCP tool
                def make_tool_func(t_name: str, t_server_url: str, t_server: str):
                    def tool_func(**kwargs) -> Dict[str, Any]:
                        # Use synchronous httpx client to avoid async/event loop issues
                        try:
                            import httpx
                            start_ms = int(time.time() * 1000)

                            # Make synchronous HTTP call directly
                            with httpx.Client(timeout=10.0) as client:
                                payload = {
                                    "jsonrpc": "2.0",
                                    "method": "tools/call",
                                    "params": {
                                        "name": t_name,
                                        "arguments": kwargs,
                                    },
                                    "id": "1",
                                }

                                resp = client.post(f"{t_server_url}/mcp", json=payload)
                                resp.raise_for_status()
                                data = resp.json()

                                # Check for JSON-RPC error
                                if "error" in data:
                                    raise Exception(f"RPC Error: {data['error']}")

                                # Parse result
                                result_data = data.get("result", {})

                                # Extract tool result from content
                                content = result_data.get("content", [])
                                if content and len(content) > 0:
                                    text = content[0].get("text", "{}")
                                    try:
                                        result = json.loads(text)
                                    except json.JSONDecodeError:
                                        result = {"error": "Failed to parse tool response"}
                                else:
                                    result = result_data

                                elapsed_ms = int(time.time() * 1000) - start_ms

                                # Attach metadata for UI inspector
                                result["_meta"] = {
                                    "tool": t_name,
                                    "server": t_server,
                                    "serverUrl": t_server_url,
                                    "elapsed": f"{elapsed_ms}ms",
                                    "args": kwargs,
                                    "timestamp": time.time(),
                                }
                                return result

                        except Exception as e:
                            logger.error(f"Tool {t_name} failed: {e}", exc_info=True)
                            return {
                                "error": str(e),
                                "_meta": {
                                    "tool": t_name,
                                    "server": t_server,
                                    "serverUrl": t_server_url,
                                    "args": kwargs,
                                }
                            }
                    return tool_func

                # Create StructuredTool
                tool_func = make_tool_func(tool_name, server_url, server_name)
                structured_tool = StructuredTool(
                    name=tool_name,
                    description=description,
                    func=tool_func,
                    args_schema=args_model,
                )

                langchain_tools.append(structured_tool)
                tool_metadata[tool_name] = {
                    "server": server_name,
                    "server_url": server_url,
                }

        except Exception as e:
            logger.error(f"❌ Failed to connect to {server_name}: {e}")

    logger.info(f"=== TOOLS BUILT: {len(langchain_tools)} tools total ===")
    return {
        "langchain_tools": langchain_tools,
        "tool_metadata": tool_metadata,
    }


# For backward compatibility (not used in async context)
def build_mcp_langchain_tools():
    """Synchronous wrapper that calls async build_mcp_langchain_tools_async."""
    try:
        loop = asyncio.get_running_loop()
        # If we're already in an event loop, this won't work
        logger.error("Cannot use sync wrapper from async context. Use build_mcp_langchain_tools_async instead.")
        raise RuntimeError("Use build_mcp_langchain_tools_async in async context")
    except RuntimeError:
        # No running loop, safe to use asyncio.run
        return asyncio.run(build_mcp_langchain_tools_async())
