import React, { useState, useRef, useEffect } from 'react';

export function InputArea({ onSendMessage, disabled }) {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
      if (inputRef.current) {
        inputRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e) => {
    setInput(e.target.value);
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 100) + 'px';
    }
  };

  return (
    <div className="input-wrapper">
      <div className="input-row">
        <textarea
          ref={inputRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask about grooming, availability, pricing..."
          disabled={disabled}
          rows={1}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          title="Send message (Enter)"
        >
          ↑
        </button>
      </div>
    </div>
  );
}
