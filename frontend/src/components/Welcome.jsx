import React from 'react';
import { WELCOME_CHIPS } from '../constants/config';

export function Welcome({ onSelectChip }) {
  return (
    <div className="welcome">
      <div className="w-icon">🐾</div>
      <div className="w-title">Welcome to PawBook</div>
      <div className="w-sub">
        Python LangGraph orchestrates Groq LLM through LangChain tools, each backed by a real MCP server.
      </div>
      <div className="w-chips">
        {WELCOME_CHIPS.map((chip, i) => (
          <button
            key={i}
            className="wc"
            onClick={() => onSelectChip(chip.replace(/^[^\s]+\s/, ''))}
          >
            {chip}
          </button>
        ))}
      </div>
    </div>
  );
}
