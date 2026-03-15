import React from 'react';
import { QUICK_PROMPTS } from '../constants/config';

export function QuickPrompts({ onSelectPrompt }) {
  return (
    <div className="sec">
      <div className="sec-lbl">Quick Prompts</div>
      {QUICK_PROMPTS.map((prompt, i) => (
        <button
          key={i}
          className="qp"
          onClick={() => onSelectPrompt(prompt)}
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}
