# Stock Research Agentic Chatbot

A production-grade AI-powered stock research platform that provides comprehensive analysis using multi-agent architecture, real-time market data, and intelligent insights for informed investment decisions.

## 🚀 Features

### Core Capabilities
- **Flexible Input Recognition**: Accepts both company names (e.g., "Apple", "Microsoft") and tickers (e.g., "AAPL", "MSFT")
- **🆕 Gemini-Powered Smart Correction**: Uses AI to detect and correct misspelled company names (e.g., "matae" → "Meta") with interactive confirmation
- **Intelligent Spelling Detection**: Automatically detects misspelled company names with interactive confirmation
- **Multi-Company Analysis**: Analyzes multiple companies in parallel with separate, clearly labeled results
- **Real-Time Data**: Genuine market data from Yahoo Finance API
- **AI-Powered Analysis**: Multi-agent system using Google Gemini 2.5 Flash
- **Grounded Insights**: All claims backed by citations with source URLs and publication dates
- **Professional JSON API**: All financial metrics formatted to exactly 2 decimal places

### Agent Architecture
- **News Agent**: Fetches and analyzes recent news from Yahoo Finance
- **Price Agent**: Analyzes price movements and technical indicators
- **Earnings Agent**: Processes earnings reports and financial statements
- **Insider Agent**: Tracks insider trading and ownership changes
- **Patents Agent**: Monitors patent filings and IP developments
- **Filings Agent**: Analyzes SEC filings and regulatory documents
- **Synthesis Agent**: Synthesizes all data to generate investment recommendations

## 📋 Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Google Gemini API Key** - [Get API Key](https://ai.google.dev/)
- **Docker** (optional) - [Download](https://www.docker.com/)

## 🔧 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd stock-research-chatbot

# 2. Configure environment
cp .env.template .env
# Edit .env and add your GEMINI_API_KEY

# 3. Build and run with Docker Compose
docker-compose up --build

# Access the application
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend UI: http://localhost:3000
```

### Option 2: Local Development

```bash
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt

# 2. Configure environment
cp ../.env.template ../.env
# Edit .env and add your GEMINI_API_KEY

# 3. Start the backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. In a new terminal, install and start frontend
cd frontend/stock-research-ui
npm install
npm run dev

# Access the application
# Backend API: http://localhost:8000
# Frontend UI: http://localhost:3000
```

## 💡 Usage Examples

### Example 1: Company Names
```
Query: "Analyze Apple Microsoft and Meta for 1 month"
Result: Analyzes AAPL, MSFT, and META with separate insights for each
```

### Example 2: Mixed Input
```
Query: "Compare NVDA AMD and Intel for AI datacenter demand"
Result: Analyzes NVDA, AMD, and INTC with focus on AI datacenter market
```

### Example 3: Spelling Correction
```
Query: "Analyze Microsft for 6 months"
Response: "Did you mean Microsoft Corporation (MSFT)?"
User: "Yes"
Result: Proceeds with MSFT analysis
```

### Example 4: Interactive Clarification
```
Query: "Analyze XYZ company"
Response: "I couldn't recognize 'XYZ'. Could you please provide the stock ticker or full company name?"
User: "Apple Inc."
Result: Proceeds with AAPL analysis
```

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Framework: FastAPI (Python 3.11)
- AI/ML: Google Gemini 2.5 Flash
- Agent Framework: LangGraph with ReAct primitives
- Vector DB: ChromaDB
- Data Sources: Yahoo Finance API, SEC EDGAR, Web Search
- Logging: Structlog with JSONL traces

**Frontend:**
- Framework: React 18
- Styling: Tailwind CSS
- State Management: React Hooks
- HTTP Client: Axios

### Multi-Agent Workflow

```
User Query
    ↓
Ticker Mapper (Company Name → Ticker)
    ↓
Parallel Agent Execution
    ├── News Agent
    ├── Price Agent
    ├── Earnings Agent
    ├── Insider Agent
    ├── Patents Agent
    └── Filings Agent
    ↓
Synthesis Agent (Gemini AI)
    ↓
Investment Recommendation
```

### ReAct Loop
Each agent follows the ReAct pattern:
1. **Ask/Think**: Determine what information is needed
2. **Act**: Execute tools to fetch data
3. **Observe**: Process results
4. **Repeat**: Continue until stop conditions (MAX_ITERS=3 or budget/timeout)

## 📖 API Documentation

### Analyze Stocks
```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "query": "Analyze Apple Microsoft and Meta for 1 month",
  "max_iterations": 3,
  "timeout_seconds": 60
}
```

### Response Format
```json
{
  "request_id": "uuid",
  "query": "Analyze Apple Microsoft and Meta for 1 month",
  "insights": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "current_price": 175.43,
      "pe_ratio": 28.45,
      "market_cap": 2890.32,
      "stance": "buy",
      "confidence": "high",
      "summary": "Strong fundamentals...",
      "rationale": "Apple demonstrates...",
      "key_drivers": ["AI integration", "Services growth"],
      "risks": ["Regulatory pressure", "China exposure"],
      "catalysts": ["iPhone 16 launch", "Vision Pro expansion"],
      "sources": [
        {
          "url": "https://...",
          "title": "Apple announces...",
          "published_at": "2025-10-20T10:00:00Z"
        }
      ]
    }
  ],
  "total_latency_ms": 15234.56,
  "tickers_analyzed": ["AAPL", "MSFT", "META"],
  "agents_used": ["news", "price", "synthesis"],
  "success": true
}
```

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

## 📊 Data Accuracy

All stock data is **genuine and real-time**, sourced directly from Yahoo Finance:
- ✅ Current prices match Yahoo Finance exactly
- ✅ P/E ratios and financial metrics are accurate
- ✅ No dummy or fallback data
- ✅ Real-time updates
- ✅ Works for any valid ticker symbol
- ✅ All numeric values formatted to exactly 2 decimal places

## 🔒 Security

- ✅ API keys stored in `.env` (never in code)
- ✅ `.gitignore` configured to exclude sensitive files
- ✅ `.dockerignore` optimized for minimal image size
- ✅ CORS properly configured
- ✅ Input validation on all endpoints
- ✅ No file uploads allowed
- ✅ Rate limiting implemented
- ✅ Non-root user in Docker containers
- ✅ Health checks for container orchestration

## 📁 Project Structure

```
stock-research-chatbot/
├── backend/
│   ├── agents/              # AI agents for research
│   │   ├── orchestrator.py
│   │   ├── yahoo_finance_orchestrator.py
│   │   ├── news_agent.py
│   │   ├── price_agent.py
│   │   └── synthesis_agent.py
│   ├── app/                 # FastAPI application
│   │   ├── main.py
│   │   ├── api.py
│   │   └── models.py
│   ├── services/            # Business logic services
│   │   ├── ticker_mapper.py
│   │   ├── conversation_manager.py
│   │   └── gemini_service.py
│   ├── tools/               # Data fetching tools
│   │   ├── yahoo_finance_tool.py
│   │   ├── sec_edgar_tool.py
│   │   └── web_search_tool.py
│   ├── utils/               # Utility modules
│   │   ├── formatters.py
│   │   └── api_client.py
│   ├── config/              # Configuration
│   │   └── settings.py
│   ├── tests/               # Test suite
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── stock-research-ui/   # React application
│       ├── src/
│       │   ├── App.jsx
│       │   └── components/
│       ├── package.json
│       └── vite.config.js
├── .env.template            # Environment template
├── .env                     # Environment variables (gitignored)
├── .dockerignore            # Docker ignore rules
├── Dockerfile               # Backend Docker image
├── docker-compose.yml       # Multi-container orchestration
├── README.md                # This file
└── pytest.ini               # Pytest configuration
```

## 🚀 Deployment

### Production Deployment

```bash
# 1. Set production environment variables
export ENVIRONMENT=production
export GEMINI_API_KEY=your_production_key

# 2. Build production images
docker-compose build

# 3. Run in detached mode
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Scale if needed
docker-compose up -d --scale backend=3
```

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_ITERATIONS=3
TIMEOUT_SECONDS=60
```

## 🔍 Observability

### Logging
- Structured logging with Structlog
- JSONL traces for all agent steps
- Includes: steps, tools, URLs, timestamps, latencies
- Log files stored in `logs/` directory

### Metrics
- Request latency tracking
- Agent execution times
- Success/failure rates
- Source citation counts

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Check via Docker
docker-compose ps
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Yahoo Finance** for market data
- **Google Gemini** for AI capabilities
- **FastAPI** and **React** communities
- **SEC EDGAR** for regulatory filings
- **LangGraph** for agent orchestration

## 📞 Support

For issues and questions:
- Check the [API Documentation](http://localhost:8000/docs)
- Review logs in `logs/` directory
- Open an issue on GitHub

---

**Built with ❤️ using LangGraph, Gemini 2.5 Flash, and Yahoo Finance**

**🚀 Ready to make informed investment decisions with AI!**

