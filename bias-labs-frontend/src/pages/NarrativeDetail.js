import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiService, withErrorHandling } from '../services/api';
import BiasRadar from '../components/BiasRadar';
import BiasTimeline from '../components/BiasTimeline';

const NarrativeDetail = () => {
  const { narrativeId } = useParams();
  const navigate = useNavigate();
  const [narrative, setNarrative] = useState(null);
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNarrativeData = async () => {
      try {
        setLoading(true);
        const [narrativeData, articlesData] = await Promise.all([
          withErrorHandling(() => apiService.getNarrativeDetail(narrativeId)),
          withErrorHandling(() => apiService.getNarrativeArticles(narrativeId))
        ]);
        setNarrative(narrativeData);
        setArticles(articlesData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchNarrativeData();
  }, [narrativeId]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSourceColor = (source) => {
    const colors = {
      'CNN': '#cc0000',
      'Fox News': '#0066cc',
      'Reuters': '#ff6600',
      'BBC': '#bb1919',
      'Wall Street Journal': '#0274be',
      'The Guardian': '#052962',
      'Associated Press': '#0084c6',
      'New York Times': '#000000'
    };
    return colors[source] || '#666666';
  };

  if (loading) {
    return <div className="loading">Loading narrative details...</div>;
  }

  if (error) {
    return (
      <div>
        <div className="error">Error: {error}</div>
        <Link to="/" className="btn btn-secondary">← Back to Home</Link>
      </div>
    );
  }

  if (!narrative) {
    return (
      <div>
        <div className="error">Narrative not found</div>
        <Link to="/" className="btn btn-secondary">← Back to Home</Link>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <Link to="/" className="btn btn-secondary" style={{ marginBottom: '1rem' }}>
          ← Back to Narratives
        </Link>
        <h1 className="page-title">{narrative.title}</h1>
        <p className="page-subtitle">{narrative.description}</p>
        <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
          <strong>{narrative.dominant_framing}</strong> • {articles.length} articles • 
          Last updated {formatDate(narrative.last_updated)}
        </div>
      </div>

      {/* Bias Analysis Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '3rem' }}>
        <div>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem', fontWeight: '600' }}>
            Average Bias Analysis
          </h2>
          <BiasRadar biasScores={narrative.avg_bias_scores} />
        </div>
        <div>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem', fontWeight: '600' }}>
            Bias Evolution Over Time
          </h2>
          {narrative.bias_evolution && narrative.bias_evolution.length > 0 ? (
            <BiasTimeline timelineData={narrative.bias_evolution} />
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#666', background: '#f8f9fa', borderRadius: '0.5rem' }}>
              Not enough data points for timeline
            </div>
          )}
        </div>
      </div>

      {/* Articles Section */}
      <div>
        <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: '600' }}>
          Articles in This Narrative
        </h2>
        <div className="article-grid">
          {articles.map((article) => (
            <div
              key={article.id}
              className="article-card"
              onClick={() => navigate(`/article/${article.id}`)}
              style={{ borderLeftColor: getSourceColor(article.source) }}
            >
              <div className="article-header">
                <h3 className="article-title">{article.title}</h3>
                <div
                  className="article-source"
                  style={{
                    backgroundColor: getSourceColor(article.source),
                    color: 'white'
                  }}
                >
                  {article.source}
                </div>
              </div>
              <div className="article-date">
                {formatDate(article.published_date)}
              </div>
              <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem' }}>
                <span>Overall Bias: <strong>{article.bias_scores.overall.toFixed(1)}%</strong></span>
                <span>Political Lean: <strong>{article.bias_scores.political_lean > 0 ? 'Right' : article.bias_scores.political_lean < 0 ? 'Left' : 'Center'} ({Math.abs(article.bias_scores.political_lean).toFixed(0)})</strong></span>
                <span>Factual: <strong>{article.bias_scores.factual_reporting.toFixed(0)}%</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NarrativeDetail;