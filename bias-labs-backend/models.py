from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class BiasScores(BaseModel):
    overall: float = Field(..., ge=0, le=100, description="Overall bias score 0-100")
    political_lean: float = Field(..., ge=-100, le=100, description="Political lean -100 (left) to 100 (right)")
    emotional_language: float = Field(..., ge=0, le=100, description="Emotional/sensational language score")
    source_diversity: float = Field(..., ge=0, le=100, description="Source diversity and fact-checking score")
    factual_reporting: float = Field(..., ge=0, le=100, description="Factual accuracy score")

class HighlightedPhrase(BaseModel):
    text: str = Field(..., description="The biased phrase")
    start_pos: int = Field(..., description="Starting position in text")
    end_pos: int = Field(..., description="Ending position in text")
    bias_type: str = Field(..., description="Type of bias (political_lean, emotional_language, etc.)")
    confidence: float = Field(..., ge=0, le=1, description="AI confidence in bias detection")
    color: str = Field(..., description="Hex color for highlighting")

class Article(BaseModel):
    id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article headline")
    content: str = Field(..., description="Article body text")
    source: str = Field(..., description="News source (CNN, Fox News, etc.)")
    author: Optional[str] = Field(None, description="Article author")
    published_date: datetime = Field(..., description="Publication timestamp")
    url: str = Field(..., description="Original article URL")
    bias_scores: BiasScores = Field(..., description="Bias analysis scores")
    highlighted_phrases: List[HighlightedPhrase] = Field(default=[], description="Biased phrases with highlights")
    narrative_id: Optional[str] = Field(None, description="Associated narrative cluster ID")

class ArticleSummary(BaseModel):
    """Lightweight version for article lists"""
    id: str
    title: str
    source: str
    published_date: datetime
    bias_scores: BiasScores
    narrative_id: Optional[str] = None

class TimePoint(BaseModel):
    timestamp: datetime = Field(..., description="Point in time")
    bias_scores: BiasScores = Field(..., description="Bias scores at this time")
    article_count: int = Field(..., description="Number of articles at this point")

class Narrative(BaseModel):
    id: str = Field(..., description="Unique narrative identifier")
    title: str = Field(..., description="Narrative title")
    description: str = Field(..., description="Brief description of the story framing")
    article_ids: List[str] = Field(..., description="Articles belonging to this narrative")
    dominant_framing: str = Field(..., description="Main way this story is being told")
    article_count: int = Field(..., description="Total articles in this narrative")
    avg_bias_scores: BiasScores = Field(..., description="Average bias across all articles")
    created_date: datetime = Field(..., description="When this narrative cluster was identified")
    last_updated: datetime = Field(..., description="Most recent article added")
    bias_evolution: List[TimePoint] = Field(default=[], description="How bias changed over time")

class NarrativeSummary(BaseModel):
    """Lightweight version for narrative lists"""
    id: str
    title: str
    description: str
    article_count: int
    avg_bias_scores: BiasScores
    last_updated: datetime