import React from 'react';
import { MCP_SERVERS } from '../constants/config';

export function MCPServersPanel({ status, doneServers }) {
  return (
    <div className="sec">
      <div className="sec-lbl">MCP Servers</div>
      <div className="mcp-cards">
        {MCP_SERVERS.map(server => {
          const isDone = doneServers.has(server.id);
          const isOnline = status?.mcpServers?.find(s => s.name.toLowerCase() === server.name.toLowerCase())?.online;

          return (
            <div key={server.id} className={`mc ${isDone ? 'done' : ''}`}>
              <div className="mc-top">
                <span className="mc-name">
                  {server.icon} {server.name}
                </span>
                <span className="mc-port">:{server.port}</span>
              </div>
              <div className="mc-tools">
                {server.tools.map(tool => (
                  <span key={tool} className="mc-t">
                    {tool}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
