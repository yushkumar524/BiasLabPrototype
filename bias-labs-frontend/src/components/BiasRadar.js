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
    <div style={{ width: '100%', height: '420px' }}>
      {/* Radar Chart - taking up most of the space */}
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
      </div>
      
      {/* Fixed Legend - now properly centered */}
      <div style={{ 
        height: '120px', 
        padding: '1rem 0', 
        fontSize: '0.8rem', 
        color: '#666',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <p style={{ 
          textAlign: 'center', 
          marginBottom: '0.75rem', 
          fontWeight: '600',
          margin: '0 0 0.75rem 0'
        }}>
          Higher scores indicate more bias
        </p>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '1fr 1fr', 
          gap: '0.5rem 1rem',
          fontSize: '0.75rem',
          maxWidth: '100%',
          width: '100%',
          justifyItems: 'center'
        }}>
          <div>Ideological: {biasScores.ideological_stance > 0 ? 'Right' : biasScores.ideological_stance < 0 ? 'Left' : 'Center'}</div>
          <div>Factual Issues: {(100 - biasScores.factual_grounding).toFixed(0)}%</div>
          <div>Framing Bias: {biasScores.framing_choices.toFixed(0)}%</div>
          <div>Emotional Tone: {biasScores.emotional_tone.toFixed(0)}%</div>
          <div style={{ 
            gridColumn: 'span 2', 
            textAlign: 'center', 
            marginTop: '0.25rem',
            justifySelf: 'center'
          }}>
            Transparency Issues: {(100 - biasScores.source_transparency).toFixed(0)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default BiasRadar;