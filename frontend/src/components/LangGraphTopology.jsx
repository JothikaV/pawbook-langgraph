import React from 'react';
import { LANGGRAPH_NODES, LG_EDGES } from '../constants/config';

function getNodeStatus(nodeId, activeNode, doneNodes) {
  if (activeNode === nodeId) return 'active';
  if (doneNodes.has(nodeId)) return 'done';
  return '';
}

export function LangGraphTopology({ activeNode, doneNodes }) {
  return (
    <div className="sec">
      <div className="sec-lbl">LangGraph Topology</div>
      <div className="lg-topology">
        {LANGGRAPH_NODES.map((node, idx) => (
          <React.Fragment key={node.id}>
            <div className={`lg-node ${getNodeStatus(node.id, activeNode, doneNodes)}`}>
              <div className="lg-node-dot"></div>
              <div className="lg-node-name">{node.label}</div>
              <div className="lg-node-badge">{node.badge}</div>
            </div>
            {idx < LANGGRAPH_NODES.length - 1 && (
              <div className="lg-edge">
                <div className="lg-edge-line"></div>
                <div className="lg-edge-txt">{LG_EDGES[idx]?.label || '→'}</div>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
