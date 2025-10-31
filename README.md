# 📊 Stock Research Chatbot v2.1

AI-powered multi-agent stock research platform with smart spelling correction, comprehensive analysis, and real-time market insights.

[![Production Ready](https://img.shields.io/badge/status-production--ready-green)]()
[![Docker](https://img.shields.io/badge/docker-enabled-blue)]()
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()

---

## 🎯 Overview

The Stock Research Chatbot is a production-grade AI system that provides comprehensive stock analysis using a multi-agent architecture powered by Google Gemini 2.5 Flash. It features intelligent typo correction, natural language understanding, and parallel research across multiple data sources.

### Key Features

- **🤖 Gemini-Powered Smart Correction**: Automatically detects and corrects misspelled company names with interactive confirmation
- **🔄 Multi-Misspelling Support**: Handles multiple typos in a single query with sequential confirmation
- **🎯 Multi-Agent Research**: 6 specialized agents analyze news, prices, earnings, insider trading, patents, and SEC filings
- **📊 Real-Time Data**: Live market data from Yahoo Finance API
- **💡 AI-Driven Insights**: Comprehensive investment recommendations with confidence scores
- **📝 Cited Sources**: All claims backed by URLs and publication dates
- **🌐 Natural Language**: Accepts both company names and ticker symbols
- **⚡ Parallel Processing**: Analyzes multiple companies simultaneously

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# 1. Clone and navigate
git clone <repository-url>
cd stock-research-chatbot

# 2. Configure environment
cp .env.template .env
nano .env  # Add your GEMINI_API_KEY

# 3. Start services
docker-compose up --build

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend Setup

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp ../.env.template ../.env
# Add your GEMINI_API_KEY to .env

# Run backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend/stock-research-ui
npm install
npm run dev
# Access at http://localhost:5173
```

---

## 📖 Usage Examples

### Simple Analysis

```
"Analyze AAPL for 1 month"
```

### Multiple Companies

```
"Compare AAPL, MSFT, and GOOGL"
```

### With Typos (Smart Correction)

```
Input: "Analyze metae Apple and TSLAA"

Bot: "I found 2 potential misspellings. Let's confirm them one by one.
      Did you mean Meta Platforms Inc. (META)?"
      
You: "Yes"

Bot: "Did you mean Tesla Inc. (TSLA)?"

You: "Yes"

Bot: [Proceeds with analysis of META, AAPL, TSLA]
```

---

## 🏗️ Architecture

For detailed architecture documentation, see **[ARCHITECTURE.md](./ARCHITECTURE.md)**

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + Vite)                    │
│  - Query Input  - Confirmation Dialogs  - Results Display   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Smart Correction Service (Gemini AI)               │   │
│  │  - Multi-misspelling detection                      │   │
│  │  - Sequential confirmation                          │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Multi-Agent Orchestrator                           │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │   │
│  │  │  News  │ │ Price  │ │Earnings│ │Insider │       │   │
│  │  │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │       │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘       │   │
│  │  ┌────────┐ ┌────────┐ ┌─────────────────┐         │   │
│  │  │Patents │ │Filings │ │  Synthesis      │         │   │
│  │  │ Agent  │ │ Agent  │ │  Agent          │         │   │
│  │  └────────┘ └────────┘ └─────────────────┘         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────┐  ┌──────────────┐
│Yahoo Finance │  │  Gemini  │  │   Ticker     │
│     API      │  │   API    │  │  Database    │
└──────────────┘  └──────────┘  └──────────────┘
```

---

## 📋 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### POST `/analyze`

Analyzes stocks based on natural language query.

**Request:**
```json
{
  "query": "Analyze AAPL for 1 month",
  "max_iterations": 3,
  "timeout_seconds": 60,
  "conversation_id": "optional-uuid",
  "confirmation_response": "Yes"
}
```

**Response (Success):**
```json
{
  "request_id": "uuid",
  "query": "Analyze AAPL for 1 month",
  "success": true,
  "insights": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "stance": "buy",
      "confidence": "high",
      "summary": "Strong buy recommendation...",
      "rationale": "Apple shows strong fundamentals...",
      "key_drivers": ["iPhone sales growth", "Services revenue"],
      "risks": ["Regulatory challenges", "Supply chain"],
      "catalysts": ["AI integration", "New products"],
      "current_price": 175.43,
      "market_cap": 2750000000000.00,
      "pe_ratio": 28.50,
      "sources": [...]
    }
  ],
  "tickers_analyzed": ["AAPL"],
  "agents_used": ["news", "price", "earnings", "synthesis"],
  "total_latency_ms": 5234.56
}
```

**Response (Confirmation Needed):**
```json
{
  "request_id": "uuid",
  "success": false,
  "needs_confirmation": true,
  "confirmation_prompt": {
    "type": "confirmation",
    "message": "Did you mean Meta Platforms Inc. (META)?",
    "suggestion": {
      "original_input": "metae",
      "corrected_name": "Meta Platforms Inc.",
      "ticker": "META",
      "confidence": "high",
      "explanation": "Detected likely misspelling"
    },
    "conversation_id": "uuid"
  }
}
```

#### GET `/health`

Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T10:30:00Z",
  "service": "stock-research-chatbot"
}
```

---

## 🧪 Testing

### Backend Unit Tests

```bash
cd backend
pip install -r requirements.txt

# Run all tests
GEMINI_API_KEY=your_key pytest tests/ -v

# Run specific test
GEMINI_API_KEY=your_key pytest tests/test_smart_correction.py -v

# With coverage
GEMINI_API_KEY=your_key pytest tests/ --cov=backend
```

### Postman Integration Tests

```bash
# Import collection and environment from postman/ directory
# Or use Newman CLI:

npm install -g newman
newman run postman/Stock_Research_Chatbot.postman_collection.json \
  -e postman/Stock_Research_Chatbot.postman_environment.json
```

See **[postman/POSTMAN_TESTING_GUIDE.md](./postman/POSTMAN_TESTING_GUIDE.md)** for detailed testing instructions.

---

## 🔧 Configuration

### Environment Variables

Required:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional:
```env
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
MAX_CONCURRENT_AGENTS=6
REQUEST_TIMEOUT=60
CONVERSATION_TTL=1800
```

See **[.env.template](./.env.template)** for all available options.

---

## 📁 Project Structure

```
stock-research-chatbot/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture documentation
├── docker-compose.yml                 # Docker orchestration
├── .env.template                      # Environment template
│
├── backend/
│   ├── agents/                        # Multi-agent system
│   │   ├── base_agent.py
│   │   ├── news_agent.py
│   │   ├── price_agent.py
│   │   ├── earnings_agent.py
│   │   ├── insider_agent.py
│   │   ├── patents_agent.py
│   │   ├── filings_agent.py
│   │   ├── synthesis_agent.py
│   │   └── yahoo_finance_orchestrator.py
│   ├── app/
│   │   ├── main.py                    # FastAPI app
│   │   ├── api.py                     # API routes
│   │   └── models.py                  # Pydantic models
│   ├── services/
│   │   ├── smart_correction_service.py  # Gemini correction
│   │   ├── conversation_manager.py      # State management
│   │   └── ticker_mapper.py             # Ticker mapping
│   ├── config/
│   │   └── settings.py
│   ├── utils/
│   │   └── formatters.py
│   ├── tests/
│   │   └── test_smart_correction.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── stock-research-ui/
│       ├── src/
│       │   ├── App.jsx                # Main component
│       │   ├── components/
│       │   └── main.jsx
│       ├── package.json
│       ├── Dockerfile
│       └── nginx.conf
│
└── postman/
    ├── Stock_Research_Chatbot.postman_collection.json
    ├── Stock_Research_Chatbot.postman_environment.json
    └── POSTMAN_TESTING_GUIDE.md
```

---

## 🚀 Deployment

### Production Deployment

```bash
# 1. Set environment variables
export GEMINI_API_KEY=your_key
export ENVIRONMENT=production
export CORS_ORIGINS=https://yourdomain.com

# 2. Build and run
docker-compose up -d --build

# 3. Verify
docker-compose ps
docker-compose logs -f
```

### Scaling

```bash
# Scale backend replicas
docker-compose up -d --scale backend=3
```

### Health Monitoring

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Frontend health
curl http://localhost:3000

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 🐛 Troubleshooting

### Issue: Smart correction not working

**Solution:**
```bash
# Check if GEMINI_API_KEY is set
echo $GEMINI_API_KEY

# Check backend logs
docker-compose logs backend | grep GEMINI
```

### Issue: Frontend can't connect to backend

**Solution:**
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check CORS settings in `backend/app/main.py`
- Ensure ports 3000 and 8000 are not blocked

### Issue: Docker build fails

**Solution:**
```bash
# Clean Docker cache
docker-compose down
docker system prune -a
docker-compose up --build
```

### Issue: "Internal Server Error" after confirmation

**Solution:**
- Check backend logs: `docker-compose logs backend`
- Verify GEMINI_API_KEY is valid
- Ensure conversation hasn't expired (30-minute TTL)

---

## 📊 Performance

- **Average Response Time**: 3-8 seconds per ticker
- **Smart Correction Overhead**: +500-1000ms (only when misspelling detected)
- **Concurrent Requests**: Supported
- **Conversation TTL**: 30 minutes
- **Max Concurrent Agents**: 6 (configurable)

---

## 🔒 Security

- **API Key Protection**: Never commit `.env` to version control
- **CORS Configuration**: Configure allowed origins for production
- **Non-root Containers**: Docker containers run as non-root users
- **Input Validation**: All inputs validated using Pydantic models
- **Rate Limiting**: Implement in production (not included by default)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Support

- **Documentation**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed technical documentation
- **Testing Guide**: See [postman/POSTMAN_TESTING_GUIDE.md](./postman/POSTMAN_TESTING_GUIDE.md)
- **Issues**: Open an issue on GitHub
- **API Docs**: http://localhost:8000/docs (when running)

---

## 🙏 Acknowledgments

- **Google Gemini AI** - Smart correction and analysis
- **Yahoo Finance** - Market data
- **FastAPI** - Backend framework
- **React + Vite** - Frontend framework

---

**Version**: 2.1.0  
**Status**: ✅ Production Ready  
**Last Updated**: October 24, 2025

---

## 📚 Additional Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system architecture and design
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and changes
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Detailed deployment instructions
- **[postman/POSTMAN_TESTING_GUIDE.md](./postman/POSTMAN_TESTING_GUIDE.md)** - API testing guide

