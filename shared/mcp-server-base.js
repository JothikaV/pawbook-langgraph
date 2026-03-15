/**
 * shared/mcp-server-base.js
 *
 * Lightweight MCP server implementation using HTTP + JSON-RPC 2.0.
 * Implements the MCP protocol spec:
 *   - POST /mcp  → JSON-RPC endpoint (initialize, tools/list, tools/call)
 *   - GET  /     → server info
 *
 * Each MCP server extends this base and registers tools.
 */

const express = require('express');
const cors    = require('cors');

class McpServerBase {
  constructor({ name, version = '1.0.0', port }) {
    this.name    = name;
    this.version = version;
    this.port    = port;
    this.tools   = {};         // toolName → { description, inputSchema, handler }
    this.app     = express();
    this.app.use(cors());
    this.app.use(express.json());
    this._setupRoutes();
  }

  // ── Register a tool ───────────────────────────────────────
  registerTool(name, { description, inputSchema, handler }) {
    this.tools[name] = { description, inputSchema, handler };
  }

  // ── MCP JSON-RPC handler ──────────────────────────────────
  _setupRoutes() {
    // Info endpoint
    this.app.get('/', (_, res) => res.json({
      mcp:     true,
      name:    this.name,
      version: this.version,
      tools:   Object.keys(this.tools),
    }));

    // Main MCP JSON-RPC endpoint
    this.app.post('/mcp', async (req, res) => {
      const { jsonrpc, id, method, params } = req.body;

      if (jsonrpc !== '2.0') {
        return res.json({ jsonrpc: '2.0', id, error: { code: -32600, message: 'Invalid Request' } });
      }

      try {
        let result;

        switch (method) {
          // ── initialize ───────────────────────────────────
          case 'initialize':
            result = {
              protocolVersion: '2024-11-05',
              capabilities:    { tools: {} },
              serverInfo:      { name: this.name, version: this.version },
            };
            break;

          // ── tools/list ───────────────────────────────────
          case 'tools/list':
            result = {
              tools: Object.entries(this.tools).map(([name, t]) => ({
                name,
                description:  t.description,
                inputSchema:  t.inputSchema,
              })),
            };
            break;

          // ── tools/call ───────────────────────────────────
          case 'tools/call': {
            const { name: toolName, arguments: toolArgs } = params;
            const tool = this.tools[toolName];

            if (!tool) {
              return res.json({ jsonrpc: '2.0', id, error: { code: -32601, message: `Tool not found: ${toolName}` } });
            }

            const callResult = await tool.handler(toolArgs || {});
            result = {
              content: [{ type: 'text', text: JSON.stringify(callResult, null, 2) }],
              isError: callResult.success === false,
            };
            break;
          }

          // ── notifications/initialized (no response needed) ─
          case 'notifications/initialized':
            return res.json({ jsonrpc: '2.0', id, result: {} });

          default:
            return res.json({ jsonrpc: '2.0', id, error: { code: -32601, message: `Method not found: ${method}` } });
        }

        res.json({ jsonrpc: '2.0', id, result });

      } catch (err) {
        res.json({ jsonrpc: '2.0', id, error: { code: -32603, message: err.message } });
      }
    });
  }

  // ── Start the server ──────────────────────────────────────
  start() {
    this.app.listen(this.port, () => {
      console.log(`  🔧 MCP Server "${this.name}" running on http://localhost:${this.port}`);
    });
  }
}

module.exports = McpServerBase;
