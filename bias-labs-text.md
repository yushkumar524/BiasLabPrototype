Project Tree:
```
├── .gitignore
├── bias-labs-backend/
│   ├── main.py
│   ├── mock_data.py
│   ├── models.py
│   └── requirements.txt
└── bias-labs-frontend/
    ├── .gitignore
    ├── README.md
    └── src/
        ├── App.css
        ├── App.js
        ├── App.test.js
        ├── components/
        │   ├── BiasRadar.js
        │   ├── BiasTimeline.js
        │   ├── Header.js
        │   └── HighlightedText.js
        ├── index.css
        ├── index.js
        ├── logo.svg
        ├── pages/
        │   ├── ArticleDetail.js
        │   ├── Homepage.js
        │   └── NarrativeDetail.js
        ├── reportWebVitals.js
        ├── services/
        │   └── api.js
        └── setupTests.js
```

# File: .gitignore
```text
# =========================
# Node / React
# =========================
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
package-lock.json
yarn.lock
.pnpm-debug.log

# Production build
build/
dist/

# Local environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# =========================
# Python / FastAPI
# =========================
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environment
venv/
ENV/
env/
.venv/

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
pytest_cache/
coverage.xml
*.cover
*.py,cover
.hypothesis/

# =========================
# OS / Editor files
# =========================
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp

# txt file for LLM prompting
bias-labs-text.md
```
# End of file: .gitignore

# File: bias-labs-backend/main.py
```python
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
```
# End of file: bias-labs-backend/main.py

# File: bias-labs-backend/mock_data.py
```python
from models import Article, BiasScores, HighlightedPhrase, Narrative, TimePoint, ArticleSummary, NarrativeSummary
from datetime import datetime, timedelta
import random
import uuid

# Color scheme for bias highlighting
BIAS_COLORS = {
    "ideological_stance": "#ff6b6b",      # Red for ideological bias
    "factual_grounding": "#48dbfb",       # Blue for factual issues
    "framing_choices": "#feca57",         # Orange for framing bias
    "emotional_tone": "#ff9ff3",          # Pink for emotional language
    "source_transparency": "#54a0ff"      # Purple for source transparency issues
}

# Sample news sources with typical bias patterns
NEWS_SOURCES = {
    "CNN": {"ideological_stance": -25, "factual_grounding": 75, "emotional_tone": 35, "framing_choices": 40, "source_transparency": 70},
    "Fox News": {"ideological_stance": 45, "factual_grounding": 65, "emotional_tone": 55, "framing_choices": 50, "source_transparency": 60},
    "Reuters": {"ideological_stance": 5, "factual_grounding": 90, "emotional_tone": 15, "framing_choices": 20, "source_transparency": 85},
    "BBC": {"ideological_stance": -10, "factual_grounding": 85, "emotional_tone": 20, "framing_choices": 25, "source_transparency": 80},
    "Wall Street Journal": {"ideological_stance": 20, "factual_grounding": 80, "emotional_tone": 25, "framing_choices": 30, "source_transparency": 75},
    "The Guardian": {"ideological_stance": -35, "factual_grounding": 70, "emotional_tone": 40, "framing_choices": 45, "source_transparency": 65},
    "Associated Press": {"ideological_stance": 0, "factual_grounding": 95, "emotional_tone": 10, "framing_choices": 15, "source_transparency": 90},
    "New York Times": {"ideological_stance": -20, "factual_grounding": 80, "emotional_tone": 30, "framing_choices": 35, "source_transparency": 75}
}

def create_bias_scores(source: str, topic_modifier: dict = None) -> BiasScores:
    """Create realistic bias scores based on source and topic"""
    base = NEWS_SOURCES.get(source, {"ideological_stance": 0, "factual_grounding": 75, "emotional_tone": 30, "framing_choices": 35, "source_transparency": 70})
    
    # Add some randomness
    ideological_stance = base["ideological_stance"] + random.randint(-10, 10)
    factual_grounding = max(0, min(100, base["factual_grounding"] + random.randint(-15, 15)))
    emotional_tone = max(0, min(100, base["emotional_tone"] + random.randint(-10, 20)))
    framing_choices = max(0, min(100, base["framing_choices"] + random.randint(-10, 15)))
    source_transparency = max(0, min(100, base["source_transparency"] + random.randint(-10, 15)))
    
    # Apply topic modifiers if provided
    if topic_modifier:
        ideological_stance += topic_modifier.get("ideological_stance", 0)
        emotional_tone += topic_modifier.get("emotional_tone", 0)
        factual_grounding += topic_modifier.get("factual_grounding", 0)
        framing_choices += topic_modifier.get("framing_choices", 0)
        source_transparency += topic_modifier.get("source_transparency", 0)
    
    # Clamp values
    ideological_stance = max(-100, min(100, ideological_stance))
    emotional_tone = max(0, min(100, emotional_tone))
    factual_grounding = max(0, min(100, factual_grounding))
    framing_choices = max(0, min(100, framing_choices))
    source_transparency = max(0, min(100, source_transparency))
    
    # Calculate overall bias score
    overall = (abs(ideological_stance) + emotional_tone + (100 - factual_grounding) + framing_choices + (100 - source_transparency)) / 5
    
    return BiasScores(
        overall=round(overall, 1),
        ideological_stance=round(ideological_stance, 1),
        factual_grounding=round(factual_grounding, 1),
        framing_choices=round(framing_choices, 1),
        emotional_tone=round(emotional_tone, 1),
        source_transparency=round(source_transparency, 1)
    )

def create_highlighted_phrases(content: str, bias_scores: BiasScores) -> list[HighlightedPhrase]:
    """Generate realistic highlighted phrases based on content and bias"""
    phrases = []
    
    # Ideological stance phrases
    ideological_phrases = [
        ("devastating blow", "ideological_stance"),
        ("radical agenda", "ideological_stance"),
        ("common-sense solution", "ideological_stance"),
        ("extreme measures", "ideological_stance"),
        ("failed policies", "ideological_stance")
    ]
    
    # Emotional tone phrases
    emotional_phrases = [
        ("shocking revelation", "emotional_tone"),
        ("catastrophic", "emotional_tone"),
        ("unprecedented crisis", "emotional_tone"),
        ("explosive", "emotional_tone"),
        ("dramatic surge", "emotional_tone")
    ]
    
    # Factual grounding issues
    factual_phrases = [
        ("sources claim", "factual_grounding"),
        ("allegedly", "factual_grounding"),
        ("reportedly", "factual_grounding"),
        ("critics argue", "factual_grounding")
    ]
    
    # Framing choices
    framing_phrases = [
        ("under fire", "framing_choices"),
        ("faces backlash", "framing_choices"),
        ("controversial", "framing_choices"),
        ("defended their position", "framing_choices")
    ]
    
    # Source transparency issues
    transparency_phrases = [
        ("anonymous sources", "source_transparency"),
        ("unnamed officials", "source_transparency"),
        ("according to reports", "source_transparency"),
        ("leaked documents", "source_transparency")
    ]
    
    all_phrases = ideological_phrases + emotional_phrases + factual_phrases + framing_phrases + transparency_phrases
    
    for phrase_text, bias_type in all_phrases:
        if phrase_text.lower() in content.lower():
            start_pos = content.lower().find(phrase_text.lower())
            if start_pos != -1:
                phrases.append(HighlightedPhrase(
                    text=phrase_text,
                    start_pos=start_pos,
                    end_pos=start_pos + len(phrase_text),
                    bias_type=bias_type,
                    confidence=random.uniform(0.7, 0.95),
                    color=BIAS_COLORS[bias_type]
                ))
    
    return phrases[:5]  # Limit to 5 highlights per article

# Sample article templates (updated with new bias dimensions in mind)
ARTICLE_TEMPLATES = [
    # Climate Policy Narrative
    {
        "narrative_id": "climate-policy",
        "articles": [
            {
                "title": "Biden's Climate Plan Faces Devastating Blow as Key Provisions Struck Down",
                "content": "In a shocking revelation that sent shockwaves through environmental circles, a federal court delivered a devastating blow to the administration's climate agenda. The ruling represents an unprecedented crisis for environmental policy, with critics arguing the decision could have catastrophic consequences for future generations. According to reports from anonymous sources, legal experts claim the court's extreme measures effectively gut the program's core provisions. The controversial decision allegedly stems from procedural violations.",
                "source": "CNN",
                "topic_modifier": {"emotional_tone": 20, "framing_choices": 15}
            },
            {
                "title": "Court Delivers Common-Sense Solution to Regulatory Overreach",
                "content": "A federal appeals court struck down key provisions of the administration's climate regulations in what legal experts are calling a victory for economic freedom. The ruling challenges what critics describe as the radical agenda of environmental extremists. Unnamed officials claim the decision will allegedly save businesses billions while reportedly restoring balance to environmental policy. The administration faces backlash from industry groups who defended their position against regulatory overreach.",
                "source": "Fox News",
                "topic_modifier": {"ideological_stance": 20, "framing_choices": 25}
            },
            {
                "title": "Appeals Court Rules Against Climate Regulations",
                "content": "The U.S. Court of Appeals for the D.C. Circuit ruled against several climate regulations on Tuesday, citing procedural concerns in the rulemaking process. The three-judge panel found that the Environmental Protection Agency had not followed proper administrative procedures when implementing the contested provisions. Industry groups welcomed the decision, while environmental advocates expressed disappointment. The EPA indicated it would review the ruling and consider its options for appeal.",
                "source": "Reuters",
                "topic_modifier": {"emotional_tone": -10, "framing_choices": -15}
            }
        ]
    },
    
    # Economic Recovery Narrative
    {
        "narrative_id": "economic-recovery",
        "articles": [
            {
                "title": "Jobs Report Shows Dramatic Surge in Employment Growth",
                "content": "The latest employment data reveals an explosive recovery in the job market, with unemployment dropping to levels not seen since before the pandemic. Economists describe the numbers as a shocking revelation of economic resilience. The unprecedented growth reportedly demonstrates the success of recent policy measures, though critics argue more work remains to be done. According to reports from labor analysts, the controversial stimulus spending allegedly contributed to the dramatic surge.",
                "source": "CNN",
                "topic_modifier": {"emotional_tone": 15, "framing_choices": 10}
            },
            {
                "title": "Employment Numbers Mask Underlying Economic Concerns",
                "content": "While headline unemployment figures show improvement, a deeper analysis reveals concerning trends beneath the surface. Many of the jobs created are allegedly temporary or part-time positions, according to unnamed officials familiar with the data. The radical agenda of excessive government spending may have created artificial demand, critics argue, leading to potentially catastrophic long-term consequences for fiscal stability. Anonymous sources claim the administration faces backlash over economic policy.",
                "source": "Wall Street Journal",
                "topic_modifier": {"factual_grounding": -10, "source_transparency": -15}
            },
            {
                "title": "US Unemployment Rate Falls to 3.7% in Latest Report",
                "content": "The Bureau of Labor Statistics reported that unemployment fell to 3.7% last month, down from 3.9% the previous month. The economy added 245,000 jobs, slightly below economist expectations of 250,000. Labor force participation remained steady at 62.8%. The Federal Reserve is monitoring these indicators as it considers future monetary policy decisions. Both seasonal adjustments and methodology remain consistent with previous reports.",
                "source": "Associated Press"
            }
        ]
    },
    
    # Tech Regulation Narrative
    {
        "narrative_id": "tech-regulation",
        "articles": [
            {
                "title": "Silicon Valley Giants Face Unprecedented Regulatory Crackdown",
                "content": "In a shocking revelation that has sent shockwaves through the tech industry, federal regulators announced explosive new measures targeting major technology companies. The unprecedented crisis for Big Tech allegedly stems from failed policies of self-regulation, according to leaked documents from unnamed officials. Critics argue these extreme measures represent a devastating blow to innovation, while anonymous sources claim the companies reportedly engaged in anti-competitive practices under fire from regulators.",
                "source": "The Guardian",
                "topic_modifier": {"emotional_tone": 25, "source_transparency": -20}
            },
            {
                "title": "Government Overreach Threatens Tech Innovation Engine",
                "content": "The administration's radical agenda to regulate technology companies represents a catastrophic threat to American innovation leadership. These extreme measures allegedly target successful companies that have driven economic growth, according to reports from industry insiders. The common-sense solution, critics argue, is to let market forces work rather than impose devastating regulatory burdens that unnamed officials claim could reportedly destroy jobs and innovation. The controversial crackdown faces backlash from business leaders.",
                "source": "Fox News",
                "topic_modifier": {"ideological_stance": 25, "framing_choices": 20}
            },
            {
                "title": "Antitrust Regulators Announce Investigation into Tech Practices",
                "content": "The Department of Justice and Federal Trade Commission announced a joint investigation into competitive practices among major technology platforms. The investigation will examine market concentration, data privacy policies, and acquisition strategies over the past five years. Technology companies expressed willingness to cooperate with the investigation while maintaining that their practices comply with existing regulations. The agencies plan to complete their preliminary review within six months.",
                "source": "Reuters"
            }
        ]
    }
]

def generate_mock_articles() -> list[Article]:
    """Generate realistic mock articles"""
    articles = []
    base_time = datetime.now() - timedelta(days=3)
    
    for narrative in ARTICLE_TEMPLATES:
        narrative_id = narrative["narrative_id"]
        
        for i, template in enumerate(narrative["articles"]):
            article_id = str(uuid.uuid4())
            published_date = base_time + timedelta(hours=i*8 + random.randint(0, 120))
            
            bias_scores = create_bias_scores(
                template["source"], 
                template.get("topic_modifier")
            )
            
            highlighted_phrases = create_highlighted_phrases(template["content"], bias_scores)
            
            article = Article(
                id=article_id,
                title=template["title"],
                content=template["content"],
                source=template["source"],
                author=f"Reporter {random.randint(1, 50)}",
                published_date=published_date,
                url=f"https://{template['source'].lower().replace(' ', '')}.com/article/{article_id[:8]}",
                bias_scores=bias_scores,
                highlighted_phrases=highlighted_phrases,
                narrative_id=narrative_id
            )
            
            articles.append(article)
    
    return articles

def generate_mock_narratives(articles: list[Article]) -> list[Narrative]:
    """Generate narrative clusters from articles"""
    narratives = []
    
    narrative_info = {
        "climate-policy": {
            "title": "Climate Policy Court Ruling",
            "description": "Federal court strikes down key climate regulations, sparking debate over environmental policy",
            "dominant_framing": "Legal challenge to environmental regulations"
        },
        "economic-recovery": {
            "title": "Economic Recovery Indicators",
            "description": "Mixed signals in employment data fuel debate over economic health and policy effectiveness",
            "dominant_framing": "Employment growth vs. underlying economic concerns"
        },
        "tech-regulation": {
            "title": "Big Tech Regulatory Crackdown",
            "description": "Federal regulators announce new investigations into major technology companies",
            "dominant_framing": "Government regulation vs. tech industry innovation"
        }
    }
    
    for narrative_id, info in narrative_info.items():
        narrative_articles = [a for a in articles if a.narrative_id == narrative_id]
        
        if not narrative_articles:
            continue
            
        # Calculate average bias scores across all 5 dimensions
        avg_overall = sum(a.bias_scores.overall for a in narrative_articles) / len(narrative_articles)
        avg_ideological = sum(a.bias_scores.ideological_stance for a in narrative_articles) / len(narrative_articles)
        avg_factual = sum(a.bias_scores.factual_grounding for a in narrative_articles) / len(narrative_articles)
        avg_framing = sum(a.bias_scores.framing_choices for a in narrative_articles) / len(narrative_articles)
        avg_emotional = sum(a.bias_scores.emotional_tone for a in narrative_articles) / len(narrative_articles)
        avg_transparency = sum(a.bias_scores.source_transparency for a in narrative_articles) / len(narrative_articles)
        
        avg_bias_scores = BiasScores(
            overall=round(avg_overall, 1),
            ideological_stance=round(avg_ideological, 1),
            factual_grounding=round(avg_factual, 1),
            framing_choices=round(avg_framing, 1),
            emotional_tone=round(avg_emotional, 1),
            source_transparency=round(avg_transparency, 1)
        )
        
        # Create bias evolution timeline
        bias_evolution = []
        for i, article in enumerate(sorted(narrative_articles, key=lambda x: x.published_date)):
            bias_evolution.append(TimePoint(
                timestamp=article.published_date,
                bias_scores=article.bias_scores,
                article_count=i + 1
            ))
        
        narrative = Narrative(
            id=narrative_id,
            title=info["title"],
            description=info["description"],
            article_ids=[a.id for a in narrative_articles],
            dominant_framing=info["dominant_framing"],
            article_count=len(narrative_articles),
            avg_bias_scores=avg_bias_scores,
            created_date=min(a.published_date for a in narrative_articles),
            last_updated=max(a.published_date for a in narrative_articles),
            bias_evolution=bias_evolution
        )
        
        narratives.append(narrative)
    
    return narratives

# Global data storage (in-memory for prototype)
MOCK_ARTICLES = generate_mock_articles()
MOCK_NARRATIVES = generate_mock_narratives(MOCK_ARTICLES)

# Helper functions for API endpoints
def get_all_articles() -> list[Article]:
    return MOCK_ARTICLES

def get_article_by_id(article_id: str) -> Article:
    for article in MOCK_ARTICLES:
        if article.id == article_id:
            return article
    return None

def get_all_narratives() -> list[Narrative]:
    return MOCK_NARRATIVES

def get_narrative_by_id(narrative_id: str) -> Narrative:
    for narrative in MOCK_NARRATIVES:
        if narrative.id == narrative_id:
            return narrative
    return None
```
# End of file: bias-labs-backend/mock_data.py

# File: bias-labs-backend/models.py
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class BiasScores(BaseModel):
    overall: float = Field(..., ge=0, le=100, description="Overall bias score 0-100")
    ideological_stance: float = Field(..., ge=-100, le=100, description="Ideological stance -100 (left) to 100 (right)")
    factual_grounding: float = Field(..., ge=0, le=100, description="Factual accuracy and evidence-based reporting score")
    framing_choices: float = Field(..., ge=0, le=100, description="Neutral vs. biased framing and perspective score")
    emotional_tone: float = Field(..., ge=0, le=100, description="Emotional/sensational language score")
    source_transparency: float = Field(..., ge=0, le=100, description="Source attribution and transparency score")

class HighlightedPhrase(BaseModel):
    text: str = Field(..., description="The biased phrase")
    start_pos: int = Field(..., description="Starting position in text")
    end_pos: int = Field(..., description="Ending position in text")
    bias_type: str = Field(..., description="Type of bias (ideological_stance, factual_grounding, framing_choices, emotional_tone, source_transparency)")
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
```
# End of file: bias-labs-backend/models.py

# File: bias-labs-backend/requirements.txt
```text
fastapi==0.116.1
uvicorn[standard]==0.25.0
pydantic==2.10.3
python-multipart==0.0.20
python-dateutil==2.8.2
```
# End of file: bias-labs-backend/requirements.txt

# File: bias-labs-frontend/.gitignore
```text
# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# production
/build

# misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

npm-debug.log*
yarn-debug.log*
yarn-error.log*
```
# End of file: bias-labs-frontend/.gitignore

# File: bias-labs-frontend/README.md
```markdown
# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
```
# End of file: bias-labs-frontend/README.md

# File: bias-labs-frontend/src/App.css
```css
/* Reset and base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f8fafc;
  color: #1a202c;
  line-height: 1.6;
}

.App {
  min-height: 100vh;
}

/* Header styles */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.8rem;
  font-weight: 700;
  text-decoration: none;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo:hover {
  opacity: 0.9;
}

.tagline {
  font-size: 0.9rem;
  opacity: 0.9;
}

/* Main content */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Loading states */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
  font-size: 1.1rem;
  color: #666;
}

.loading::after {
  content: '';
  width: 20px;
  height: 20px;
  border: 2px solid #ccc;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-left: 0.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Error states */
.error {
  background-color: #fed7d7;
  border: 1px solid #fc8181;
  color: #c53030;
  padding: 1rem;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

/* Narrative clusters */
.narrative-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.narrative-card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  transition: all 0.2s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.narrative-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.narrative-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2d3748;
}

.narrative-description {
  color: #4a5568;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.narrative-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.article-count {
  background-color: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 500;
}

.bias-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bias-score {
  font-weight: 600;
  font-size: 0.9rem;
}

.bias-bar {
  width: 60px;
  height: 6px;
  background-color: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.bias-fill {
  height: 100%;
  transition: width 0.3s ease;
}

/* Article cards */
.article-grid {
  display: grid;
  gap: 1rem;
  margin-bottom: 2rem;
}

.article-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: 1.25rem;
  transition: all 0.2s ease;
  cursor: pointer;
  border-left: 4px solid #e2e8f0;
}

.article-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateX(2px);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.article-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.4;
  flex: 1;
}

.article-source {
  font-size: 0.85rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.article-date {
  font-size: 0.8rem;
  color: #718096;
  margin-bottom: 0.5rem;
}

/* Bias colors */
.bias-low {
  background-color: #48bb78;
}

.bias-medium {
  background-color: #ed8936;
}

.bias-high {
  background-color: #f56565;
}

/* Page headers */
.page-header {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #4a5568;
  max-width: 600px;
  margin: 0 auto;
}

/* Responsive design */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }

  .narrative-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .page-title {
    font-size: 1.8rem;
  }

  .article-header {
    flex-direction: column;
    gap: 0.5rem;
  }

  .article-source {
    align-self: flex-start;
  }
}

/* Button styles */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #667eea;
  color: white;
}

.btn-primary:hover {
  background-color: #5a6fd8;
}

.btn-secondary {
  background-color: #e2e8f0;
  color: #4a5568;
}

.btn-secondary:hover {
  background-color: #cbd5e0;
}
```
# End of file: bias-labs-frontend/src/App.css

# File: bias-labs-frontend/src/App.js
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Import components
import Header from './components/Header';
import Homepage from './pages/Homepage';
import NarrativeDetail from './pages/NarrativeDetail';
import ArticleDetail from './pages/ArticleDetail';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Homepage />} />
            <Route path="/narrative/:narrativeId" element={<NarrativeDetail />} />
            <Route path="/article/:articleId" element={<ArticleDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
```
# End of file: bias-labs-frontend/src/App.js

# File: bias-labs-frontend/src/App.test.js
```javascript
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
```
# End of file: bias-labs-frontend/src/App.test.js

# File: bias-labs-frontend/src/components/BiasRadar.js
```javascript
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
```
# End of file: bias-labs-frontend/src/components/BiasRadar.js

# File: bias-labs-frontend/src/components/BiasTimeline.js
```javascript
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BiasTimeline = ({ timelineData }) => {
  if (!timelineData || timelineData.length === 0) {
    return <div style={{ textAlign: 'center', color: '#666' }}>No timeline data available</div>;
  }

  // Format data for the chart with all 5 dimensions
  const chartData = timelineData.map((point, index) => ({
    time: new Date(point.timestamp).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit'
    }),
    timestamp: point.timestamp,
    overallBias: point.bias_scores.overall,
    ideologicalStance: Math.abs(point.bias_scores.ideological_stance),
    factualGrounding: 100 - point.bias_scores.factual_grounding, // Invert for consistency
    framingChoices: point.bias_scores.framing_choices,
    emotionalTone: point.bias_scores.emotional_tone, // Now included in chart
    sourceTransparency: 100 - point.bias_scores.source_transparency, // Invert for consistency
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
          <p style={{ color: '#ff6b6b', margin: '0.25rem 0' }}>
            Ideological Stance: {data.ideologicalStance.toFixed(1)}%
          </p>
          <p style={{ color: '#48dbfb', margin: '0.25rem 0' }}>
            Factual Grounding: {data.factualGrounding.toFixed(1)}%
          </p>
          <p style={{ color: '#feca57', margin: '0.25rem 0' }}>
            Framing Choices: {data.framingChoices.toFixed(1)}%
          </p>
          <p style={{ color: '#ff9ff3', margin: '0.25rem 0' }}>
            Emotional Tone: {data.emotionalTone.toFixed(1)}%
          </p>
          <p style={{ color: '#54a0ff', margin: '0.25rem 0' }}>
            Source Transparency: {data.sourceTransparency.toFixed(1)}%
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
            dataKey="ideologicalStance"
            stroke="#ff6b6b"
            strokeWidth={3}
            dot={{ fill: '#ff6b6b', strokeWidth: 2, r: 4 }}
            name="Ideological Stance"
          />
          <Line
            type="monotone"
            dataKey="factualGrounding"
            stroke="#48dbfb"
            strokeWidth={2}
            dot={{ fill: '#48dbfb', strokeWidth: 1, r: 3 }}
            name="Factual Grounding"
          />
          <Line
            type="monotone"
            dataKey="framingChoices"
            stroke="#feca57"
            strokeWidth={2}
            dot={{ fill: '#feca57', strokeWidth: 1, r: 3 }}
            name="Framing Choices"
          />
          <Line
            type="monotone"
            dataKey="emotionalTone"
            stroke="#ff9ff3"
            strokeWidth={2}
            dot={{ fill: '#ff9ff3', strokeWidth: 1, r: 3 }}
            name="Emotional Tone"
          />
          <Line
            type="monotone"
            dataKey="sourceTransparency"
            stroke="#54a0ff"
            strokeWidth={2}
            dot={{ fill: '#54a0ff', strokeWidth: 1, r: 3 }}
            name="Source Transparency"
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
```
# End of file: bias-labs-frontend/src/components/BiasTimeline.js

# File: bias-labs-frontend/src/components/Header.js
```javascript
import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          🔍 Bias Labs
        </Link>
        <div className="tagline">
          AI-powered media bias analysis
        </div>
      </div>
    </header>
  );
};

export default Header;
```
# End of file: bias-labs-frontend/src/components/Header.js

# File: bias-labs-frontend/src/components/HighlightedText.js
```javascript
import React from 'react';

// Consistent color scheme for bias highlighting across the project
const BIAS_COLORS = {
  "ideological_stance": "#ff6b6b",      // Red for ideological bias
  "factual_grounding": "#48dbfb",       // Blue for factual issues  
  "framing_choices": "#feca57",         // Orange for framing bias
  "emotional_tone": "#ff9ff3",          // Pink for emotional language
  "source_transparency": "#54a0ff"      // Purple for source transparency issues
};

const HighlightedText = ({ content, highlights = [] }) => {
  if (!content) {
    return <div style={{ color: '#666' }}>No content available</div>;
  }

  if (!highlights || highlights.length === 0) {
    return <div>{content}</div>;
  }

  // Bias type labels for tooltips
  const biasTypeLabels = {
    'ideological_stance': 'Ideological Stance',
    'factual_grounding': 'Factual Grounding',
    'framing_choices': 'Framing Choices',
    'emotional_tone': 'Emotional Tone',
    'source_transparency': 'Source Transparency'
  };

  // Sort highlights by start position to process them in order
  const sortedHighlights = [...highlights].sort((a, b) => a.start_pos - b.start_pos);

  // Build the highlighted text
  let result = [];
  let lastPos = 0;

  sortedHighlights.forEach((highlight, index) => {
    const { start_pos, end_pos, text, bias_type, confidence } = highlight;
    
    // Use consistent color from our palette, fallback to original color if needed
    const color = BIAS_COLORS[bias_type] || highlight.color || '#cccccc';

    // Add text before this highlight
    if (start_pos > lastPos) {
      result.push(
        <span key={`text-${index}`}>
          {content.substring(lastPos, start_pos)}
        </span>
      );
    }

    // Add the highlighted text
    result.push(
      <span
        key={`highlight-${index}`}
        style={{
          backgroundColor: color,
          padding: '2px 4px',
          borderRadius: '3px',
          color: '#000',
          fontWeight: '500',
          cursor: 'help',
          position: 'relative'
        }}
        title={`${biasTypeLabels[bias_type] || bias_type} bias (${Math.round(confidence * 100)}% confidence)`}
      >
        {text}
      </span>
    );

    lastPos = end_pos;
  });

  // Add remaining text
  if (lastPos < content.length) {
    result.push(
      <span key="text-final">
        {content.substring(lastPos)}
      </span>
    );
  }

  return <div>{result}</div>;
};

export default HighlightedText;
```
# End of file: bias-labs-frontend/src/components/HighlightedText.js

# File: bias-labs-frontend/src/index.css
```css
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
```
# End of file: bias-labs-frontend/src/index.css

# File: bias-labs-frontend/src/index.js
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
```
# End of file: bias-labs-frontend/src/index.js

# File: bias-labs-frontend/src/logo.svg
```text
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 841.9 595.3"><g fill="#61DAFB"><path d="M666.3 296.5c0-32.5-40.7-63.3-103.1-82.4 14.4-63.6 8-114.2-20.2-130.4-6.5-3.8-14.1-5.6-22.4-5.6v22.3c4.6 0 8.3.9 11.4 2.6 13.6 7.8 19.5 37.5 14.9 75.7-1.1 9.4-2.9 19.3-5.1 29.4-19.6-4.8-41-8.5-63.5-10.9-13.5-18.5-27.5-35.3-41.6-50 32.6-30.3 63.2-46.9 84-46.9V78c-27.5 0-63.5 19.6-99.9 53.6-36.4-33.8-72.4-53.2-99.9-53.2v22.3c20.7 0 51.4 16.5 84 46.6-14 14.7-28 31.4-41.3 49.9-22.6 2.4-44 6.1-63.6 11-2.3-10-4-19.7-5.2-29-4.7-38.2 1.1-67.9 14.6-75.8 3-1.8 6.9-2.6 11.5-2.6V78.5c-8.4 0-16 1.8-22.6 5.6-28.1 16.2-34.4 66.7-19.9 130.1-62.2 19.2-102.7 49.9-102.7 82.3 0 32.5 40.7 63.3 103.1 82.4-14.4 63.6-8 114.2 20.2 130.4 6.5 3.8 14.1 5.6 22.5 5.6 27.5 0 63.5-19.6 99.9-53.6 36.4 33.8 72.4 53.2 99.9 53.2 8.4 0 16-1.8 22.6-5.6 28.1-16.2 34.4-66.7 19.9-130.1 62-19.1 102.5-49.9 102.5-82.3zm-130.2-66.7c-3.7 12.9-8.3 26.2-13.5 39.5-4.1-8-8.4-16-13.1-24-4.6-8-9.5-15.8-14.4-23.4 14.2 2.1 27.9 4.7 41 7.9zm-45.8 106.5c-7.8 13.5-15.8 26.3-24.1 38.2-14.9 1.3-30 2-45.2 2-15.1 0-30.2-.7-45-1.9-8.3-11.9-16.4-24.6-24.2-38-7.6-13.1-14.5-26.4-20.8-39.8 6.2-13.4 13.2-26.8 20.7-39.9 7.8-13.5 15.8-26.3 24.1-38.2 14.9-1.3 30-2 45.2-2 15.1 0 30.2.7 45 1.9 8.3 11.9 16.4 24.6 24.2 38 7.6 13.1 14.5 26.4 20.8 39.8-6.3 13.4-13.2 26.8-20.7 39.9zm32.3-13c5.4 13.4 10 26.8 13.8 39.8-13.1 3.2-26.9 5.9-41.2 8 4.9-7.7 9.8-15.6 14.4-23.7 4.6-8 8.9-16.1 13-24.1zM421.2 430c-9.3-9.6-18.6-20.3-27.8-32 9 .4 18.2.7 27.5.7 9.4 0 18.7-.2 27.8-.7-9 11.7-18.3 22.4-27.5 32zm-74.4-58.9c-14.2-2.1-27.9-4.7-41-7.9 3.7-12.9 8.3-26.2 13.5-39.5 4.1 8 8.4 16 13.1 24 4.7 8 9.5 15.8 14.4 23.4zM420.7 163c9.3 9.6 18.6 20.3 27.8 32-9-.4-18.2-.7-27.5-.7-9.4 0-18.7.2-27.8.7 9-11.7 18.3-22.4 27.5-32zm-74 58.9c-4.9 7.7-9.8 15.6-14.4 23.7-4.6 8-8.9 16-13 24-5.4-13.4-10-26.8-13.8-39.8 13.1-3.1 26.9-5.8 41.2-7.9zm-90.5 125.2c-35.4-15.1-58.3-34.9-58.3-50.6 0-15.7 22.9-35.6 58.3-50.6 8.6-3.7 18-7 27.7-10.1 5.7 19.6 13.2 40 22.5 60.9-9.2 20.8-16.6 41.1-22.2 60.6-9.9-3.1-19.3-6.5-28-10.2zM310 490c-13.6-7.8-19.5-37.5-14.9-75.7 1.1-9.4 2.9-19.3 5.1-29.4 19.6 4.8 41 8.5 63.5 10.9 13.5 18.5 27.5 35.3 41.6 50-32.6 30.3-63.2 46.9-84 46.9-4.5-.1-8.3-1-11.3-2.7zm237.2-76.2c4.7 38.2-1.1 67.9-14.6 75.8-3 1.8-6.9 2.6-11.5 2.6-20.7 0-51.4-16.5-84-46.6 14-14.7 28-31.4 41.3-49.9 22.6-2.4 44-6.1 63.6-11 2.3 10.1 4.1 19.8 5.2 29.1zm38.5-66.7c-8.6 3.7-18 7-27.7 10.1-5.7-19.6-13.2-40-22.5-60.9 9.2-20.8 16.6-41.1 22.2-60.6 9.9 3.1 19.3 6.5 28.1 10.2 35.4 15.1 58.3 34.9 58.3 50.6-.1 15.7-23 35.6-58.4 50.6zM320.8 78.4z"/><circle cx="420.9" cy="296.5" r="45.7"/><path d="M520.5 78.1z"/></g></svg>
```
# End of file: bias-labs-frontend/src/logo.svg

# File: bias-labs-frontend/src/pages/ArticleDetail.js
```javascript
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

  const getIdeologicalStanceLabel = (ideologicalStance) => {
    if (ideologicalStance >= 60) return 'Right';
    if (ideologicalStance >= 20) return 'Skews Right';
    if (ideologicalStance > -20) return 'Center';
    if (ideologicalStance > -60) return 'Skews Left';
    return 'Left';
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
              <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
                Ideological Lean: <strong>{getIdeologicalStanceLabel(article.bias_scores.ideological_stance)}</strong>
              </div>
              <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.25rem' }}>
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
```
# End of file: bias-labs-frontend/src/pages/ArticleDetail.js

# File: bias-labs-frontend/src/pages/Homepage.js
```javascript
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
```
# End of file: bias-labs-frontend/src/pages/Homepage.js

# File: bias-labs-frontend/src/pages/NarrativeDetail.js
```javascript
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

  const getIdeologicalStanceLabel = (ideologicalStance) => {
    if (ideologicalStance >= 60) return 'Right';
    if (ideologicalStance >= 20) return 'Skews Right';
    if (ideologicalStance > -20) return 'Center';
    if (ideologicalStance > -60) return 'Skews Left';
    return 'Left';
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
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '4rem' }}>
        <div>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem', fontWeight: '600' }}>
            Average Bias Analysis
          </h2>
          <div style={{ minHeight: '400px' }}> {/* Added min height to ensure proper spacing */}
            <BiasRadar biasScores={narrative.avg_bias_scores} />
          </div>
        </div>
        <div>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem', fontWeight: '600' }}>
            Bias Evolution Over Time
          </h2>
          <div style={{ minHeight: '400px' }}> {/* Added min height to ensure proper spacing */}
            {narrative.bias_evolution && narrative.bias_evolution.length > 0 ? (
              <BiasTimeline timelineData={narrative.bias_evolution} />
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#666', background: '#f8f9fa', borderRadius: '0.5rem' }}>
                Not enough data points for timeline
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Articles Section - Now with proper spacing */}
      <div style={{ marginTop: '3rem' }}> {/* Added explicit margin top */}
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
              <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', flexWrap: 'wrap' }}>
                <span>Overall Bias: <strong>{article.bias_scores.overall.toFixed(1)}%</strong></span>
                <span>Ideological: <strong>{getIdeologicalStanceLabel(article.bias_scores.ideological_stance)}</strong></span>
                <span>Factual Issues: <strong>{(100 - article.bias_scores.factual_grounding).toFixed(0)}%</strong></span>
                <span>Emotional: <strong>{article.bias_scores.emotional_tone.toFixed(0)}%</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NarrativeDetail;
```
# End of file: bias-labs-frontend/src/pages/NarrativeDetail.js

# File: bias-labs-frontend/src/reportWebVitals.js
```javascript
const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
```
# End of file: bias-labs-frontend/src/reportWebVitals.js

# File: bias-labs-frontend/src/services/api.js
```javascript
import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Health check
  async getHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  // Narratives
  async getNarratives() {
    const response = await api.get('/narratives');
    return response.data;
  },

  async getNarrativeDetail(narrativeId) {
    const response = await api.get(`/narratives/${narrativeId}`);
    return response.data;
  },

  async getNarrativeTimeline(narrativeId) {
    const response = await api.get(`/narratives/${narrativeId}/timeline`);
    return response.data;
  },

  async getNarrativeArticles(narrativeId) {
    const response = await api.get(`/narratives/${narrativeId}/articles`);
    return response.data;
  },

  // Articles
  async getArticles(params = {}) {
    const response = await api.get('/articles', { params });
    return response.data;
  },

  async getArticleDetail(articleId) {
    const response = await api.get(`/articles/${articleId}`);
    return response.data;
  },

  // Statistics
  async getStats() {
    const response = await api.get('/stats');
    return response.data;
  },
};

// Error handling wrapper
export const withErrorHandling = async (apiCall) => {
  try {
    return await apiCall();
  } catch (error) {
    console.error('API Error:', error);
    if (error.response) {
      // Server responded with error status
      throw new Error(`API Error: ${error.response.data.detail || error.response.statusText}`);
    } else if (error.request) {
      // Network error
      throw new Error('Network Error: Unable to connect to the server');
    } else {
      // Other error
      throw new Error(`Error: ${error.message}`);
    }
  }
};

export default api;
```
# End of file: bias-labs-frontend/src/services/api.js

# File: bias-labs-frontend/src/setupTests.js
```javascript
// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
```
# End of file: bias-labs-frontend/src/setupTests.js

