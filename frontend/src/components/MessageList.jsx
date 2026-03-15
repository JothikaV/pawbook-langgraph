import React, { useEffect, useRef } from 'react';
import { Message } from './Message';
import { Welcome } from './Welcome';

export function MessageList({ messages, loading, onSelectChip, activeNode }) {
  const msgsRef = useRef(null);

  useEffect(() => {
    if (msgsRef.current) {
      msgsRef.current.scrollTop = msgsRef.current.scrollHeight;
    }
  }, [messages, loading]);

  return (
    <div className="msgs" ref={msgsRef}>
      {messages.length === 0 ? (
        <Welcome onSelectChip={onSelectChip} />
      ) : (
        messages.map(msg => <Message key={msg.id} message={msg} />)
      )}
      {loading && (
        <div className="mg assistant">
          <div className="av">🐾</div>
          <div className="ni">
            <div className="ni-spin" />
            <div className="ni-txt">
              {activeNode ? `Processing on ${activeNode}...` : 'Thinking...'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
