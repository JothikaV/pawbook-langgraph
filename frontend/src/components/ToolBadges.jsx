import React from 'react';
import { MCP_SERVERS, TOOL_TO_SERVER } from '../constants/config';

export function ToolBadges({ toolsUsed }) {
  if (!toolsUsed || toolsUsed.length === 0) return null;

  return (
    <div className="tool-tags">
      <span className="tt lgt">⬡ LangGraph</span>
      {toolsUsed.map((tool, i) => {
        const serverId = TOOL_TO_SERVER[tool];
        const server = MCP_SERVERS.find(s => s.id === serverId);
        return (
          <span
            key={i}
            className="tt mcpt"
            title={server ? `MCP :${server.port}` : ''}
          >
            {server?.icon} {tool}
          </span>
        );
      })}
    </div>
  );
}
