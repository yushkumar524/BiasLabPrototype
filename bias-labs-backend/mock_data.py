from models import Article, BiasScores, HighlightedPhrase, Narrative, TimePoint, ArticleSummary, NarrativeSummary
from datetime import datetime, timedelta
import random
import uuid

# Color scheme for bias highlighting
BIAS_COLORS = {
    "political_lean": "#ff6b6b",      # Red for political bias
    "emotional_language": "#feca57",   # Orange for emotional language
    "source_diversity": "#48dbfb",     # Blue for source issues
    "factual_reporting": "#ff9ff3",    # Pink for factual concerns
    "sensationalism": "#54a0ff"        # Purple for sensationalism
}

# Sample news sources with typical bias patterns
NEWS_SOURCES = {
    "CNN": {"political_lean": -25, "factual_reporting": 75, "emotional_language": 35},
    "Fox News": {"political_lean": 45, "factual_reporting": 65, "emotional_language": 55},
    "Reuters": {"political_lean": 5, "factual_reporting": 90, "emotional_language": 15},
    "BBC": {"political_lean": -10, "factual_reporting": 85, "emotional_language": 20},
    "Wall Street Journal": {"political_lean": 20, "factual_reporting": 80, "emotional_language": 25},
    "The Guardian": {"political_lean": -35, "factual_reporting": 70, "emotional_language": 40},
    "Associated Press": {"political_lean": 0, "factual_reporting": 95, "emotional_language": 10},
    "New York Times": {"political_lean": -20, "factual_reporting": 80, "emotional_language": 30}
}

def create_bias_scores(source: str, topic_modifier: dict = None) -> BiasScores:
    """Create realistic bias scores based on source and topic"""
    base = NEWS_SOURCES.get(source, {"political_lean": 0, "factual_reporting": 75, "emotional_language": 30})
    
    # Add some randomness
    political_lean = base["political_lean"] + random.randint(-10, 10)
    factual_reporting = max(0, min(100, base["factual_reporting"] + random.randint(-15, 15)))
    emotional_language = max(0, min(100, base["emotional_language"] + random.randint(-10, 20)))
    
    # Apply topic modifiers if provided
    if topic_modifier:
        political_lean += topic_modifier.get("political_lean", 0)
        emotional_language += topic_modifier.get("emotional_language", 0)
        factual_reporting += topic_modifier.get("factual_reporting", 0)
    
    # Clamp values
    political_lean = max(-100, min(100, political_lean))
    emotional_language = max(0, min(100, emotional_language))
    factual_reporting = max(0, min(100, factual_reporting))
    
    # Calculate other scores
    source_diversity = random.randint(40, 90)
    overall = (abs(political_lean) + emotional_language + (100 - factual_reporting)) / 3
    
    return BiasScores(
        overall=round(overall, 1),
        political_lean=round(political_lean, 1),
        emotional_language=round(emotional_language, 1),
        source_diversity=round(source_diversity, 1),
        factual_reporting=round(factual_reporting, 1)
    )

def create_highlighted_phrases(content: str, bias_scores: BiasScores) -> list[HighlightedPhrase]:
    """Generate realistic highlighted phrases based on content and bias"""
    phrases = []
    
    # Political bias phrases
    political_phrases = [
        ("devastating blow", "political_lean"),
        ("radical agenda", "political_lean"),
        ("common-sense solution", "political_lean"),
        ("extreme measures", "political_lean"),
        ("failed policies", "political_lean")
    ]
    
    # Emotional language phrases
    emotional_phrases = [
        ("shocking revelation", "emotional_language"),
        ("catastrophic", "emotional_language"),
        ("unprecedented crisis", "emotional_language"),
        ("explosive", "emotional_language"),
        ("dramatic surge", "emotional_language")
    ]
    
    # Factual reporting issues
    factual_phrases = [
        ("sources claim", "factual_reporting"),
        ("allegedly", "factual_reporting"),
        ("reportedly", "factual_reporting"),
        ("critics argue", "factual_reporting")
    ]
    
    all_phrases = political_phrases + emotional_phrases + factual_phrases
    
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

# Sample article templates
ARTICLE_TEMPLATES = [
    # Climate Policy Narrative
    {
        "narrative_id": "climate-policy",
        "articles": [
            {
                "title": "Biden's Climate Plan Faces Devastating Blow as Key Provisions Struck Down",
                "content": "In a shocking revelation that sent shockwaves through environmental circles, a federal court delivered a devastating blow to the administration's climate agenda. The ruling represents an unprecedented crisis for environmental policy, with critics arguing the decision could catastrophic consequences for future generations. Legal experts claim the court's extreme measures effectively gut the program's core provisions.",
                "source": "CNN",
                "topic_modifier": {"emotional_language": 20}
            },
            {
                "title": "Court Delivers Common-Sense Solution to Regulatory Overreach",
                "content": "A federal appeals court struck down key provisions of the administration's climate regulations in what legal experts are calling a victory for economic freedom. The ruling challenges what critics describe as the radical agenda of environmental extremists. Sources claim the decision will allegedly save businesses billions while reportedly restoring balance to environmental policy.",
                "source": "Fox News",
                "topic_modifier": {"political_lean": 20}
            },
            {
                "title": "Appeals Court Rules Against Climate Regulations",
                "content": "The U.S. Court of Appeals for the D.C. Circuit ruled against several climate regulations on Tuesday, citing procedural concerns. The three-judge panel found that the Environmental Protection Agency had not followed proper rulemaking procedures when implementing the contested provisions. Industry groups welcomed the decision, while environmental advocates expressed disappointment.",
                "source": "Reuters",
                "topic_modifier": {"emotional_language": -10}
            }
        ]
    },
    
    # Economic Recovery Narrative
    {
        "narrative_id": "economic-recovery",
        "articles": [
            {
                "title": "Jobs Report Shows Dramatic Surge in Employment Growth",
                "content": "The latest employment data reveals an explosive recovery in the job market, with unemployment dropping to levels not seen since before the pandemic. Economists describe the numbers as a shocking revelation of economic resilience. The unprecedented growth reportedly demonstrates the success of recent policy measures, though critics argue more work remains to be done.",
                "source": "CNN",
                "topic_modifier": {"emotional_language": 15}
            },
            {
                "title": "Employment Numbers Mask Underlying Economic Concerns",
                "content": "While headline unemployment figures show improvement, a deeper analysis reveals concerning trends beneath the surface. Many of the jobs created are allegedly temporary or part-time positions, sources claim. The radical agenda of excessive government spending may have created artificial demand, critics argue, leading to potentially catastrophic long-term consequences for fiscal stability.",
                "source": "Wall Street Journal",
                "topic_modifier": {"factual_reporting": -10}
            },
            {
                "title": "US Unemployment Rate Falls to 3.7% in Latest Report",
                "content": "The Bureau of Labor Statistics reported that unemployment fell to 3.7% last month, down from 3.9% the previous month. The economy added 245,000 jobs, slightly below economist expectations of 250,000. Labor force participation remained steady at 62.8%. The Federal Reserve is monitoring these indicators as it considers future monetary policy decisions.",
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
                "content": "In a shocking revelation that has sent shockwaves through the tech industry, federal regulators announced explosive new measures targeting major technology companies. The unprecedented crisis for Big Tech allegedly stems from failed policies of self-regulation. Critics argue these extreme measures represent a devastating blow to innovation, while sources claim the companies reportedly engaged in anti-competitive practices.",
                "source": "The Guardian",
                "topic_modifier": {"emotional_language": 25}
            },
            {
                "title": "Government Overreach Threatens Tech Innovation Engine",
                "content": "The administration's radical agenda to regulate technology companies represents a catastrophic threat to American innovation leadership. These extreme measures allegedly target successful companies that have driven economic growth. The common-sense solution, critics argue, is to let market forces work rather than impose devastating regulatory burdens that sources claim could reportedly destroy jobs and innovation.",
                "source": "Fox News",
                "topic_modifier": {"political_lean": 25}
            },
            {
                "title": "Antitrust Regulators Announce Investigation into Tech Practices",
                "content": "The Department of Justice and Federal Trade Commission announced a joint investigation into competitive practices among major technology platforms. The investigation will examine market concentration, data privacy policies, and acquisition strategies. Technology companies expressed willingness to cooperate with the investigation while maintaining that their practices comply with existing regulations.",
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
            
        # Calculate average bias scores
        avg_overall = sum(a.bias_scores.overall for a in narrative_articles) / len(narrative_articles)
        avg_political = sum(a.bias_scores.political_lean for a in narrative_articles) / len(narrative_articles)
        avg_emotional = sum(a.bias_scores.emotional_language for a in narrative_articles) / len(narrative_articles)
        avg_source = sum(a.bias_scores.source_diversity for a in narrative_articles) / len(narrative_articles)
        avg_factual = sum(a.bias_scores.factual_reporting for a in narrative_articles) / len(narrative_articles)
        
        avg_bias_scores = BiasScores(
            overall=round(avg_overall, 1),
            political_lean=round(avg_political, 1),
            emotional_language=round(avg_emotional, 1),
            source_diversity=round(avg_source, 1),
            factual_reporting=round(avg_factual, 1)
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