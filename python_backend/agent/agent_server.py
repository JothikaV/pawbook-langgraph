"""
agent/agent_server.py
FastAPI agent server on port 3100.
Endpoints: POST /api/chat, GET /api/status, GET /api/health
"""
import os
import asyncio
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

from agent.graph import build_graph
from agent.mcp_tool_adapter import build_mcp_langchain_tools
from shared.mcp_client import McpClient
from shared.logger import setup_logger

logger = setup_logger("AgentServer")

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

app = FastAPI(title="PawBook Agent Server")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global state ─────────────────────────────────────────
graph = None
langchain_tools = []
tool_metadata = {}


@app.on_event("startup")
async def init_graph():
    """Initialize the graph on startup."""
    global graph, langchain_tools, tool_metadata

    logger.info("=== AGENT SERVER STARTUP ===")

    # Note: Ollama doesn't need API key, runs locally

    logger.info("Building LangChain tools from MCP servers...")
    # Call async function directly from async context
    from agent.mcp_tool_adapter import build_mcp_langchain_tools_async
    result = await build_mcp_langchain_tools_async()
    langchain_tools = result["langchain_tools"]
    tool_metadata = result["tool_metadata"]
    logger.info(f"✅ Loaded {len(langchain_tools)} LangChain tools")

    logger.info(f"Building LangGraph StateGraph with {len(langchain_tools)} tools...")
    graph = build_graph(langchain_tools)

    logger.info("✅ LangGraph StateGraph compiled successfully")
    logger.info(f"   Architecture: START → agent → [conditional_edge] → tools → agent → END")
    logger.info(f"   Tools available: {', '.join([t.name for t in langchain_tools])}")
    logger.info(f"   State type: messages + sessionContext + toolCallLog")
    logger.info("=== AGENT SERVER READY ===")


@app.post("/api/chat")
async def chat(request: Dict[str, Any]):
    """Main chat endpoint."""
    logger.info("=== /api/chat REQUEST ===")

    # Ollama doesn't require API key

    if not graph:
        logger.error("Graph not initialised")
        return {
            "error": "Graph not initialised yet. Please wait a moment."
        }, 503

    messages = request.get("messages", [])
    session_context = request.get("sessionContext", {})
    logger.info(f"Chat request - messages: {len(messages)}, sessionContext: {session_context}")

    try:
        # Convert to LangChain messages
        lc_messages = []
        for msg in messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(msg["content"]))

        # Invoke graph
        logger.info("Invoking LangGraph...")
        result = await asyncio.to_thread(graph.invoke, {
            "messages": lc_messages,
            "sessionContext": session_context,
            "toolCallLog": [],
            "lastNode": "idle",
        })
        logger.info("✅ Graph invocation completed")

        # Extract final message
        last_msg = result["messages"][-1] if result["messages"] else None
        response_text = ""
        tool_results = {}

        if last_msg:
            logger.info(f"Last message type: {type(last_msg)}, content type: {type(last_msg.content)}")
            if isinstance(last_msg.content, str):
                response_text = last_msg.content
            elif isinstance(last_msg.content, list):
                response_text = "".join(c.get("text", "") for c in last_msg.content if isinstance(c, dict))
            else:
                # Handle other content types
                response_text = str(last_msg.content)
            logger.info(f"Extracted response: {response_text[:100] if response_text else 'EMPTY'}")

        # Extract tool results from ToolMessages in the conversation
        import json
        from langchain_core.messages import ToolMessage
        for msg in result.get("messages", []):
            if isinstance(msg, ToolMessage):
                # Parse tool result (it's JSON string)
                try:
                    content = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                    tool_results[msg.tool_call_id] = {
                        "tool_call_id": msg.tool_call_id,
                        "content": content
                    }
                    logger.info(f"Extracted tool result from {msg.tool_call_id}")
                except (json.JSONDecodeError, AttributeError):
                    pass

        # Collect tools used
        tools_used = [entry["tool"] for entry in result.get("toolCallLog", [])]
        logger.info(f"Response generated - tools_used: {tools_used}, response_length: {len(response_text)}")

        logger.info("=== /api/chat RESPONSE ===")
        return {
            "message": response_text,
            "toolsUsed": tools_used,
            "toolCallLog": result.get("toolCallLog", []),
            "toolResults": tool_results,
            "contextUpdates": result.get("sessionContext", {}),
            "graphMeta": {
                "totalMessages": len(result.get("messages", [])),
                "toolCallCount": len(result.get("toolCallLog", [])),
                "lastNode": result.get("lastNode", "idle"),
            },
        }

    except Exception as e:
        logger.error(f"Graph invocation error: {e}", exc_info=True)
        # Don't return tuple - FastAPI will handle status codes
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Graph invocation failed: {e}"
            }
        )


@app.get("/api/status")
async def status():
    """Return server status."""
    logger.info("/api/status requested")
    mcp_servers = []

    for server_name, server_url in {
        "availability": "http://localhost:3101",
        "pricing": "http://localhost:3102",
        "booking": "http://localhost:3103",
        "notification": "http://localhost:3104",
    }.items():
        client = McpClient(server_url)
        online = await client.ping()
        await client.close()
        logger.info(f"  {server_name}: {'online' if online else 'offline'}")

        mcp_servers.append({
            "name": server_name,
            "url": server_url,
            "online": online,
        })

    return {
        "framework": "LangGraph + LangChain + MCP",
        "architecture": "StateGraph with agent, tools, and conditional routing",
        "llm": "Groq API (llama-3.3-70b-versatile - free)",
        "graphReady": graph is not None,
        "graphType": "PawBookGraph (StateGraph-based)",
        "nodes": ["START", "agent", "tools", "END"],
        "edges": ["START→agent", "agent→[conditional]", "[conditional]→tools", "tools→agent"],
        "toolCount": len(langchain_tools),
        "tools": [t.name for t in langchain_tools],
        "mcpServers": mcp_servers,
        "groqReady": bool(os.getenv("GROQ_API_KEY")),
        "mcp_protocol": "JSON-RPC 2.0 / HTTP POST",
    }


@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import os
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    print("[AGENT] ")
    print("[AGENT] 🐾 PawBook Agent Server on http://localhost:3100")
    print("[AGENT]    Framework:   LangGraph StateGraph + LangChain + MCP")
    print("[AGENT]    Architecture: START → agent → [conditional] → tools → agent → END")
    print("[AGENT]    LLM:         Groq API (llama-3.3-70b-versatile - free)")
    print("[AGENT]    Protocol:    MCP 2024-11-05 / JSON-RPC 2.0")
    print("[AGENT]    State:       messages + sessionContext + toolCallLog\n")
    uvicorn.run(app, host="0.0.0.0", port=3100, log_level="error")
