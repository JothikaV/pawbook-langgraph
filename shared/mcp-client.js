/**
 * shared/mcp-client.js
 *
 * MCP Client — connects the agent to individual MCP servers.
 * Speaks JSON-RPC 2.0 over HTTP POST /mcp.
 * Caches tool lists after the first tools/list call.
 */

let _reqId = 1;
const nextId = () => _reqId++;

class McpClient {
  constructor({ name, url }) {
    this.name       = name;
    this.url        = url.replace(/\/$/, '');
    this._toolCache = null;
  }

  // ── Send a JSON-RPC request ───────────────────────────────
  async _rpc(method, params = {}) {
    const response = await fetch(`${this.url}/mcp`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ jsonrpc: '2.0', id: nextId(), method, params }),
    });

    if (!response.ok) {
      throw new Error(`MCP server "${this.name}" returned HTTP ${response.status}`);
    }

    const json = await response.json();
    if (json.error) {
      throw new Error(`MCP error from "${this.name}": ${json.error.message}`);
    }
    return json.result;
  }

  // ── Initialize the connection ─────────────────────────────
  async initialize() {
    const result = await this._rpc('initialize', {
      protocolVersion: '2024-11-05',
      capabilities:    {},
      clientInfo:      { name: 'pawbook-agent', version: '1.0.0' },
    });
    await this._rpc('notifications/initialized');
    return result;
  }

  // ── List available tools (cached) ─────────────────────────
  async listTools() {
    if (!this._toolCache) {
      const result     = await this._rpc('tools/list');
      this._toolCache  = result.tools || [];
    }
    return this._toolCache;
  }

  // ── Call a tool ───────────────────────────────────────────
  async callTool(name, args) {
    const result = await this._rpc('tools/call', { name, arguments: args });
    // Parse the text content back to an object
    const text = result.content?.[0]?.text;
    try { return JSON.parse(text); } catch { return { raw: text }; }
  }

  // ── Health check ──────────────────────────────────────────
  async ping() {
    try {
      const response = await fetch(`${this.url}/`, { signal: AbortSignal.timeout(2000) });
      return response.ok;
    } catch {
      return false;
    }
  }
}

module.exports = McpClient;
