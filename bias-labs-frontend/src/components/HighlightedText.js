import React from 'react';

// Consistent color scheme for bias highlighting across the project
const BIAS_COLORS = {
  "ideological_stance": "#ff6b6b",      // Red for ideological bias
  "factual_grounding": "#48dbfb",       // Blue for factual issues  
  "framing_choices": "#feca57",         // Orange for framing bias
  "emotional_tone": "#ff9ff3",          // Pink for emotional language
  "source_transparency": "#54a0ff"      // Purple for source transparency issues
};

const HighlightedText = ({ content, highlights = [] }) => {
  if (!content) {
    return <div style={{ color: '#666' }}>No content available</div>;
  }

  if (!highlights || highlights.length === 0) {
    return <div>{content}</div>;
  }

  // Bias type labels for tooltips
  const biasTypeLabels = {
    'ideological_stance': 'Ideological Stance',
    'factual_grounding': 'Factual Grounding',
    'framing_choices': 'Framing Choices',
    'emotional_tone': 'Emotional Tone',
    'source_transparency': 'Source Transparency'
  };

  // Sort highlights by start position to process them in order
  const sortedHighlights = [...highlights].sort((a, b) => a.start_pos - b.start_pos);

  // Build the highlighted text
  let result = [];
  let lastPos = 0;

  sortedHighlights.forEach((highlight, index) => {
    const { start_pos, end_pos, text, bias_type, confidence } = highlight;
    
    // Use consistent color from our palette, fallback to original color if needed
    const color = BIAS_COLORS[bias_type] || highlight.color || '#cccccc';

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
        title={`${biasTypeLabels[bias_type] || bias_type} bias (${Math.round(confidence * 100)}% confidence)`}
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