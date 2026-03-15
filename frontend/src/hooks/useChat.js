import { useState, useCallback } from 'react';
import { sendChatMessage } from '../utils/api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionContext, setSessionContext] = useState({});
  const [activeNode, setActiveNode] = useState(null);
  const [doneNodes, setDoneNodes] = useState(new Set());
  const [doneServers, setDoneServers] = useState(new Set());

  const updateContext = useCallback((updates) => {
    setSessionContext(prev => ({ ...prev, ...updates }));
  }, []);

  const sendMessage = useCallback(async (content) => {
    if (!content.trim()) return;

    // Add user message
    const userMsg = { id: Date.now(), role: 'user', content, ts: new Date() };
    setMessages(prev => [...prev, userMsg]);

    setLoading(true);
    setActiveNode('agent');
    setDoneNodes(new Set());
    setDoneServers(new Set());

    try {
      const response = await sendChatMessage(
        [...messages, userMsg].map(m => ({ role: m.role, content: m.content })),
        sessionContext
      );

      // Update context from response
      if (response.contextUpdates) {
        updateContext(response.contextUpdates);
      }

      // Track tool execution
      if (response.toolCallLog) {
        response.toolCallLog.forEach(entry => {
          setDoneServers(prev => new Set([...prev, entry.server]));
        });
      }

      // Add assistant message
      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message || '',
        toolsUsed: response.toolsUsed || [],
        toolCallLog: response.toolCallLog || [],
        graphMeta: response.graphMeta || {},
        ts: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `⚠️ Error: ${err.message}`,
        ts: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      setActiveNode(null);
      setDoneNodes(prev => new Set([...prev, 'agent']));
    }
  }, [messages, sessionContext, updateContext]);

  return {
    messages,
    setMessages,
    loading,
    sendMessage,
    sessionContext,
    updateContext,
    activeNode,
    doneNodes,
    doneServers,
    setActiveNode,
    setDoneNodes,
    setDoneServers,
  };
}
