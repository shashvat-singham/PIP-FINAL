# 🏗️ Stock Research Chatbot - Architecture

**Version**: 3.0.0  
**Last Updated**: Nov 10, 2025

---

## 1. System Overview

The Stock Research Chatbot is a cloud-native, AI-powered application designed to provide real-time, comprehensive stock analysis. It leverages a microservices-oriented architecture with a multi-agent system at its core, enabling parallel data gathering and analysis to deliver timely and accurate investment insights.

### Core Technologies

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React (Vite) | Modern, responsive user interface with real-time log streaming. |
| **Backend** | FastAPI (Python 3.11) | High-performance, asynchronous API for orchestration and analysis. |
| **AI Engine** | Google Gemini | Powers smart typo correction, sentiment analysis, and data synthesis. |
| **Data Source** | Yahoo Finance API | Provides real-time market data, news, and financial statements. |
| **Containerization** | Docker & Docker Compose | Ensures consistent, scalable, and isolated deployment environments. |
| **Real-time Comms** | WebSocket | Streams professional, user-facing logs from backend to frontend. |

### Architectural Principles

- **Modularity & Decoupling**: The system is divided into a frontend, a backend, and a set of specialized agents. This separation of concerns allows for independent development, scaling, and maintenance.
- **Asynchronous & Non-Blocking**: The backend is built with `asyncio` and FastAPI to handle concurrent requests and long-running analysis tasks efficiently without blocking the server.
- **Scalability**: The containerized setup allows for horizontal scaling of the backend service to handle increased load.
- **User-Centric Design**: Features like smart typo correction and professional streaming logs are designed to create a smooth and informative user experience.

---

## 2. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph User Interface
        A[React Frontend] -->|HTTP/WebSocket| B
    end

    subgraph Backend Services (FastAPI)
        B(API Gateway) --> C{Smart Correction}
        C -->|Corrected Query| D(Orchestrator)
        B -->|WebSocket| E(Log Broadcaster)
        D --> E
    end

    subgraph AI & Data Agents
        D --> F[News Agent]
        D --> G[Price Agent]
        D --> H[Financials Agent]
        D --> I[Synthesis Agent]
    end

    subgraph External Services
        F --> J[Yahoo Finance News]
        G --> K[Yahoo Finance Price Data]
        H --> L[Yahoo Finance Financials]
        C --> M[Gemini API]
        I --> M
    end

    style A fill:#cde4ff
    style B fill:#d8b4fe
    style E fill:#d8b4fe
    style D fill:#fecdd3
    style F fill:#fef08a
    style G fill:#fef08a
    style H fill:#fef08a
    style I fill:#fef08a
```

---

## 3. Component Breakdown

### 3.1. Frontend (React + Vite)

-   **Responsibilities**: Renders the user interface, captures user queries, establishes a WebSocket connection to receive real-time logs, and displays the final analysis results.
-   **Key Components**:
    -   `App.jsx`: The main application component that manages state.
    -   `useWebSocketLogs.js`: A custom hook to handle WebSocket communication for streaming logs.
    -   **UI Components**: A library of reusable components for displaying data, charts, and user feedback.

### 3.2. Backend (FastAPI)

-   **API Gateway (`api.py`)**: The entry point for all client requests. It handles HTTP routes, validates incoming data (Pydantic models), and initiates the analysis process.
-   **Log Broadcaster (`log_broadcaster.py`)**: Manages WebSocket connections and broadcasts structured, user-facing log messages to the appropriate client based on the `request_id`.
-   **Smart Correction Service (`smart_correction_service.py`)**: Pre-processes the user query by sending it to the Gemini API to detect and suggest corrections for misspelled company names, improving the accuracy of ticker extraction.
-   **Orchestrator (`yahoo_finance_orchestrator.py`)**: The core of the backend. Once tickers are confirmed, it coordinates the execution of various data-gathering and analysis agents in parallel.

### 3.3. Multi-Agent System

The orchestrator spawns a set of specialized, asynchronous agents for each stock ticker being analyzed. This parallel execution model significantly speeds up the research process.

-   **News Agent**: Fetches and summarizes the latest news articles to gauge market sentiment.
-   **Price Agent**: Retrieves historical price data to analyze trends and technical indicators (e.g., support and resistance).
-   **Financials Agent**: Gathers fundamental financial data, such as P/E ratios and market cap.
-   **Synthesis Agent**: The final step in the pipeline. It receives the outputs from all other agents and uses the Gemini API to synthesize the information into a coherent investment thesis, including a stance (Buy, Sell, Hold), confidence level, and a detailed rationale.

### 3.4. External Services

-   **Yahoo Finance API**: The primary source for all real-time and historical market data.
-   **Gemini API**: Used for all AI-driven tasks, including typo correction, data analysis, and the final synthesis of the investment recommendation.

---

## 4. Deployment & Scalability

The application is fully containerized using Docker and orchestrated with Docker Compose. This approach provides a consistent and reproducible environment for both development and production.

-   **Services**: The `docker-compose.yml` file defines two main services: `frontend` and `backend`.
-   **Networking**: The services communicate over a shared Docker network.
-   **Scalability**: The backend can be scaled horizontally to handle a larger volume of concurrent analysis requests by running multiple container instances.

    ```bash
    docker-compose up --build --scale backend=3
    ```

This architecture ensures a robust, scalable, and maintainable system capable of delivering powerful stock market insights through an intuitive and responsive interface.
