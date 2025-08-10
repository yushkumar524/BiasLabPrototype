from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import random
import uuid

# Import our models and mock data
from models import Article, Narrative, ArticleSummary, NarrativeSummary, BiasScores, TimePoint
from mock_data import (
    get_all_articles, 
    get_article_by_id, 
    get_all_narratives, 
    get_narrative_by_id,
    MOCK_ARTICLES,
    MOCK_NARRATIVES
)

# Initialize FastAPI app
app = FastAPI(
    title="Bias Labs API",
    description="API for media bias analysis and narrative clustering",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # React dev server + deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to ensure consistent ArticleSummary conversion
def article_to_summary(article: Article) -> ArticleSummary:
    """Convert Article to ArticleSummary ensuring data consistency"""
    return ArticleSummary(
        id=article.id,
        title=article.title,
        source=article.source,
        published_date=article.published_date,
        bias_scores=article.bias_scores,  # Use exact same bias_scores object
        narrative_id=article.narrative_id
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Bias Labs API",
        "version": "1.0.0",
        "data_stats": {
            "total_articles": len(MOCK_ARTICLES),
            "total_narratives": len(MOCK_NARRATIVES)
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Bias Labs API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "articles": "/articles",
            "narratives": "/narratives"
        }
    }

# Articles endpoints
@app.get("/articles", response_model=List[ArticleSummary])
async def get_articles(
    limit: int = Query(10, description="Maximum number of articles to return", ge=1, le=50),
    offset: int = Query(0, description="Number of articles to skip", ge=0),
    bias_threshold: Optional[float] = Query(None, description="Filter articles above this bias threshold", ge=0, le=100),
    narrative_id: Optional[str] = Query(None, description="Filter articles by narrative ID")
):
    """Get list of articles with basic information and bias scores"""
    articles = get_all_articles()
    
    # Apply filters
    if bias_threshold is not None:
        articles = [a for a in articles if a.bias_scores.overall >= bias_threshold]
    
    if narrative_id is not None:
        articles = [a for a in articles if a.narrative_id == narrative_id]
    
    # Sort by publication date (most recent first)
    articles = sorted(articles, key=lambda x: x.published_date, reverse=True)
    
    # Apply pagination
    paginated_articles = articles[offset:offset + limit]
    
    # Convert to ArticleSummary format using helper function
    article_summaries = [article_to_summary(article) for article in paginated_articles]
    
    return article_summaries

@app.get("/articles/{article_id}", response_model=Article)
async def get_article_detail(article_id: str):
    """Get detailed article with bias analysis and highlighted phrases"""
    article = get_article_by_id(article_id)
    
    if not article:
        raise HTTPException(status_code=404, detail=f"Article with ID {article_id} not found")
    
    return article

# Narratives endpoints
@app.get("/narratives", response_model=List[NarrativeSummary])
async def get_narratives():
    """Get list of narrative clusters with summary information"""
    narratives = get_all_narratives()
    
    # Sort by last updated (most recent first)
    narratives = sorted(narratives, key=lambda x: x.last_updated, reverse=True)
    
    # Convert to NarrativeSummary format
    narrative_summaries = [
        NarrativeSummary(
            id=narrative.id,
            title=narrative.title,
            description=narrative.description,
            article_count=narrative.article_count,
            avg_bias_scores=narrative.avg_bias_scores,
            last_updated=narrative.last_updated
        )
        for narrative in narratives
    ]
    
    return narrative_summaries

@app.get("/narratives/{narrative_id}", response_model=Narrative)
async def get_narrative_detail(narrative_id: str):
    """Get detailed narrative with all associated articles and bias evolution"""
    narrative = get_narrative_by_id(narrative_id)
    
    if not narrative:
        raise HTTPException(status_code=404, detail=f"Narrative with ID {narrative_id} not found")
    
    return narrative

@app.get("/narratives/{narrative_id}/timeline", response_model=List[TimePoint])
async def get_narrative_timeline(narrative_id: str):
    """Get bias evolution timeline for a specific narrative"""
    narrative = get_narrative_by_id(narrative_id)
    
    if not narrative:
        raise HTTPException(status_code=404, detail=f"Narrative with ID {narrative_id} not found")
    
    return narrative.bias_evolution

@app.get("/narratives/{narrative_id}/articles", response_model=List[ArticleSummary])
async def get_narrative_articles(narrative_id: str):
    """Get all articles belonging to a specific narrative"""
    narrative = get_narrative_by_id(narrative_id)
    
    if not narrative:
        raise HTTPException(status_code=404, detail=f"Narrative with ID {narrative_id} not found")
    
    # Get articles for this narrative - using get_article_by_id to ensure consistency
    narrative_articles = []
    for article_id in narrative.article_ids:
        article = get_article_by_id(article_id)
        if article:
            narrative_articles.append(article)
    
    # Sort by publication date
    narrative_articles = sorted(narrative_articles, key=lambda x: x.published_date, reverse=True)
    
    # Convert to ArticleSummary format using helper function
    article_summaries = [article_to_summary(article) for article in narrative_articles]
    
    return article_summaries

# Statistics endpoint for dashboard overview
@app.get("/stats")
async def get_statistics():
    """Get overall statistics about bias analysis data"""
    articles = get_all_articles()
    narratives = get_all_narratives()
    
    if not articles:
        return {"error": "No articles available"}
    
    # Calculate average bias scores across all articles for the 5 correct dimensions
    avg_overall_bias = sum(a.bias_scores.overall for a in articles) / len(articles)
    avg_ideological_stance = sum(a.bias_scores.ideological_stance for a in articles) / len(articles)
    avg_factual_grounding = sum(a.bias_scores.factual_grounding for a in articles) / len(articles)
    avg_framing_choices = sum(a.bias_scores.framing_choices for a in articles) / len(articles)
    avg_emotional_tone = sum(a.bias_scores.emotional_tone for a in articles) / len(articles)
    avg_source_transparency = sum(a.bias_scores.source_transparency for a in articles) / len(articles)
    
    # Source distribution
    source_counts = {}
    for article in articles:
        source_counts[article.source] = source_counts.get(article.source, 0) + 1
    
    return {
        "total_articles": len(articles),
        "total_narratives": len(narratives),
        "average_bias_scores": {
            "overall": round(avg_overall_bias, 1),
            "ideological_stance": round(avg_ideological_stance, 1),
            "factual_grounding": round(avg_factual_grounding, 1),
            "framing_choices": round(avg_framing_choices, 1),
            "emotional_tone": round(avg_emotional_tone, 1),
            "source_transparency": round(avg_source_transparency, 1)
        },
        "source_distribution": source_counts,
        "time_range": {
            "earliest_article": min(a.published_date for a in articles).isoformat(),
            "latest_article": max(a.published_date for a in articles).isoformat()
        }
    }

# Debug endpoint to check data consistency
@app.get("/debug/article/{article_id}")
async def debug_article_consistency(article_id: str):
    """Debug endpoint to check if article data is consistent across endpoints"""
    
    # Get article directly
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Find which narrative this article belongs to
    narrative = None
    for n in get_all_narratives():
        if article_id in n.article_ids:
            narrative = n
            break
    
    # Get article via narrative endpoint
    narrative_article_summary = None
    if narrative:
        narrative_articles = []
        for aid in narrative.article_ids:
            a = get_article_by_id(aid)
            if a and a.id == article_id:
                narrative_article_summary = article_to_summary(a)
                break
    
    return {
        "article_direct": {
            "id": article.id,
            "title": article.title,
            "bias_scores": article.bias_scores.dict()
        },
        "article_via_narrative": {
            "id": narrative_article_summary.id if narrative_article_summary else None,
            "title": narrative_article_summary.title if narrative_article_summary else None,
            "bias_scores": narrative_article_summary.bias_scores.dict() if narrative_article_summary else None
        },
        "scores_match": article.bias_scores.dict() == narrative_article_summary.bias_scores.dict() if narrative_article_summary else None,
        "narrative_id": narrative.id if narrative else None
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)