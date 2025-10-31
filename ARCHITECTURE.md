# 🏗️ Stock Research Chatbot - Architecture Documentation

Complete technical architecture and system design documentation.

**Version**: 2.1.0  
**Last Updated**: October 24, 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Smart Correction System](#smart-correction-system)
6. [Multi-Agent System](#multi-agent-system)
7. [API Design](#api-design)
8. [Database & State Management](#database--state-management)
9. [Security Architecture](#security-architecture)
10. [Deployment Architecture](#deployment-architecture)
11. [Performance & Scaling](#performance--scaling)

---

## System Overview

The Stock Research Chatbot is a production-grade AI system built on a **multi-agent architecture** that combines natural language processing, real-time market data analysis, and intelligent spell correction to provide comprehensive stock research insights.

### Core Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 + Vite | Interactive UI with confirmation dialogs |
| Backend | FastAPI + Python 3.11 | High-performance async API |
| AI Engine | Google Gemini 2.5 Flash | Smart correction & analysis |
| Data Source | Yahoo Finance API | Real-time market data |
| Containerization | Docker + Docker Compose | Production deployment |
| State Management | In-memory (production: Redis) | Conversation state |

### Design Principles

1. **Modularity**: Each agent is independent and specialized
2. **Scalability**: Horizontal scaling via Docker Compose
3. **Reliability**: Comprehensive error handling and fallbacks
4. **User-Friendly**: Interactive confirmations for ambiguous inputs
5. **Production-Ready**: Health checks, logging, monitoring

---

## Architecture Layers

### 1. Presentation Layer (Frontend)

```
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend (Port 3000)                 │
├─────────────────────────────────────────────────────────────┤
│  Components:                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Query Input  │  │ Confirmation │  │   Results    │      │
│  │   Component  │  │    Dialog    │  │   Display    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  State Management: React useState + useEffect               │
│  HTTP Client: Fetch API                                     │
│  Styling: CSS Modules                                       │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Query Input**: Textarea with placeholder examples
- **Confirmation Dialog**: Modal with confidence indicators
- **Results Display**: Tabbed interface for multiple tickers
- **Error Handling**: User-friendly error messages

**File**: `frontend/stock-research-ui/src/App.jsx`

---

### 2. API Layer (Backend)

```
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                 │
├─────────────────────────────────────────────────────────────┤
│  Routes:                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ POST /analyze│  │ GET /health  │  │ GET /docs    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Middleware:                                                 │
│  - CORS (configurable origins)                              │
│  - Request logging (structlog)                              │
│  - Error handling (global exception handler)                │
│                                                              │
│  Models (Pydantic):                                         │
│  - AnalysisRequest                                          │
│  - AnalysisResponse                                         │
│  - CorrectionSuggestion                                     │
│  - ConfirmationPrompt                                       │
│  - TickerInsight                                            │
└─────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `backend/app/main.py` - FastAPI application setup
- `backend/app/api.py` - API route handlers
- `backend/app/models.py` - Pydantic data models

---

### 3. Service Layer

```
┌─────────────────────────────────────────────────────────────┐
│                       Service Layer                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Smart Correction Service                           │   │
│  │  - Gemini AI integration                            │   │
│  │  - Multi-misspelling detection                      │   │
│  │  - Confidence scoring                               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Conversation Manager                               │   │
│  │  - State management (30-min TTL)                    │   │
│  │  - Sequential confirmation flow                     │   │
│  │  - User response processing                         │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Ticker Mapper                                      │   │
│  │  - Company name → ticker mapping                    │   │
│  │  - Fuzzy matching fallback                          │   │
│  │  - 5000+ ticker database                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `backend/services/smart_correction_service.py`
- `backend/services/conversation_manager.py`
- `backend/services/ticker_mapper.py`

---

### 4. Agent Layer (Multi-Agent System)

```
┌─────────────────────────────────────────────────────────────┐
│                  Multi-Agent Orchestrator                    │
├─────────────────────────────────────────────────────────────┤
│  Coordination:                                               │
│  - Parallel agent execution                                 │
│  - Result aggregation                                       │
│  - Error handling per agent                                 │
│                                                              │
│  Agents (6 specialized):                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │    News    │  │   Price    │  │  Earnings  │           │
│  │   Agent    │  │   Agent    │  │   Agent    │           │
│  │            │  │            │  │            │           │
│  │ - Recent   │  │ - Price    │  │ - EPS      │           │
│  │   news     │  │   movement │  │ - Revenue  │           │
│  │ - Sentiment│  │ - Technical│  │ - Guidance │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Insider   │  │  Patents   │  │  Filings   │           │
│  │   Agent    │  │   Agent    │  │   Agent    │           │
│  │            │  │            │  │            │           │
│  │ - Trades   │  │ - IP       │  │ - SEC      │           │
│  │ - Holdings │  │   activity │  │   filings  │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Synthesis Agent                         │   │
│  │  - Aggregates all agent findings                     │   │
│  │  - Generates investment recommendation               │   │
│  │  - Assigns confidence score                          │   │
│  │  - Identifies key drivers, risks, catalysts          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `backend/agents/yahoo_finance_orchestrator.py` - Orchestrator
- `backend/agents/base_agent.py` - Base agent class
- `backend/agents/*_agent.py` - Individual agents
- `backend/agents/synthesis_agent.py` - Final synthesis

---

## Component Details

### Smart Correction Service

**Purpose**: Detect and correct misspelled company names using Gemini AI

**Flow**:
```
User Input → Gemini API → JSON Response → Parsing → Correction Suggestions
```

**Key Methods**:

```python
class SmartCorrectionService:
    def detect_and_correct(self, user_input: str) -> Dict:
        """Detect single misspelling"""
        
    def detect_and_correct_multiple(self, user_input: str) -> Dict:
        """Detect multiple misspellings"""
        
    def generate_confirmation_message(self, correction: Dict) -> str:
        """Generate user-friendly confirmation message"""
```

**Gemini Prompt Template**:
```
Analyze this user input for potential misspellings of publicly traded company names or ticker symbols:

Input: "{user_input}"

Return JSON with corrections for ALL misspellings found.
```

**Response Format**:
```json
{
  "has_misspellings": true,
  "corrections": [
    {
      "original": "metae",
      "corrected_name": "Meta Platforms Inc.",
      "ticker": "META",
      "confidence": "high",
      "explanation": "Likely misspelling of Meta"
    }
  ]
}
```

---

### Conversation Manager

**Purpose**: Manage stateful conversations for multi-step confirmations

**State Machine**:
```
INITIAL → AWAITING_CONFIRMATION → READY_FOR_ANALYSIS → COMPLETED
                ↓
        AWAITING_CLARIFICATION
```

**Key Data Structures**:

```python
class Conversation:
    conversation_id: str
    state: ConversationState
    created_at: datetime
    last_updated: datetime
    original_query: str
    resolved_tickers: List[str]
    pending_confirmations: List[Dict]
    confirmed_tickers: List[str]  # For multi-correction
    user_responses: List[str]
```

**TTL Management**:
- Default: 30 minutes
- Automatic cleanup of expired conversations
- Configurable via `CONVERSATION_TTL` environment variable

---

### Ticker Mapper

**Purpose**: Map company names to ticker symbols

**Data Source**:
- Built-in database of 5000+ tickers
- Major US exchanges (NYSE, NASDAQ)
- Popular international stocks

**Matching Strategy**:
1. **Exact match**: Direct ticker or company name lookup
2. **Fuzzy match**: Using `difflib.SequenceMatcher`
3. **Smart correction**: Gemini AI as final fallback

**Example**:
```python
ticker_mapper.extract_tickers_from_query("Analyze Apple and Microsoft")
# Returns: (["AAPL", "MSFT"], [])

ticker_mapper.extract_tickers_from_query("Analyze Appel")
# Returns: ([], ["Appel"])  # Triggers smart correction
```

---

## Data Flow

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Input                                                │
│    "Analyze metae Apple and TSLAA"                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Frontend → Backend                                        │
│    POST /api/v1/analyze                                     │
│    { "query": "Analyze metae Apple and TSLAA" }            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Smart Correction Service                                 │
│    - Sends query to Gemini API                              │
│    - Detects: "metae" → META, "TSLAA" → TSLA               │
│    - Returns: 2 corrections                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Conversation Manager                                     │
│    - Creates conversation (UUID)                            │
│    - Stores pending_confirmations: [META, TSLA]            │
│    - Returns first confirmation prompt                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Backend → Frontend                                        │
│    { "needs_confirmation": true,                            │
│      "confirmation_prompt": {                               │
│        "message": "Did you mean Meta (META)?",              │
│        "conversation_id": "uuid"                            │
│      }}                                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. User Confirms: "Yes"                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Frontend → Backend                                        │
│    POST /api/v1/analyze                                     │
│    { "query": "...",                                        │
│      "conversation_id": "uuid",                             │
│      "confirmation_response": "Yes" }                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Conversation Manager                                     │
│    - Processes "Yes" response                               │
│    - Adds META to confirmed_tickers                         │
│    - Checks pending_confirmations: [TSLA] remaining         │
│    - Returns second confirmation prompt                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. User Confirms: "Yes" (for TSLA)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. Conversation Manager                                    │
│     - All confirmations complete                            │
│     - confirmed_tickers: [META, TSLA]                       │
│     - Extracts correctly spelled: [AAPL]                    │
│     - Final tickers: [META, AAPL, TSLA]                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. Multi-Agent Orchestrator                                │
│     - Spawns 6 agents per ticker (18 total)                 │
│     - Parallel execution                                    │
│     - Aggregates results                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 12. Synthesis Agent                                         │
│     - Analyzes all agent findings                           │
│     - Generates recommendations                             │
│     - Assigns confidence scores                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 13. Backend → Frontend                                       │
│     { "success": true,                                      │
│       "insights": [                                         │
│         { "ticker": "META", "stance": "buy", ... },        │
│         { "ticker": "AAPL", "stance": "hold", ... },       │
│         { "ticker": "TSLA", "stance": "buy", ... }         │
│       ]}                                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 14. Frontend Displays Results                               │
│     - Tabbed interface for each ticker                      │
│     - Stance, confidence, summary                           │
│     - Key drivers, risks, catalysts                         │
│     - Sources with citations                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Smart Correction System

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Smart Correction Pipeline                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: "Analyze metae Apple and TSLAA"                     │
│     │                                                        │
│     ▼                                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Step 1: Gemini API Call                             │   │
│  │ - Sends query with prompt template                  │   │
│  │ - Requests JSON response                            │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Step 2: Response Parsing                            │   │
│  │ - Extracts JSON from markdown code blocks           │   │
│  │ - Validates structure                               │   │
│  │ - Handles malformed responses                       │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Step 3: Correction Extraction                       │   │
│  │ - Identifies all misspellings                       │   │
│  │ - Maps to correct company names & tickers           │   │
│  │ - Assigns confidence levels                         │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Step 4: Confirmation Message Generation             │   │
│  │ - Creates user-friendly messages                    │   │
│  │ - Includes confidence indicators                    │   │
│  │ - Adds explanations                                 │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│                     ▼                                        │
│  Output: {                                                   │
│    "has_misspellings": true,                                │
│    "corrections": [                                         │
│      { "original": "metae", "ticker": "META", ... },       │
│      { "original": "TSLAA", "ticker": "TSLA", ... }        │
│    ]                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

### Confidence Scoring

| Level | Criteria | Example |
|-------|----------|---------|
| **High** | Clear typo, single obvious match | "matae" → "Meta" |
| **Medium** | Phonetic similarity, multiple possibilities | "microsft" → "Microsoft" |
| **Low** | Ambiguous, significant differences | "amazn" → "Amazon" |

### Error Handling

```python
try:
    result = gemini_api.generate_content(prompt)
except Exception as e:
    logger.error("Gemini API error", error=str(e))
    # Fallback to traditional fuzzy matching
    return fallback_correction(user_input)
```

---

## Multi-Agent System

### Agent Architecture

Each agent follows the **ReAct (Reasoning + Acting)** pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                      Base Agent Class                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  def analyze(ticker: str, query: str) -> AgentResult:       │
│      1. Fetch data from source                              │
│      2. Process with Gemini AI                              │
│      3. Extract structured insights                         │
│      4. Return with citations                               │
│                                                              │
│  Properties:                                                 │
│  - agent_name: str                                          │
│  - data_source: DataSource                                  │
│  - max_iterations: int                                      │
│  - timeout: int                                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

#### 1. News Agent
- **Data Source**: Yahoo Finance News API
- **Analysis**: Sentiment, key events, market reactions
- **Output**: Recent news summary with sentiment scores

#### 2. Price Agent
- **Data Source**: Yahoo Finance Historical Prices
- **Analysis**: Price movements, technical indicators, trends
- **Output**: Price analysis with support/resistance levels

#### 3. Earnings Agent
- **Data Source**: Yahoo Finance Financials
- **Analysis**: EPS, revenue, margins, guidance
- **Output**: Financial health assessment

#### 4. Insider Agent
- **Data Source**: Yahoo Finance Insider Transactions
- **Analysis**: Insider buying/selling patterns
- **Output**: Insider sentiment indicators

#### 5. Patents Agent
- **Data Source**: Yahoo Finance Company Info
- **Analysis**: IP activity, innovation indicators
- **Output**: Innovation assessment

#### 6. Filings Agent
- **Data Source**: Yahoo Finance SEC Filings
- **Analysis**: Recent filings, regulatory changes
- **Output**: Regulatory risk assessment

#### 7. Synthesis Agent
- **Input**: All agent results
- **Analysis**: Holistic view, weighted scoring
- **Output**: Final recommendation with confidence

### Parallel Execution

```python
async def analyze_ticker(ticker: str):
    agents = [NewsAgent(), PriceAgent(), EarningsAgent(), ...]
    
    # Execute agents in parallel
    results = await asyncio.gather(
        *[agent.analyze(ticker) for agent in agents],
        return_exceptions=True
    )
    
    # Synthesis
    synthesis = SynthesisAgent().synthesize(results)
    return synthesis
```

---

## API Design

### RESTful Principles

- **Resource-oriented**: `/api/v1/analyze`
- **HTTP methods**: POST for analysis, GET for health
- **Status codes**: 200 (success), 400 (bad request), 500 (server error)
- **JSON format**: All requests and responses

### Request/Response Models

**AnalysisRequest**:
```python
class AnalysisRequest(BaseModel):
    query: str  # Natural language query
    max_iterations: int = 3
    timeout_seconds: int = 60
    conversation_id: Optional[str] = None
    confirmation_response: Optional[str] = None
```

**AnalysisResponse**:
```python
class AnalysisResponse(BaseModel):
    request_id: str
    query: str
    success: bool
    insights: List[TickerInsight]
    tickers_analyzed: List[str]
    agents_used: List[str]
    total_latency_ms: float
    needs_confirmation: bool = False
    confirmation_prompt: Optional[ConfirmationPrompt] = None
```

### Error Handling

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )
```

---

## Database & State Management

### Current Implementation (Development)

- **In-memory storage**: Python dictionaries
- **TTL**: 30 minutes
- **Cleanup**: Periodic background task

```python
conversations: Dict[str, Conversation] = {}
```

### Production Recommendation

- **Redis**: Distributed state management
- **Benefits**: Persistence, scalability, clustering
- **Migration**: Replace in-memory dict with Redis client

```python
# Production implementation
import redis

redis_client = redis.Redis(host='redis', port=6379)

def store_conversation(conv_id, data):
    redis_client.setex(
        f"conversation:{conv_id}",
        1800,  # 30 minutes TTL
        json.dumps(data)
    )
```

---

## Security Architecture

### API Key Protection

```bash
# Never commit .env
.env
*.env

# Use environment variables
export GEMINI_API_KEY=xxx
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Input Validation

```python
class AnalysisRequest(BaseModel):
    query: constr(min_length=1, max_length=1000)
    max_iterations: conint(ge=1, le=10)
    timeout_seconds: conint(ge=10, le=300)
```

### Docker Security

```dockerfile
# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Read-only filesystem (where possible)
# Minimal base image
FROM python:3.11-slim
```

---

## Deployment Architecture

### Docker Compose Setup

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    restart: unless-stopped
    
  frontend:
    build: ./frontend/stock-research-ui
    ports: ["3000:3000"]
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:3000"]
    restart: unless-stopped
```

### Production Enhancements

1. **Reverse Proxy**: Nginx or Traefik
2. **SSL/TLS**: Let's Encrypt certificates
3. **Load Balancer**: HAProxy or AWS ELB
4. **Monitoring**: Prometheus + Grafana
5. **Logging**: ELK stack or CloudWatch

---

## Performance & Scaling

### Current Performance

- **Average latency**: 3-8 seconds per ticker
- **Concurrent requests**: Supported via async
- **Agent parallelization**: 6 agents per ticker

### Scaling Strategies

#### Horizontal Scaling

```bash
docker-compose up -d --scale backend=3
```

#### Caching

```python
# Cache ticker mappings
@lru_cache(maxsize=10000)
def get_ticker(company_name: str) -> str:
    return ticker_mapper.map(company_name)
```

#### Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze(request: AnalysisRequest):
    ...
```

### Optimization Opportunities

1. **Database connection pooling**
2. **Result caching** (Redis)
3. **CDN for frontend** (CloudFront, Cloudflare)
4. **API response compression** (gzip)
5. **Async database queries** (asyncpg)

---

## Monitoring & Observability

### Logging

```python
import structlog

logger = structlog.get_logger()
logger.info("Analysis started", ticker="AAPL", user_id="123")
```

### Health Checks

```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "stock-research-chatbot"
    }
```

### Metrics (Recommended)

- Request count
- Latency percentiles (p50, p95, p99)
- Error rate
- Agent execution time
- Gemini API latency

---

## Future Enhancements

1. **User Authentication**: JWT-based auth
2. **Persistent Storage**: PostgreSQL for user queries
3. **Real-time Updates**: WebSocket for live data
4. **Advanced Analytics**: Historical trend analysis
5. **Mobile App**: React Native client
6. **API Rate Limiting**: Per-user quotas
7. **Caching Layer**: Redis for frequent queries
8. **Batch Processing**: Analyze multiple portfolios

---

## Conclusion

The Stock Research Chatbot is a production-ready, scalable system built on modern architecture principles. Its modular design allows for easy extension and maintenance, while the multi-agent approach ensures comprehensive analysis.

For questions or contributions, see the main [README.md](./README.md).

---

**Document Version**: 1.0  
**Architecture Version**: 2.1.0  
**Last Updated**: October 24, 2025

