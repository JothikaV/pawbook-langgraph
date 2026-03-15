import React from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { useChat } from './hooks/useChat';
import { useSystemStatus } from './hooks/useSystemStatus';
import { GLOBAL_STYLES } from './styles/globals';

// Import all CSS files
import './styles/sidebar.css';
import './styles/chat.css';
import './styles/components.css';
import './styles/animations.css';

function App() {
  const {
    messages,
    loading,
    sendMessage,
    sessionContext,
    activeNode,
    doneNodes,
    doneServers,
  } = useChat();

  const { status } = useSystemStatus();

  const handleSelectPrompt = (prompt) => {
    sendMessage(prompt);
  };

  const handleSelectChip = (chip) => {
    sendMessage(chip);
  };

  return (
    <>
      <style>{GLOBAL_STYLES}</style>
      <div className="app">
        <Sidebar
          activeNode={activeNode}
          doneNodes={doneNodes}
          doneServers={doneServers}
          status={status}
          sessionContext={sessionContext}
          onSelectPrompt={handleSelectPrompt}
        />
        <ChatArea
          messages={messages}
          loading={loading}
          onSendMessage={sendMessage}
          onSelectChip={handleSelectChip}
          status={status}
          activeNode={activeNode}
        />
      </div>
    </>
  );
}

export default App;
