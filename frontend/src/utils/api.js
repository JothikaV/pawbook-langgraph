import { CHAT_ENDPOINT, STATUS_ENDPOINT, HEALTH_ENDPOINT } from '../constants/config';

export async function sendChatMessage(messages, sessionContext) {
  try {
    const response = await fetch(CHAT_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, sessionContext }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to send message: ${error.message}`);
  }
}

export async function getStatus() {
  try {
    const response = await fetch(STATUS_ENDPOINT);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Status check failed:', error);
    return null;
  }
}

export async function getHealth() {
  try {
    const response = await fetch(HEALTH_ENDPOINT);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    return null;
  }
}
