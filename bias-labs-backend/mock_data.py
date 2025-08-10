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

# Sample article templates (updated with guaranteed bias phrases)
ARTICLE_TEMPLATES = [
    # Climate Policy Narrative
    {
        "narrative_id": "climate-policy",
        "articles": [
            {
                "title": "Biden's Climate Plan Faces Devastating Blow as Key Provisions Struck Down",
                "content": "In a shocking revelation that sent shockwaves through environmental circles, a federal court delivered a devastating blow to the administration's climate agenda. The ruling represents an unprecedented crisis for environmental policy, with critics arguing the decision could have catastrophic consequences for future generations. According to reports from anonymous sources, legal experts claim the court's extreme measures effectively gut the program's core provisions. The controversial decision allegedly stems from procedural violations, sources claim. Unnamed officials reportedly defended their position against what they call radical agenda policies.",
                "source": "CNN",
                "topic_modifier": {"emotional_tone": 20, "framing_choices": 15}
            },
            {
                "title": "Court Delivers Common-Sense Solution to Regulatory Overreach",
                "content": "A federal appeals court struck down key provisions of the administration's climate regulations in what legal experts are calling a victory for economic freedom. The ruling challenges what critics describe as the radical agenda of environmental extremists who have allegedly pushed through failed policies. Unnamed officials claim the decision will reportedly save businesses billions while restoring balance to environmental policy. The administration now faces backlash from industry groups who defended their position against the controversial regulatory overreach. Anonymous sources suggest this devastating blow to bureaucratic power represents a common-sense solution.",
                "source": "Fox News",
                "topic_modifier": {"ideological_stance": 20, "framing_choices": 25}
            },
            {
                "title": "Appeals Court Rules Against Climate Regulations",
                "content": "The U.S. Court of Appeals for the D.C. Circuit ruled against several climate regulations on Tuesday, citing procedural concerns in the rulemaking process. The three-judge panel found that the Environmental Protection Agency had not followed proper administrative procedures when implementing the contested provisions. Industry groups welcomed the decision, while environmental advocates expressed disappointment. The EPA indicated it would review the ruling and consider its options for appeal. Critics argue this represents a controversial setback, though sources claim the agency reportedly will continue defending their position. According to reports, unnamed officials allegedly view this as part of a broader pattern.",
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
                "content": "The latest employment data reveals an explosive recovery in the job market, with unemployment dropping to levels not seen since before the pandemic. Economists describe the numbers as a shocking revelation of economic resilience. The unprecedented growth reportedly demonstrates the success of recent policy measures, though critics argue more work remains to be done. According to reports from labor analysts, the controversial stimulus spending allegedly contributed to the dramatic surge. Anonymous sources claim this devastating blow to unemployment represents a common-sense solution, while unnamed officials defended their position on economic policy.",
                "source": "CNN",
                "topic_modifier": {"emotional_tone": 15, "framing_choices": 10}
            },
            {
                "title": "Employment Numbers Mask Underlying Economic Concerns",
                "content": "While headline unemployment figures show improvement, a deeper analysis reveals concerning trends beneath the surface. Many of the jobs created are allegedly temporary or part-time positions, according to unnamed officials familiar with the data. The radical agenda of excessive government spending may have created artificial demand, critics argue, leading to potentially catastrophic long-term consequences for fiscal stability. Anonymous sources claim the administration now faces backlash over failed policies that reportedly mask deeper problems. This controversial approach represents extreme measures that sources claim could deliver a devastating blow to economic stability.",
                "source": "Wall Street Journal",
                "topic_modifier": {"factual_grounding": -10, "source_transparency": -15}
            },
            {
                "title": "US Unemployment Rate Falls to 3.7% in Latest Report",
                "content": "The Bureau of Labor Statistics reported that unemployment fell to 3.7% last month, down from 3.9% the previous month. The economy added 245,000 jobs, slightly below economist expectations of 250,000. Labor force participation remained steady at 62.8%. The Federal Reserve is monitoring these indicators as it considers future monetary policy decisions. Critics argue the numbers are controversial, while sources claim this reportedly represents solid progress. According to reports, unnamed officials allegedly view this as validation of their approach, though some defended their position on the need for continued vigilance.",
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
                "content": "In a shocking revelation that has sent shockwaves through the tech industry, federal regulators announced explosive new measures targeting major technology companies. The unprecedented crisis for Big Tech allegedly stems from failed policies of self-regulation, according to leaked documents from unnamed officials. Critics argue these extreme measures represent a devastating blow to innovation, while anonymous sources claim the companies reportedly engaged in anti-competitive practices. The controversial crackdown has put tech giants under fire as they face backlash from regulators who defended their position on market competition.",
                "source": "The Guardian",
                "topic_modifier": {"emotional_tone": 25, "source_transparency": -20}
            },
            {
                "title": "Government Overreach Threatens Tech Innovation Engine",
                "content": "The administration's radical agenda to regulate technology companies represents a catastrophic threat to American innovation leadership. These extreme measures allegedly target successful companies that have driven economic growth, according to reports from industry insiders. The common-sense solution, critics argue, is to let market forces work rather than impose devastating regulatory burdens that unnamed officials claim could reportedly destroy jobs and innovation. The controversial crackdown puts the industry under fire as companies face backlash from bureaucrats who have defended their position through failed policies and anonymous sources.",
                "source": "Fox News",
                "topic_modifier": {"ideological_stance": 25, "framing_choices": 20}
            },
            {
                "title": "Antitrust Regulators Announce Investigation into Tech Practices",
                "content": "The Department of Justice and Federal Trade Commission announced a joint investigation into competitive practices among major technology platforms. The investigation will examine market concentration, data privacy policies, and acquisition strategies over the past five years. Technology companies expressed willingness to cooperate with the investigation while maintaining that their practices comply with existing regulations. The agencies plan to complete their preliminary review within six months. Some critics argue this controversial move puts companies under fire, while sources claim regulators reportedly defended their position. According to reports, unnamed officials allegedly believe this represents necessary oversight, though the industry faces backlash from various stakeholders.",
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