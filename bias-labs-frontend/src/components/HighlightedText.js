import React from 'react';

const HighlightedText = ({ content, highlights = [] }) => {
  if (!content) {
    return <div style={{ color: '#666' }}>No content available</div>;
  }

  if (!highlights || highlights.length === 0) {
    return <div>{content}</div>;
  }

  // Sort highlights by start position to process them in order
  const sortedHighlights = [...highlights].sort((a, b) => a.start_pos - b.start_pos);

  // Build the highlighted text
  let result = [];
  let lastPos = 0;

  sortedHighlights.forEach((highlight, index) => {
    const { start_pos, end_pos, text, bias_type, confidence, color } = highlight;

    // Add text before this highlight
    if (start_pos > lastPos) {
      result.push(
        <span key={`text-${index}`}>
          {content.substring(lastPos, start_pos)}
        </span>
      );
    }

    // Add the highlighted text
    result.push(
      <span
        key={`highlight-${index}`}
        style={{
          backgroundColor: color,
          padding: '2px 4px',
          borderRadius: '3px',
          color: '#000',
          fontWeight: '500',
          cursor: 'help',
          position: 'relative'
        }}
        title={`${bias_type.replace('_', ' ')} bias (${Math.round(confidence * 100)}% confidence)`}
      >
        {text}
      </span>
    );

    lastPos = end_pos;
  });

  // Add remaining text
  if (lastPos < content.length) {
    result.push(
      <span key="text-final">
        {content.substring(lastPos)}
      </span>
    );
  }

  return <div>{result}</div>;
};

export default HighlightedText;