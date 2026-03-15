import React from 'react';
import { LangGraphTopology } from './LangGraphTopology';
import { MCPServersPanel } from './MCPServersPanel';
import { ContextPanel } from './ContextPanel';
import { QuickPrompts } from './QuickPrompts';

export function Sidebar({
  activeNode,
  doneNodes,
  doneServers,
  status,
  sessionContext,
  onSelectPrompt,
}) {
  return (
    <aside className="lp">
      <div className="lp-head">
        <span className="logo-icon">🐾</span>
        <div>
          <div className="logo-name">PawBook</div>
          <div className="logo-sub">LangGraph + MCP</div>
        </div>
      </div>
      <div className="lp-body">
        <LangGraphTopology activeNode={activeNode} doneNodes={doneNodes} />
        <MCPServersPanel status={status} doneServers={doneServers} />
        <ContextPanel sessionContext={sessionContext} />
        <QuickPrompts onSelectPrompt={onSelectPrompt} />
      </div>
    </aside>
  );
}
