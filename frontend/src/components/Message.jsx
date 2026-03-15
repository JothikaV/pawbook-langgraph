import React from 'react';
import { renderMarkdown } from '../utils/markdown';
import { ToolBadges } from './ToolBadges';

export function Message({ message }) {
  const isAssistant = message.role === 'assistant';

  return (
    <div key={message.id} className={`mg ${message.role}`}>
      <div className="av">{isAssistant ? '🐾' : 'U'}</div>
      <div className="bub">
        {renderMarkdown(message.content)}
        {message.toolsUsed && message.toolsUsed.length > 0 && (
          <ToolBadges toolsUsed={message.toolsUsed} />
        )}
      </div>
    </div>
  );
}
