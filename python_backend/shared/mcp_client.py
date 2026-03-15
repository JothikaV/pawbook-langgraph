"""
shared/mcp_client.py
Async HTTP client for calling MCP servers over JSON-RPC 2.0.
"""
import json
import time
import httpx
from typing import Any, Dict, Optional

class McpClient:
    """HTTP client for MCP servers (JSON-RPC 2.0 over HTTP)."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.tools_cache: Optional[Dict[str, Any]] = None
        self.client = httpx.AsyncClient(timeout=10.0)

    async def initialize(self) -> Dict[str, Any]:
        """Send initialize and notifications/initialized."""
        # Initialize
        init_resp = await self._send_rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "pawbook-agent", "version": "1.0.0"},
        })

        # Notifications/initialized
        await self._send_rpc("notifications/initialized", {})

        return init_resp

    async def list_tools(self) -> Dict[str, Any]:
        """List all tools. Results are cached."""
        if self.tools_cache is not None:
            return self.tools_cache

        resp = await self._send_rpc("tools/list", {})
        self.tools_cache = resp.get("tools", [])
        return self.tools_cache

    async def call_tool(self, name: str, args: Dict[str, Any]) -> tuple[Any, int]:
        """
        Call a tool and return (result, elapsed_ms).
        """
        start_ms = int(time.time() * 1000)

        resp = await self._send_rpc("tools/call", {
            "name": name,
            "arguments": args,
        })

        elapsed_ms = int(time.time() * 1000) - start_ms

        # Parse content[0].text as JSON
        content = resp.get("content", [])
        if content and len(content) > 0:
            text = content[0].get("text", "{}")
            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                result = {"error": "Failed to parse tool response"}
        else:
            result = resp

        return result, elapsed_ms

    async def ping(self) -> bool:
        """Ping server, return True if online."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.base_url}/")
                return resp.status_code == 200
        except Exception:
            return False

    async def _send_rpc(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC 2.0 request."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": "1",
        }

        try:
            resp = await self.client.post(f"{self.base_url}/mcp", json=payload)
            resp.raise_for_status()
            data = resp.json()

            # Check for JSON-RPC error
            if "error" in data:
                raise Exception(f"RPC Error: {data['error']}")

            return data.get("result", {})

        except Exception as e:
            raise Exception(f"MCP call failed: {e}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
