import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiService, withErrorHandling } from '../services/api';
import BiasRadar from '../components/BiasRadar';
import HighlightedText from '../components/HighlightedText';

const ArticleDetail = () => {
  const { articleId } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        setLoading(true);
        const data = await withErrorHandling(() => apiService.getArticleDetail(articleId));
        setArticle(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [articleId]);

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
    return <div className="loading">Loading article...</div>;
  }

  if (error) {
    return (
      <div>
        <div className="error">Error: {error}</div>
        <Link to="/" className="btn btn-secondary">← Back to Home</Link>
      </div>
    );
  }

  if (!article) {
    return (
      <div>
        <div className="error">Article not found</div>
        <Link to="/" className="btn btn-secondary">← Back to Home</Link>
      </div>
    );
  }

  return (
    <div>
      {/* Navigation */}
      <div style={{ marginBottom: '2rem', display: 'flex', gap: '1rem' }}>
        <Link to="/" className="btn btn-secondary">← Home</Link>
        {article.narrative_id && (
          <Link to={`/narrative/${article.narrative_id}`} className="btn btn-secondary">
            View Narrative
          </Link>
        )}
      </div>

      {/* Article Header */}
      <div className="page-header">
        <div
          style={{
            display: 'inline-block',
            padding: '0.5rem 1rem',
            borderRadius: '0.5rem',
            backgroundColor: getSourceColor(article.source),
            color: 'white',
            fontSize: '0.9rem',
            fontWeight: '600',
            marginBottom: '1rem'
          }}
        >
          {article.source}
        </div>
        <h1 className="page-title" style={{ textAlign: 'left', marginBottom: '0.5rem' }}>
          {article.title}
        </h1>
        <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
          {article.author && <span>By {article.author} • </span>}
          {formatDate(article.published_date)}
        </div>
        <a 
          href={article.url} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="btn btn-primary"
          style={{ marginBottom: '2rem' }}
        >
          Read Original Article →
        </a>
      </div>

      {/* Content and Analysis */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '3rem', alignItems: 'start' }}>
        {/* Article Content */}
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem' }}>
            Article Content with Bias Highlighting
          </h2>
          <div style={{ 
            background: 'white', 
            padding: '2rem', 
            borderRadius: '0.75rem', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            lineHeight: '1.8',
            fontSize: '1.05rem'
          }}>
            <HighlightedText 
              content={article.content} 
              highlights={article.highlighted_phrases}
            />
          </div>

          {/* Bias Legend */}
          {article.highlighted_phrases && article.highlighted_phrases.length > 0 && (
            <div style={{ 
              marginTop: '1.5rem', 
              padding: '1rem', 
              background: '#f8f9fa', 
              borderRadius: '0.5rem' 
            }}>
              <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>
                Highlighted Bias Types:
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ width: '12px', height: '12px', backgroundColor: '#ff6b6b', borderRadius: '2px' }}></div>
                  Ideological Stance
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ width: '12px', height: '12px', backgroundColor: '#48dbfb', borderRadius: '2px' }}></div>
                  Factual Grounding
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ width: '12px', height: '12px', backgroundColor: '#feca57', borderRadius: '2px' }}></div>
                  Framing Choices
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ width: '12px', height: '12px', backgroundColor: '#ff9ff3', borderRadius: '2px' }}></div>
                  Emotional Tone
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ width: '12px', height: '12px', backgroundColor: '#54a0ff', borderRadius: '2px' }}></div>
                  Source Transparency
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Bias Analysis Sidebar */}
        <div style={{ position: 'sticky', top: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem' }}>
            Bias Analysis
          </h2>
          <div style={{ 
            background: 'white', 
            padding: '1.5rem', 
            borderRadius: '0.75rem', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)' 
          }}>
            <BiasRadar biasScores={article.bias_scores} />
            
            {/* Bias Summary with controlled spacing */}
            <div style={{ 
              marginTop: '1rem', // Reduced margin since BiasRadar now controls its own spacing
              padding: '1rem',
              backgroundColor: '#f8f9fa',
              borderRadius: '0.5rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '1.1rem', fontWeight: '600', color: '#2d3748' }}>
                Overall Bias Score: {article.bias_scores.overall.toFixed(1)}%
              </div>
              <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
                See radar chart above for detailed breakdown
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleDetail;