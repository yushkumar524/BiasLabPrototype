import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BiasTimeline = ({ timelineData }) => {
  if (!timelineData || timelineData.length === 0) {
    return <div style={{ textAlign: 'center', color: '#666' }}>No timeline data available</div>;
  }

  // Format data for the chart
  const chartData = timelineData.map((point, index) => ({
    time: new Date(point.timestamp).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit'
    }),
    timestamp: point.timestamp,
    overallBias: point.bias_scores.overall,
    politicalLean: Math.abs(point.bias_scores.political_lean),
    emotionalLanguage: point.bias_scores.emotional_language,
    factualReporting: 100 - point.bias_scores.factual_reporting, // Invert for consistency
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
          <p style={{ color: '#667eea', margin: '0.25rem 0' }}>
            Overall Bias: {data.overallBias.toFixed(1)}%
          </p>
          <p style={{ color: '#f56565', margin: '0.25rem 0' }}>
            Political Bias: {data.politicalLean.toFixed(1)}%
          </p>
          <p style={{ color: '#ed8936', margin: '0.25rem 0' }}>
            Emotional Language: {data.emotionalLanguage.toFixed(1)}%
          </p>
          <p style={{ color: '#38b2ac', margin: '0.25rem 0' }}>
            Factual Issues: {data.factualReporting.toFixed(1)}%
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
            dataKey="overallBias"
            stroke="#667eea"
            strokeWidth={3}
            dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
            name="Overall Bias"
          />
          <Line
            type="monotone"
            dataKey="politicalLean"
            stroke="#f56565"
            strokeWidth={2}
            dot={{ fill: '#f56565', strokeWidth: 1, r: 3 }}
            name="Political Bias"
          />
          <Line
            type="monotone"
            dataKey="emotionalLanguage"
            stroke="#ed8936"
            strokeWidth={2}
            dot={{ fill: '#ed8936', strokeWidth: 1, r: 3 }}
            name="Emotional Language"
          />
          <Line
            type="monotone"
            dataKey="factualReporting"
            stroke="#38b2ac"
            strokeWidth={2}
            dot={{ fill: '#38b2ac', strokeWidth: 1, r: 3 }}
            name="Factual Issues"
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