import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

const BiasRadar = ({ biasScores }) => {
  if (!biasScores) {
    return <div style={{ textAlign: 'center', color: '#666' }}>No bias data available</div>;
  }

  const data = [
    {
      dimension: 'Ideological\nStance',
      score: Math.abs(biasScores.ideological_stance),
      fullMark: 100,
    },
    {
      dimension: 'Factual\nGrounding',
      score: 100 - biasScores.factual_grounding, // Invert so high factual = low bias
      fullMark: 100,
    },
    {
      dimension: 'Framing\nChoices',
      score: biasScores.framing_choices,
      fullMark: 100,
    },
    {
      dimension: 'Emotional\nTone',
      score: biasScores.emotional_tone,
      fullMark: 100,
    },
    {
      dimension: 'Source\nTransparency',
      score: 100 - biasScores.source_transparency, // Invert so high transparency = low bias
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
          <div>Ideological: {biasScores.ideological_stance > 0 ? 'Right' : biasScores.ideological_stance < 0 ? 'Left' : 'Center'}</div>
          <div>Factual Issues: {(100 - biasScores.factual_grounding).toFixed(0)}%</div>
          <div>Framing Bias: {biasScores.framing_choices.toFixed(0)}%</div>
          <div>Emotional Tone: {biasScores.emotional_tone.toFixed(0)}%</div>
          <div>Transparency Issues: {(100 - biasScores.source_transparency).toFixed(0)}%</div>
        </div>
      </div>
    </div>
  );
};

export default BiasRadar;