# 🔍 The Bias Lab - Full-Stack Engineer Work Sample

**72-Hour Deliverable for Track 2: Full-Stack Engineer Position**

Built by: Ayush Kumar
Submitted: August 10, 2025
Live Demo: [Your Deployment URL]

---

## 📋 Work Sample Brief Compliance

This prototype hits all the Track 2 requirements from your brief:

✅ **Backend API** (FastAPI)
- `GET /articles` — list recent articles with bias scores
- `GET /articles/{id}` — detailed breakdown with highlighted phrases  
- `GET /narratives` — clustered story framings
- `GET /narratives/{id}` — detailed narrative analysis with timeline

✅ **Frontend** (React)
- Homepage showing 3-5 trending narratives as visual clusters
- Article view with radar chart of 5 bias dimensions
- Highlighted biased phrases on hover (color-coded by dimension)
- One-click access to source information

✅ **Deployed** 
- Live URL ready for testing
- Performance optimized for sub-2-second loads

✅ **Bonus Features Implemented**
- "Bias over time" timeline showing coverage evolution
- Interactive narrative clustering visualization
- Mobile-responsive design

## 🏗️ Architecture Overview

### Backend Stack
```
FastAPI + Python
├── main.py           # API routes with CORS configuration
├── models.py         # Pydantic schemas for bias scoring
├── mock_data.py      # Realistic data matching your 5-dimension framework
└── requirements.txt  # Minimal production-ready dependencies
```

### Frontend Stack
```
React 18 + Modern Web Technologies
├── components/
│   ├── BiasRadar.js     # 5-dimension radar charts
│   ├── BiasTimeline.js  # Bias evolution over time
│   └── HighlightedText.js # Interactive phrase highlighting
├── pages/
│   ├── Homepage.js      # Narrative cluster discovery
│   ├── ArticleDetail.js # Individual article analysis
│   └── NarrativeDetail.js # Cross-source comparison
└── services/api.js      # API integration layer
```

## 🚀 Quick Start

### Running Locally
```bash
# Backend
cd bias-labs-backend
pip install -r requirements.txt
python main.py  # Runs on :8000

# Frontend  
cd bias-labs-frontend
npm install
npm start      # Runs on :3000
```

### Testing the Demo
1. **Homepage**: View trending narrative clusters with bias indicators
2. **Narrative Detail**: Click clusters to see cross-source analysis
3. **Article Analysis**: Click individual articles for detailed breakdown
4. **Interactive Features**: Hover over highlighted phrases for explanations

## 📊 Mock Data Design

### Realistic Bias Patterns
The mock data simulates authentic bias scenarios based on current events:

- **Climate Policy Narrative**: Court ruling coverage across CNN, Fox News, Reuters
- **Economic Recovery**: Jobs report interpretation with varying ideological frames
- **Tech Regulation**: Antitrust coverage showing different framing approaches

### 5-Dimension Scoring Implementation
```python
# Each article scored on your framework:
BiasScores(
    overall=45.2,                    # 0-100 composite score
    ideological_stance=-25.0,        # -100 (left) to +100 (right)
    factual_grounding=75.0,          # 0-100 evidence quality
    framing_choices=40.0,            # 0-100 neutral vs biased framing
    emotional_tone=35.0,             # 0-100 objective vs sensational
    source_transparency=70.0         # 0-100 attribution clarity
)
```

## 💡 Key Development Decisions

### 1. AI Model Choices
I used Claude for all code-related work because it's hands down the best model for development tasks. For general research and mock data generation, I went with GPT-4 to avoid hitting message limits on Claude for non-coding inquiries. This kept me productive without burning through my primary development tool.

### 2. Technology Stack
**FastAPI** was the obvious choice here. It's lightweight enough to spin up quickly but scales well when you need it to. Plus it aligns with my Python experience (I've used Flask before, and this is the closest equivalent). 

**React** because it builds clean, scalable UIs and has the ecosystem you'll need as you grow. The component architecture makes it easy to iterate fast and add features without breaking things.

---

**Ready to integrate this into your MVP next week.** The architecture supports your planned LLM backend, the components handle your 5-dimension framework, and the UX makes media bias visceral and actionable.

This isn't just a demo—it's the foundation of what you're building.

---
*Built for The Bias Lab • Track 2: Full-Stack Engineer • 72-Hour Work Sample*
