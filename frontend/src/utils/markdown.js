// Markdown to JSX utilities

export function formatInline(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code style="background:#f5f5f5;padding:2px 6px;border-radius:3px;font-family:monospace">$1</code>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" style="color:#c8722a;text-decoration:none">$1</a>');
}

export function renderMarkdown(text) {
  if (!text) return <p style={{ color: '#999' }}>No response</p>;

  const lines = text.split('\n');
  const out = [];
  let i = 0;

  while (i < lines.length) {
    const l = lines[i];

    // Skip empty lines
    if (!l.trim()) {
      i++;
      continue;
    }

    // Handle lists (ordered and unordered)
    if (l.match(/^[\-\*•]\s+/) || l.match(/^\d+\.\s+/)) {
      const items = [];
      while (
        i < lines.length &&
        (lines[i].match(/^[\-\*•]\s+/) || lines[i].match(/^\d+\.\s+/))
      ) {
        items.push(
          lines[i]
            .replace(/^[\-\*•]\s+/, '')
            .replace(/^\d+\.\s+/, '')
        );
        i++;
      }

      const Tag = lines[i - 1]?.match(/^\d+\./) ? 'ol' : 'ul';
      out.push(
        <Tag key={i} style={{ paddingLeft: 16, margin: '4px 0' }}>
          {items.map((x, j) => (
            <li
              key={j}
              dangerouslySetInnerHTML={{ __html: formatInline(x) }}
              style={{ marginBottom: 2 }}
            />
          ))}
        </Tag>
      );
      continue;
    }

    // Regular paragraphs
    out.push(
      <p
        key={i}
        dangerouslySetInnerHTML={{ __html: formatInline(l) }}
        style={{ marginBottom: 4 }}
      />
    );
    i++;
  }

  return out;
}
