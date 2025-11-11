# 📊 Stock Research Chatbot v3.0

AI-powered multi-agent stock research platform with professional-grade streaming logs, smart spelling correction, comprehensive analysis, and real-time market insights.

[![Production Ready](https://img.shields.io/badge/status-production--ready-green)]()
[![Docker](https://img.shields.io/badge/docker-enabled-blue)]()
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()

---

## 🎯 Overview

The Stock Research Chatbot is a production-grade AI system that provides comprehensive stock analysis using a multi-agent architecture powered by Google Gemini. It features intelligent typo correction, natural language understanding, and parallel research across multiple data sources, now with enhanced user-facing streaming logs for a professional experience.

### Key Features

- **✨ Professional Streaming Logs**: Real-time, user-friendly status updates for each step of the analysis process.
- **🤖 Gemini-Powered Smart Correction**: Automatically detects and corrects misspelled company names with interactive confirmation.
- **🔄 Multi-Misspelling Support**: Handles multiple typos in a single query with a single confirmation step.
- **🎯 Multi-Agent Research**: Specialized agents analyze news, prices, and financials, orchestrated for deep insights.
- **📊 Real-Time Data**: Live market data from Yahoo Finance API.
- **💡 AI-Driven Insights**: Comprehensive investment recommendations with confidence scores.
- **📝 Cited Sources**: All claims backed by URLs and publication dates.
- **🌐 Natural Language**: Accepts both company names and ticker symbols.
- **⚡ Parallel Processing**: Analyzes multiple companies simultaneously.

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

Bot: "I found 2 potential misspellings:
      1. 'metae' -> **Meta Platforms Inc.** (META)
      2. 'TSLAA' -> **Tesla Inc.** (TSLA)

      Did you mean these corrections?"

You: "Yes"

Bot: [Proceeds with analysis of META, AAPL, TSLA]
```

---

## 🏗️ Architecture

For a detailed architecture diagram and explanation, please see **[ARCHITECTURE.md](./ARCHITECTURE.md)**.

---

## 🌊 Code Flow

For a detailed explanation of how the code works and how data flows between files, please see **[CODE_FLOW.md](./CODE_FLOW.md)**.

---

## 📋 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### POST `/analyze`

Analyzes stocks based on a natural language query.

**Request:**
```json
{
  "query": "Analyze AAPL for 1 month",
  "request_id": "optional-uuid"
}
```

**Response (Success):**
```json
{
  "request_id": "uuid",
  "query": "Analyze AAPL for 1 month",
  "success": true,
  "insights": [...],
  "..."
}
```

#### GET `/health`

Returns the health status of the service.

---

## 🧪 Testing

### Backend Unit Tests

```bash
cd backend
pip install -r requirements.txt

# Run all tests
GEMINI_API_KEY=your_key pytest tests/ -v
```

### Postman Integration Tests

Import the collection and environment from the `postman/` directory into Postman to run integration tests against a running server.

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
```

See **`.env.template`** for all available options.

---

## 📁 Project Structure

```
stock-research-chatbot/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture documentation
├── CODE_FLOW.md                       # Detailed code flow explanation
├── docker-compose.yml                 # Docker orchestration
├── .env.template                      # Environment template
│
├── backend/
│   ├── agents/                        # Multi-agent system
│   │   └── yahoo_finance_orchestrator.py
│   ├── app/
│   │   ├── main.py                    # FastAPI app
│   │   ├── api.py                     # API routes
│   │   └── models.py                  # Pydantic models
│   ├── services/
│   │   ├── smart_correction_service.py  # Gemini correction
│   │   ├── conversation_manager.py      # State management
│   │   ├── ticker_mapper.py             # Ticker mapping
│   │   └── log_broadcaster.py           # Professional streaming logs
│   ├── config/
│   │   └── settings.py
│   ├── tools/
│   │   └── yahoo_finance_tool.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── stock-research-ui/
│       ├── src/
│       ├── package.json
│       └── Dockerfile
│
└── postman/
    └── Stock_Research_Chatbot.postman_collection.json
```

---

## 🚀 Deployment

To deploy the application to a production environment, you can use the provided Docker setup. Ensure you have Docker and Docker Compose installed on your server.

1.  **Set Environment Variables**: Create a `.env` file on your server with the production configurations. At a minimum, you need to set `GEMINI_API_KEY` and `CORS_ORIGINS` to your frontend's domain.

2.  **Build and Run**: Use `docker-compose` to build and run the services in detached mode:

    ```bash
    docker-compose up -d --build
    ```

3.  **Verify**: Check the status of the running containers:

    ```bash
    docker-compose ps
    ```

4.  **Access**: The application should now be accessible at your domain.
