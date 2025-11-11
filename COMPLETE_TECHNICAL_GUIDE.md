# Stock Research Chatbot 


---

## 1. Introduction

This document provides a comprehensive, end-to-end technical explanation of the Stock Research Chatbot. It is designed for senior engineers and technical managers who require a deep understanding of the entire codebase, from system startup to the final API response. We will trace the flow of data and control through every major component, with direct references to file paths, functions, and line numbers to illustrate how the system is linked together.

---

## 2. System Startup and Configuration

The application starts with the FastAPI backend, which is configured to be flexible and environment-aware.

### 2.1. Application Entry Point

The entire backend application is initialized and run from `main.py`.

-   **File**: `backend/app/main.py`

```python
# backend/app/main.py: line 57
app = FastAPI(
    title="Stock Research Chatbot API",
    # ...
    lifespan=lifespan
)

# backend/app/main.py: line 74
app.include_router(api_router, prefix="/api/v1")

# backend/app/main.py: line 77
@app.websocket("/ws/{request_id}")
# ...
```

**Explanation**:

1.  A `FastAPI` application instance is created. The `lifespan` context manager (lines 42-54) handles startup and shutdown events, such as logging the application environment.
2.  The API routes defined in `api.py` are included with a `/api/v1` prefix.
3.  A WebSocket endpoint is established at `/ws/{request_id}` to handle real-time log streaming.

### 2.2. Configuration Management

All configuration is managed through Pydantic settings, allowing for easy environment variable overrides.

-   **File**: `backend/config/settings.py`

```python
# backend/config/settings.py: line 9
class Settings(BaseSettings):
    gemini_api_key: Optional[str] = None
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    
    model_config = SettingsConfigDict(env_file=".env", ...)

# backend/config/settings.py: line 38
def get_settings() -> Settings:
    return settings
```

**Code Linkage**:

-   Anywhere in the application that configuration is needed (e.g., in `main.py` or `gemini_service.py`), the `get_settings()` function is called. This provides a singleton `Settings` object with all the loaded environment variables, ensuring consistent configuration across the app.

---

## 3. The Full Request Lifecycle (End-to-End)

This section traces a user query like "Analyze Apple and Microsoft" from the frontend through every backend component.

### Step 1: Frontend - User Submits Query

The process begins in the React UI.

-   **File**: `frontend/stock-research-ui/src/App.jsx`

When the user types a query and clicks "Analyze", the `handleAnalysis` function is called. This function makes a `POST` request to the backend.

### Step 2: Backend - API Route Receives Request

The request arrives at the main analysis endpoint in `api.py`.

-   **File**: `backend/app/api.py`

```python
# backend/app/api.py: line 40
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stocks(request: AnalysisRequest) -> AnalysisResponse:
    request_id = request.request_id or str(uuid.uuid4())
    start_time = time.time()
    
    # ... (Services are initialized here)
```

**Explanation**:

-   The `analyze_stocks` function is the main entry point for any analysis query.
-   It generates a unique `request_id` which is critical for tracking this specific request and for the WebSocket connection.

### Step 3: Real-time Logging is Initialized

Immediately, the backend prepares to send real-time updates.

-   **File**: `backend/app/api.py`

```python
# backend/app/api.py: line 60
connection_manager = get_connection_manager()
log_broadcaster = create_log_broadcaster(request_id, connection_manager)

await log_broadcaster.query_received(request.query)
```

**Code Linkage**:

1.  **`api.py:60`**: `get_connection_manager()` is called.
    -   **Links to**: `backend/app/websocket.py` (line 131), which returns the global `ConnectionManager` instance responsible for all WebSocket connections.
2.  **`api.py:61`**: `create_log_broadcaster()` is called.
    -   **Links to**: `backend/services/log_broadcaster.py` (line 271), which returns a new `LogBroadcaster` instance, associating it with the `request_id`.
3.  **`api.py:64`**: The first log is emitted. The `log_broadcaster` will use the `connection_manager` to send this message to any client that connects to the WebSocket with the matching `request_id`.

### Step 4: Frontend Connects to WebSocket

Back on the frontend, the `request_id` from the initial HTTP response triggers the WebSocket connection.

-   **File**: `frontend/stock-research-ui/src/hooks/useWebSocketLogs.js`

```javascript
// useWebSocketLogs.js: line 32
const wsUrl = `ws://localhost:8000/ws/${requestId}`;
const ws = new WebSocket(wsUrl);
```

**Code Linkage**:

-   This URL targets the endpoint defined in `backend/app/main.py` at line 77. The `ConnectionManager` then handles this new connection, adding it to the set of clients listening for logs for this `request_id`.

### Step 5: Ticker Extraction and Smart Correction

The backend now needs to figure out which stocks to analyze.

-   **File**: `backend/app/api.py`

```python
# backend/app/api.py: line 71
ticker_mapper = get_ticker_mapper()
# ...

# backend/app/api.py: line 215
tickers, unresolved_names = ticker_mapper.extract_tickers_from_query(query)
```

**Code Linkage**:

1.  **`api.py:71`**: `get_ticker_mapper()` is called.
    -   **Links to**: `backend/services/ticker_mapper.py` (line 355), which returns the global `TickerMapper` instance.
2.  **`api.py:215`**: `extract_tickers_from_query()` is called.
    -   **Links to**: `backend/services/ticker_mapper.py` (line 246). This function uses a combination of regex and a large dictionary (`COMPANY_TO_TICKER`) to find all tickers and company names in the query.

If there are `unresolved_names`, the `SmartCorrectionService` is used.

-   **File**: `backend/app/api.py`

```python
# backend/app/api.py: line 131
corrections = await smart_correction_service.detect_and_correct_multiple(
    unresolved_names, request.query
)
```

**Code Linkage**:

-   **`api.py:131`**: This calls the correction service.
    -   **Links to**: `backend/services/smart_correction_service.py`. This service constructs a prompt and sends it to the Gemini API to get spelling corrections for the unresolved names.

### Step 6: The Orchestrator Takes Over

Once tickers are finalized, the main analysis begins.

-   **File**: `backend/app/api.py`

```python
# backend/app/api.py: line 245
results = await orchestrator.analyze(
    query=request.query,
    tickers=tickers,
    log_broadcaster=log_broadcaster,
)
```

**Code Linkage**:

-   **`api.py:245`**: The `analyze` method of the `YahooFinanceOrchestrator` is called.
    -   **Links to**: `backend/agents/yahoo_finance_orchestrator.py` (line 300). This is the heart of the application. It takes the list of tickers and orchestrates the entire data gathering and analysis process.

### Step 7: Parallel Agent Execution

The orchestrator runs analysis for each ticker in parallel.

-   **File**: `backend/agents/yahoo_finance_orchestrator.py`

```python
# yahoo_finance_orchestrator.py: line 356
tasks = [self._analyze_ticker(ticker, query, max_iterations) for ticker in tickers]
insights = await asyncio.gather(*tasks, return_exceptions=True)
```

**Explanation**:

-   `asyncio.gather` is used to run the `_analyze_ticker` method for all tickers concurrently. This is a massive performance win.

Inside `_analyze_ticker`, a sequence of steps are executed, each involving a **Tool** and a **Service**.

**Example Step: Fetching and Analyzing News**

```python
# yahoo_finance_orchestrator.py: line 102
await self.log_broadcaster.fetching_news(ticker, company_name)
news_articles = self.yahoo_tool.get_news(ticker, limit=10)

# ...

# yahoo_finance_orchestrator.py: line 130
news_summary = self.gemini_service.summarize_news(ticker, news_articles)
```

**Code Linkage**:

1.  **`line 103`**: `self.yahoo_tool.get_news()` is called.
    -   **Links to**: `backend/tools/yahoo_finance_tool.py` (line 153). This tool is responsible for all communication with the Yahoo Finance API. It calls the Manus API Hub to get the data.
2.  **`line 130`**: `self.gemini_service.summarize_news()` is called.
    -   **Links to**: `backend/services/gemini_service.py` (line 34). This service takes the raw news articles, constructs a detailed prompt, and sends it to the Gemini API to get a structured JSON summary and sentiment analysis.

This **Tool -> Service -> Log** pattern is repeated for price data, financial metrics, and the final synthesis.

### Step 8: Final Synthesis

After all individual data points are gathered, the `Synthesis Agent` (which is part of the orchestrator's logic) creates the final investment thesis.

-   **File**: `backend/agents/yahoo_finance_orchestrator.py`

```python
# yahoo_finance_orchestrator.py: line 209
investment_analysis = self.gemini_service.generate_investment_analysis(
    ticker=ticker,
    company_name=company_name,
    news_summary=news_summary,
    price_data=price_data,
    financial_metrics=financials,
)
```

**Code Linkage**:

-   This is the most important call to the AI. It links to `backend/services/gemini_service.py` at line 106. The prompt for this function is extremely detailed, instructing the AI to act like a senior analyst and provide a rationale, key drivers, risks, catalysts, and a final stance.

### Step 9: Formatting and Returning the Final Response

Once `asyncio.gather` completes, the `api.py` route receives the list of `TickerInsight` objects.

-   **File**: `backend/app/api.py`

```python
# backend/app/api.py: line 255
response = format_analysis_response(
    request_id=request_id,
    query=request.query,
    insights=valid_results,
    # ...
)
return response
```

**Code Linkage**:

-   **`api.py:255`**: `format_analysis_response` is called.
    -   **Links to**: `backend/utils/formatters.py`. This utility function takes all the results and structures them into the final `AnalysisResponse` Pydantic model, which is then automatically serialized to JSON by FastAPI and sent back to the client.

---

## 4. Data Models

The entire system relies on strongly-typed Pydantic models for data integrity.

-   **File**: `backend/app/models.py`

-   **`AnalysisRequest`**: Defines the structure of the incoming request from the frontend.
-   **`TickerInsight`**: A rich object that holds all the analyzed data for a single stock, from market cap to the final investment rationale.
-   **`AnalysisResponse`**: Defines the final JSON structure returned to the client. By using this as the `response_model` in the FastAPI route, we get automatic data validation and serialization.

This end-to-end flow, with its clear separation of concerns (API, Services, Tools, Orchestrator) and strong data typing, creates a system that is robust, scalable, and easy to maintain. Every component has a specific job, and the linkages between them are explicit and traceable.
