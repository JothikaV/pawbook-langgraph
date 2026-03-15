import React from 'react';
import { ChatHeader } from './ChatHeader';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';

export function ChatArea({
  messages,
  loading,
  onSendMessage,
  onSelectChip,
  status,
  activeNode,
}) {
  return (
    <div className="chat">
      <ChatHeader status={status} />
      <MessageList
        messages={messages}
        loading={loading}
        onSelectChip={onSelectChip}
        activeNode={activeNode}
      />
      <InputArea onSendMessage={onSendMessage} disabled={loading} />
    </div>
  );
}
