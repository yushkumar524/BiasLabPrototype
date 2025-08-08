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
    
    # Convert to ArticleSummary format
    article_summaries = [
        ArticleSummary(
            id=article.id,
            title=article.title,
            source=article.source,
            published_date=article.published_date,
            bias_scores=article.bias_scores,
            narrative_id=article.narrative_id
        )
        for article in paginated_articles
    ]
    
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
    
    # Get articles for this narrative
    narrative_articles = [
        article for article in get_all_articles() 
        if article.id in narrative.article_ids
    ]
    
    # Sort by publication date
    narrative_articles = sorted(narrative_articles, key=lambda x: x.published_date, reverse=True)
    
    # Convert to ArticleSummary format
    article_summaries = [
        ArticleSummary(
            id=article.id,
            title=article.title,
            source=article.source,
            published_date=article.published_date,
            bias_scores=article.bias_scores,
            narrative_id=article.narrative_id
        )
        for article in narrative_articles
    ]
    
    return article_summaries

# Statistics endpoint for dashboard overview
@app.get("/stats")
async def get_statistics():
    """Get overall statistics about bias analysis data"""
    articles = get_all_articles()
    narratives = get_all_narratives()
    
    if not articles:
        return {"error": "No articles available"}
    
    # Calculate average bias scores across all articles
    avg_overall_bias = sum(a.bias_scores.overall for a in articles) / len(articles)
    avg_political_lean = sum(a.bias_scores.political_lean for a in articles) / len(articles)
    avg_emotional_language = sum(a.bias_scores.emotional_language for a in articles) / len(articles)
    avg_factual_reporting = sum(a.bias_scores.factual_reporting for a in articles) / len(articles)
    
    # Source distribution
    source_counts = {}
    for article in articles:
        source_counts[article.source] = source_counts.get(article.source, 0) + 1
    
    return {
        "total_articles": len(articles),
        "total_narratives": len(narratives),
        "average_bias_scores": {
            "overall": round(avg_overall_bias, 1),
            "political_lean": round(avg_political_lean, 1),
            "emotional_language": round(avg_emotional_language, 1),
            "factual_reporting": round(avg_factual_reporting, 1)
        },
        "source_distribution": source_counts,
        "time_range": {
            "earliest_article": min(a.published_date for a in articles).isoformat(),
            "latest_article": max(a.published_date for a in articles).isoformat()
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)