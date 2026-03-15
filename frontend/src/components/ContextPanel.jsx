import React from 'react';
import { CTX_LABELS } from '../constants/config';

export function ContextPanel({ sessionContext }) {
  const displayContext = Object.entries(sessionContext).filter(
    ([key]) => CTX_LABELS[key]
  );

  return (
    <div className="sec">
      <div className="sec-lbl">Session Context</div>
      <div className="ctx-block">
        {displayContext.length === 0 ? (
          <div className="ctx-empty">No context yet</div>
        ) : (
          displayContext.map(([key, value]) => (
            <div key={key} className="ctx-r">
              <div className="ctx-k">{CTX_LABELS[key]}</div>
              <div className="ctx-v">{String(value)}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
