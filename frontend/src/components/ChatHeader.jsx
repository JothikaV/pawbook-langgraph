import React from 'react';

export function ChatHeader({ status }) {
  return (
    <div className="chat-head">
      <div>
        <div className="ch-t">PawBook Agent</div>
        <div className="ch-s">
          {status ? `Ready • ${status.toolCount || 0} tools` : 'Connecting...'}
        </div>
      </div>
      <div className="badges">
        <div className="badge lg">
          <span className="b-dot"></span>
          LangGraph
        </div>
        <div className="badge mcp">
          <span className="b-dot"></span>
          MCP
        </div>
      </div>
    </div>
  );
}
