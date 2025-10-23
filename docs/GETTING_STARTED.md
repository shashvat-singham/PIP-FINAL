# Getting Started Guide

This guide provides detailed instructions for setting up and running the Stock Research Agentic Chatbot in a local development environment.

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.11 or higher**
- **Node.js 18 or higher** and **npm** (for React frontend development)
- **Git** for cloning the repository
- **A Gemini API Key** from Google AI Studio

## 2. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone <repository_url>
cd stock-research-chatbot
```

## 3. Environment Setup

### 3.1. Run the Setup Script

The project includes a convenient Python script to set up your development environment. This script will:

- Check Python and Node.js versions.
- Create a Python virtual environment if it doesn't exist.
- Install all required Python dependencies.
- Install all required Node.js dependencies for the React frontend.
- Create necessary data directories (`data/chroma_db`, `logs`).
- Create a `.env` file from `.env.template` if it doesn't exist.
- Run tests to verify the setup.

To run the script, execute the following command from the project root:

```bash
python scripts/setup.py
```

### 3.2. Activate the Virtual Environment

After running the setup script, you need to activate the Python virtual environment. This step is crucial for ensuring that all Python dependencies are correctly used.

- On **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```
- On **Windows (Command Prompt)**:
  ```cmd
  .\venv\Scripts\activate.bat
  ```
- On **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

### 3.3. Configure Environment Variables

If the `setup.py` script created a new `.env` file, or if you need to update your API key:

1.  Open the `.env` file in a text editor (it's located in the project root).
2.  Add or update your Gemini API key:
    ```dotenv
    # Gemini API Configuration
    GEMINI_API_KEY=your_gemini_api_key_here

    # Application Configuration
    APP_ENV=development
    LOG_LEVEL=INFO
    MAX_ITERATIONS=3
    REQUEST_TIMEOUT=60

    # Vector Database Configuration
    CHROMA_PERSIST_DIRECTORY=./data/chroma_db

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE=60

    # Security
    SECRET_KEY=a_secure_random_string_for_development
    ```

## 4. Running the Application

The application consists of a backend API and a choice of two frontends (React or Streamlit). The `start.py` script can be used to run them in different configurations. Ensure your virtual environment is activated before running the start script.

### 4.1. Running with the React Frontend (Recommended)

This will start the backend API server and the React development server in parallel.

```bash
python scripts/start.py --frontend react
```

Once started, you can access:

- **React Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

### 4.2. Running with the Streamlit Frontend

This will start the backend API server and the Streamlit application.

```bash
python scripts/start.py --frontend streamlit
```

Once started, you can access:

- **Streamlit Frontend**: `http://localhost:8501`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

### 4.3. Running Both Frontends

You can also run both frontends simultaneously for comparison:

```bash
python scripts/start.py --frontend both
```

### 4.4. Installing Dependencies During Startup

If you want to force reinstall dependencies or haven't run `setup.py` previously, you can use the `--install-deps` flag:

```bash
python scripts/start.py --frontend react --install-deps
```

## 5. Running Tests

The project has a comprehensive test suite. To run the tests, make sure your virtual environment is activated and run:

```bash
pytest
```

## 6. Project Structure

Here is an overview of the project's directory structure:

```
stock-research-chatbot/
├── backend/                # FastAPI backend application
│   ├── app/                # API endpoints, models, main app
│   ├── agents/             # Research agents (news, filings, etc.)
│   ├── tools/              # Tools for agents (web search, data APIs)
│   ├── config/             # Configuration settings
│   └── tests/              # Backend tests
├── frontend/               # Frontend applications
│   ├── stock-research-ui/  # React application
│   └── app.py              # Streamlit application
├── docs/                   # Project documentation
├── scripts/                # Helper scripts (start, setup, deploy)
├── data/                   # Data storage (e.g., vector database)
├── logs/                   # Application logs
├── .env                    # Environment variables (gitignored)
├── .env.template           # Template for .env file
├── Dockerfile              # Dockerfile for the main application
├── Dockerfile.streamlit    # Dockerfile for the Streamlit UI
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # Main project README
```

## 7. Troubleshooting

- **Virtual Environment Activation**: Ensure your virtual environment is activated in each new terminal session where you intend to run Python scripts.
- **Port conflicts**: If you have other services running on ports `8000`, `3000`, or `8501`, you may need to stop them or change the port mappings in `docker-compose.yml` or the start scripts.
- **API Key Issues**: Ensure your `GEMINI_API_KEY` is correct and has the necessary permissions.
- **Dependency Errors**: If you encounter dependency issues, try deleting the `venv` and `node_modules` directories and re-running the setup script.

For any other issues, please open an issue on the project's GitHub repository.

