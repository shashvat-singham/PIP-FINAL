# Deployment Guide - Stock Research Chatbot

## Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key
- Docker (optional but recommended)

### Step 1: Get API Key
1. Visit https://ai.google.dev/
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

### Step 2: Configure Environment
```bash
# Copy the template
cp .env.template .env

# Edit .env and add your API key
nano .env  # or use any text editor

# Add this line:
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 3: Run with Docker (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access the application:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend UI: http://localhost:3000

### Step 4: Run Locally (Development)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cd ..
export PYTHONPATH=$(pwd)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend/stock-research-ui
npm install
npm run dev
```

## Usage Examples

### Example 1: Single Company by Name
```
Query: "Analyze Apple for 1 month"
Result: Analyzes AAPL with comprehensive insights
```

### Example 2: Multiple Companies
```
Query: "Compare Apple Microsoft and Meta"
Result: Separate analysis for AAPL, MSFT, and META
```

### Example 3: Using Tickers
```
Query: "Analyze NVDA AMD TSM for AI datacenter demand"
Result: Analyzes all three semiconductor stocks
```

### Example 4: Mixed Input
```
Query: "Compare NVDA with Intel and AMD"
Result: Analyzes NVDA, INTC, and AMD
```

## API Usage

### cURL Example
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze Apple Microsoft for 3 months",
    "max_iterations": 3,
    "timeout_seconds": 60
  }'
```

### Python Example
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "query": "Analyze Apple Microsoft for 3 months",
        "max_iterations": 3,
        "timeout_seconds": 60
    }
)

result = response.json()
print(f"Analyzed: {result['tickers_analyzed']}")
for insight in result['insights']:
    print(f"{insight['ticker']}: {insight['stance']} - {insight['summary']}")
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');

async function analyzeStocks() {
    const response = await axios.post('http://localhost:8000/api/v1/analyze', {
        query: 'Analyze Apple Microsoft for 3 months',
        max_iterations: 3,
        timeout_seconds: 60
    });
    
    console.log('Tickers:', response.data.tickers_analyzed);
    response.data.insights.forEach(insight => {
        console.log(`${insight.ticker}: ${insight.stance} - ${insight.summary}`);
    });
}

analyzeStocks();
```

## Troubleshooting

### Issue: "No valid stock tickers found"
**Solution:** Make sure you're using valid company names or ticker symbols.
```
✅ Correct: "Analyze Apple" or "Analyze AAPL"
❌ Incorrect: "Analyze XYZ" (unknown company)
```

### Issue: Backend not starting
**Solution:** Check if port 8000 is already in use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process if needed
kill -9 <PID>
```

### Issue: "GEMINI_API_KEY not found"
**Solution:** Make sure .env file exists and contains your API key
```bash
# Check if .env exists
ls -la .env

# Verify it contains the key
cat .env | grep GEMINI_API_KEY
```

### Issue: Docker build fails
**Solution:** Make sure Docker has enough resources
```bash
# Check Docker status
docker info

# Clean up old images
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Issue: Slow API responses
**Solution:** The Gemini API can take 10-30 seconds for complex queries. This is normal.
- Increase `timeout_seconds` in your request
- Reduce `max_iterations` for faster results
- Use Docker with proper resource allocation

## Production Deployment

### Environment Variables for Production
```env
GEMINI_API_KEY=your_production_key
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_ITERATIONS=3
TIMEOUT_SECONDS=90
CORS_ORIGINS=https://yourdomain.com
```

### Security Checklist
- [ ] Change SECRET_KEY to a random string
- [ ] Use HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Use environment-specific .env files
- [ ] Never commit .env to version control

### Scaling Considerations
- Use Redis for conversation state management
- Implement caching for frequently requested tickers
- Use a load balancer for multiple backend instances
- Consider using a CDN for frontend assets
- Monitor API rate limits for Gemini and Yahoo Finance

## Monitoring

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Check with Docker
docker-compose ps
```

### Logs
```bash
# View backend logs
docker-compose logs backend

# View frontend logs
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Metrics to Monitor
- Request latency (should be < 30s for most queries)
- Success rate (should be > 95%)
- API errors (Gemini, Yahoo Finance)
- Memory usage
- CPU usage

## Support

For issues:
1. Check the logs: `docker-compose logs`
2. Verify .env configuration
3. Test API endpoint: `curl http://localhost:8000/health`
4. Review README.md for detailed documentation

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Google Gemini Docs**: https://ai.google.dev/docs
- **Yahoo Finance API**: https://github.com/ranaroussi/yfinance

