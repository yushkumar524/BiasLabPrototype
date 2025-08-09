import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BiasTimeline = ({ timelineData }) => {
  if (!timelineData || timelineData.length === 0) {
    return <div style={{ textAlign: 'center', color: '#666' }}>No timeline data available</div>;
  }

  // Format data for the chart with all 5 dimensions
  const chartData = timelineData.map((point, index) => ({
    time: new Date(point.timestamp).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit'
    }),
    timestamp: point.timestamp,
    overallBias: point.bias_scores.overall,
    ideologicalStance: Math.abs(point.bias_scores.ideological_stance),
    factualGrounding: 100 - point.bias_scores.factual_grounding, // Invert for consistency
    framingChoices: point.bias_scores.framing_choices,
    emotionalTone: point.bias_scores.emotional_tone, // Now included in chart
    sourceTransparency: 100 - point.bias_scores.source_transparency, // Invert for consistency
    articleCount: point.article_count,
    index: index
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '0.75rem',
          border: '1px solid #e2e8f0',
          borderRadius: '0.5rem',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          fontSize: '0.85rem'
        }}>
          <p style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{label}</p>
          <p style={{ color: '#ff6b6b', margin: '0.25rem 0' }}>
            Ideological Stance: {data.ideologicalStance.toFixed(1)}%
          </p>
          <p style={{ color: '#48dbfb', margin: '0.25rem 0' }}>
            Factual Grounding: {data.factualGrounding.toFixed(1)}%
          </p>
          <p style={{ color: '#feca57', margin: '0.25rem 0' }}>
            Framing Choices: {data.framingChoices.toFixed(1)}%
          </p>
          <p style={{ color: '#ff9ff3', margin: '0.25rem 0' }}>
            Emotional Tone: {data.emotionalTone.toFixed(1)}%
          </p>
          <p style={{ color: '#54a0ff', margin: '0.25rem 0' }}>
            Source Transparency: {data.sourceTransparency.toFixed(1)}%
          </p>
          <p style={{ color: '#666', margin: '0.25rem 0', fontSize: '0.8rem' }}>
            Articles: {data.articleCount}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height: '300px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 10 }}
            stroke="#718096"
          />
          <YAxis 
            domain={[0, 100]}
            tick={{ fontSize: 10 }}
            stroke="#718096"
            label={{ value: 'Bias Score (%)', angle: -90, position: 'insideLeft', style: { fontSize: '12px' } }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontSize: '12px' }}
          />
          <Line
            type="monotone"
            dataKey="ideologicalStance"
            stroke="#ff6b6b"
            strokeWidth={3}
            dot={{ fill: '#ff6b6b', strokeWidth: 2, r: 4 }}
            name="Ideological Stance"
          />
          <Line
            type="monotone"
            dataKey="factualGrounding"
            stroke="#48dbfb"
            strokeWidth={2}
            dot={{ fill: '#48dbfb', strokeWidth: 1, r: 3 }}
            name="Factual Grounding"
          />
          <Line
            type="monotone"
            dataKey="framingChoices"
            stroke="#feca57"
            strokeWidth={2}
            dot={{ fill: '#feca57', strokeWidth: 1, r: 3 }}
            name="Framing Choices"
          />
          <Line
            type="monotone"
            dataKey="emotionalTone"
            stroke="#ff9ff3"
            strokeWidth={2}
            dot={{ fill: '#ff9ff3', strokeWidth: 1, r: 3 }}
            name="Emotional Tone"
          />
          <Line
            type="monotone"
            dataKey="sourceTransparency"
            stroke="#54a0ff"
            strokeWidth={2}
            dot={{ fill: '#54a0ff', strokeWidth: 1, r: 3 }}
            name="Source Transparency"
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#666', textAlign: 'center' }}>
        Bias evolution over {chartData.length} article{chartData.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
};

export default BiasTimeline;