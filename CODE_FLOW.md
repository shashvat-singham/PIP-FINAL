# 🌊 Stock Research Chatbot - Code Flow

**Version**: 3.0.0  
**Last Updated**: Nov 10, 2025

---

This document provides a detailed, line-by-line explanation of how data and control flow through the backend of the Stock Research Chatbot. Its purpose is to help developers understand how different components interact to process a user query and generate a comprehensive stock analysis.

## 1. The Request Lifecycle: From Query to Insight

The entire process begins when a user submits a query to the frontend, which then makes a `POST` request to the `/analyze` endpoint in the backend.

**Entry Point**: `backend/app/api.py`

1.  **Request Reception** (lines 40-56):
    The `analyze_stocks` function receives the `AnalysisRequest`, which contains the user's query. A unique `request_id` is generated, and the start time is recorded for latency tracking.

2.  **Log Broadcaster Initialization** (lines 59-67):
    A `LogBroadcaster` instance is created immediately. This is crucial for providing real-time feedback to the user from the very beginning. The first log message, `"📝 Received query..."`, is emitted to the frontend via WebSocket.

3.  **Service Initialization** (lines 69-73):
    The core services are initialized, including the `YahooFinanceOrchestrator`, `TickerMapper`, and `SmartCorrectionService`.

4.  **Smart Correction** (lines 130-212):
    The query is first passed to the `SmartCorrectionService` to check for typos. If misspellings are found, the API returns a `ConfirmationPrompt` to the user and the process pauses until the user confirms the corrections. (See Section 2 for details).

5.  **Ticker Extraction** (lines 215-226):
    If no typos are found, the `TickerMapper` service is used to extract stock tickers (e.g., `AAPL`, `GOOGL`) from the natural language query.

6.  **Orchestrated Analysis** (lines 245-252):
    The validated tickers are passed to the `YahooFinanceOrchestrator.analyze()` method. This is the main workhorse of the application, where the multi-agent analysis takes place. The `log_broadcaster` instance is passed along to provide streaming updates during this long-running process.

    -   **File**: `backend/agents/yahoo_finance_orchestrator.py`
    -   **Function**: `analyze()` (line 300)

7.  **Response Formatting** (lines 255-261):
    Once the orchestrator completes its analysis and returns the `TickerInsight` objects, the `format_analysis_response` utility is used to structure the final JSON response.

8.  **Final Response** (line 267):
    The FastAPI route returns the complete `AnalysisResponse` to the client, which includes the investment insights, sources, and performance metrics.

## 2. The Smart Correction Flow

This flow is triggered if the user's query contains potential misspellings of company names.

**Entry Point**: `backend/app/api.py`, `analyze_stocks` function

1.  **Typo Detection** (lines 131-139):
    The `smart_correction_service.detect_and_correct_multiple()` method is called. This service sends a specially crafted prompt to the Gemini API, asking it to identify and correct any company names in the user's query.

    -   **File**: `backend/services/smart_correction_service.py`

2.  **Confirmation Prompt Generation** (lines 141-206):
    If the Gemini API returns corrections, the backend constructs a `ConfirmationPrompt`. This prompt contains a user-friendly message asking for confirmation and includes all suggested corrections in a single message for a better user experience.

3.  **User Confirmation Handling** (lines 79-95):
    When the user responds to the confirmation prompt (e.g., by clicking "Yes"), the frontend sends a new request to the `/analyze` endpoint, this time including the `conversation_id` and a `confirmation_response`. The `ConversationManager` processes this response. If confirmed, the corrected tickers are extracted and used for the analysis.

## 3. Orchestration and Agent Execution

This is where the deep analysis happens. The orchestrator manages a pool of agents, each responsible for a specific piece of research.

**Entry Point**: `backend/agents/yahoo_finance_orchestrator.py`, `analyze` function (line 300)

1.  **Parallel Task Creation** (line 356):
    The `analyze` method creates a list of asynchronous tasks, where each task is a call to the `_analyze_ticker()` method for a single stock ticker. `asyncio.gather()` is used to run all these tasks concurrently.

2.  **Single Ticker Analysis** (`_analyze_ticker` method, line 47):
    For each ticker, this method executes a series of steps, with the `log_broadcaster` providing updates at each stage:

    -   **Fetch Company Info** (lines 73-82): Gathers basic information like company name and market cap using `YahooFinanceTool`.
    -   **Fetch News** (lines 102-111): The "News Agent" fetches recent articles.
    -   **Analyze News** (line 130): `GeminiService` summarizes the news and determines sentiment.
    -   **Fetch Price Data** (lines 152-161): The "Price Agent" gets historical price data.
    -   **Analyze Technicals** (line 170): `GeminiService` identifies support/resistance levels.
    -   **Fetch Financials** (line 199): Gathers key financial metrics.
    -   **Synthesize Analysis** (lines 202-217): The "Synthesis Agent" is the final and most critical step. It takes all the data gathered by the other agents and uses `GeminiService.generate_investment_analysis()` to create the final recommendation, rationale, and key insights.

3.  **Result Aggregation** (lines 357-367):
    Back in the `analyze` method, `asyncio.gather()` returns the results from all the `_analyze_ticker` tasks. The code filters out any exceptions that may have occurred during an individual ticker's analysis and collects the valid `TickerInsight` objects.

## 4. Streaming Log Flow

The professional, user-facing logs are streamed to the frontend via a WebSocket connection, managed by the `LogBroadcaster`.

**Entry Point**: `backend/services/log_broadcaster.py`

1.  **Connection Management**:
    The `ConnectionManager` class (in `backend/app/websocket.py`) is responsible for handling WebSocket connections. When a client connects, it is associated with its unique `request_id`.

2.  **Emitting Logs** (line 44):
    The `LogBroadcaster.emit()` method is the core of the logging system. It constructs a JSON log event containing a timestamp, message, and other details.

3.  **Broadcasting** (line 76):
    The `emit` method calls `self.connection_manager.broadcast()`, which finds the correct client WebSocket connection based on the `request_id` and sends the JSON log event to the frontend.

4.  **User-Facing Methods** (lines 87-268):
    The `LogBroadcaster` class contains many high-level, descriptive methods like `query_received()`, `extracting_tickers()`, `fetching_news()`, and `synthesizing_analysis()`. These methods are called from the `api.py` and `yahoo_finance_orchestrator.py` files at the appropriate points in the code flow. They abstract away the details of creating the log message, making the main application code cleaner and more readable.

    **Example**: In `yahoo_finance_orchestrator.py`, instead of a generic log, a specific, user-friendly message is sent:

    ```python
    # backend/agents/yahoo_finance_orchestrator.py: line 102
    if self.log_broadcaster:
        await self.log_broadcaster.fetching_news(ticker, company_name)
    ```

This structured and detailed flow ensures that the application is not only powerful but also transparent and maintainable.
