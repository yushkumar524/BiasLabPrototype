import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

const BiasRadar = ({ biasScores }) => {
  if (!biasScores) {
    return <div style={{ textAlign: 'center', color: '#666' }}>No bias data available</div>;
  }

  const data = [
    {
      dimension: 'Political\nLean',
      score: Math.abs(biasScores.political_lean),
      fullMark: 100,
    },
    {
      dimension: 'Emotional\nLanguage',
      score: biasScores.emotional_language,
      fullMark: 100,
    },
    {
      dimension: 'Source\nDiversity',
      score: 100 - biasScores.source_diversity, // Invert so high diversity = low bias
      fullMark: 100,
    },
    {
      dimension: 'Factual\nReporting',
      score: 100 - biasScores.factual_reporting, // Invert so high factual = low bias
      fullMark: 100,
    },
    {
      dimension: 'Overall\nBias',
      score: biasScores.overall,
      fullMark: 100,
    },
  ];

  return (
    <div style={{ width: '100%', height: '300px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis 
            tick={{ fontSize: 10, fill: '#4a5568' }} 
            className="radar-axis"
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 100]} 
            tick={{ fontSize: 8, fill: '#718096' }}
          />
          <Radar
            name="Bias Score"
            dataKey="score"
            stroke="#667eea"
            fill="#667eea"
            fillOpacity={0.2}
            strokeWidth={2}
            dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
          />
        </RadarChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#666' }}>
        <p style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
          <strong>Higher scores indicate more bias</strong>
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem' }}>
          <div>Political: {biasScores.political_lean > 0 ? 'Right' : biasScores.political_lean < 0 ? 'Left' : 'Center'}</div>
          <div>Emotional: {biasScores.emotional_language.toFixed(0)}%</div>
          <div>Source Issues: {(100 - biasScores.source_diversity).toFixed(0)}%</div>
          <div>Factual Issues: {(100 - biasScores.factual_reporting).toFixed(0)}%</div>
        </div>
      </div>
    </div>
  );
};

export default BiasRadar;