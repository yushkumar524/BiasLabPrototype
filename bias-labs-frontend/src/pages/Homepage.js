import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, withErrorHandling } from '../services/api';

const Homepage = () => {
  const navigate = useNavigate();
  const [narratives, setNarratives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNarratives = async () => {
      try {
        setLoading(true);
        const data = await withErrorHandling(() => apiService.getNarratives());
        setNarratives(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchNarratives();
  }, []);

  const getBiasColor = (biasScore) => {
    if (biasScore < 30) return '#48bb78'; // Green for low bias
    if (biasScore < 60) return '#ed8936'; // Orange for medium bias
    return '#f56565'; // Red for high bias
  };

  const getBiasLabel = (biasScore) => {
    if (biasScore < 30) return 'Low Bias';
    if (biasScore < 60) return 'Medium Bias';
    return 'High Bias';
  };

  const getIdeologicalStanceLabel = (ideologicalStance) => {
    if (ideologicalStance >= 60) return 'Right';
    if (ideologicalStance >= 20) return 'Skews Right';
    if (ideologicalStance > -20) return 'Center';
    if (ideologicalStance > -60) return 'Skews Left';
    return 'Left';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="loading">Loading narrative clusters...</div>;
  }

  if (error) {
    return (
      <div className="error">
        Error loading narratives: {error}
        <br />
        <button 
          onClick={() => window.location.reload()} 
          className="btn btn-secondary"
          style={{ marginTop: '1rem' }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Media Bias Analysis</h1>
        <p className="page-subtitle">
          Explore how different news sources frame the same stories. 
          Click on any narrative cluster to see detailed bias analysis and article comparisons.
        </p>
      </div>

      {/* Narrative Clusters */}
      {narratives.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '3rem', 
          color: '#666',
          background: '#f8f9fa',
          borderRadius: '0.75rem'
        }}>
          <h3>No narratives available</h3>
          <p>Check back later for analysis of trending news stories.</p>
        </div>
      ) : (
        <>
          <h2 style={{ 
            fontSize: '1.5rem', 
            fontWeight: '600', 
            marginBottom: '1.5rem',
            color: '#2d3748'
          }}>
            Trending Narrative Clusters
          </h2>
          
          <div className="narrative-grid">
            {narratives.map((narrative) => (
              <div
                key={narrative.id}
                className="narrative-card"
                onClick={() => navigate(`/narrative/${narrative.id}`)}
              >
                <h3 className="narrative-title">{narrative.title}</h3>
                <p className="narrative-description">{narrative.description}</p>
                
                <div className="narrative-stats">
                  <div className="article-count">
                    {narrative.article_count} article{narrative.article_count !== 1 ? 's' : ''}
                  </div>
                  <div className="bias-indicator">
                    <span className="bias-score">
                      {getBiasLabel(narrative.avg_bias_scores.overall)}
                    </span>
                    <div className="bias-bar">
                      <div 
                        className="bias-fill"
                        style={{ 
                          width: `${narrative.avg_bias_scores.overall}%`,
                          backgroundColor: getBiasColor(narrative.avg_bias_scores.overall)
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Ideological stance indicator */}
                <div style={{ 
                  marginTop: '0.75rem', 
                  fontSize: '0.85rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  color: '#666'
                }}>
                  <span>
                    Ideological Lean: <strong>
                      {getIdeologicalStanceLabel(narrative.avg_bias_scores.ideological_stance)}
                    </strong>
                  </span>
                  <span>
                    Updated: {formatDate(narrative.last_updated)}
                  </span>
                </div>

                {/* Hover indicator */}
                <div style={{
                  marginTop: '0.75rem',
                  fontSize: '0.8rem',
                  color: '#667eea',
                  opacity: 0.8
                }}>
                  Click to explore →
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Info Section */}
      <div style={{
        marginTop: '3rem',
        padding: '2rem',
        background: 'white',
        borderRadius: '0.75rem',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
      }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600' }}>
          How It Works
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          <div>
            <h4 style={{ color: '#667eea', marginBottom: '0.5rem' }}>1. Story Clustering</h4>
            <p style={{ fontSize: '0.9rem', color: '#666', lineHeight: '1.5' }}>
              We group articles covering the same story from different news sources to identify narrative patterns.
            </p>
          </div>
          <div>
            <h4 style={{ color: '#667eea', marginBottom: '0.5rem' }}>2. Bias Analysis</h4>
            <p style={{ fontSize: '0.9rem', color: '#666', lineHeight: '1.5' }}>
              Each article is analyzed across 5 dimensions: ideological stance, factual grounding, framing choices, emotional tone, and source transparency.
            </p>
          </div>
          <div>
            <h4 style={{ color: '#667eea', marginBottom: '0.5rem' }}>3. Visual Comparison</h4>
            <p style={{ fontSize: '0.9rem', color: '#666', lineHeight: '1.5' }}>
              See how the same story is framed differently across sources with highlighted biased phrases and radar charts.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Homepage;