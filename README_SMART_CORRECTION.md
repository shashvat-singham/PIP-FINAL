# Smart Correction Feature - Implementation Guide

## Overview

The stock research chatbot has been enhanced with a **Gemini-powered smart correction mechanism** that intelligently detects and corrects misspelled company names before processing stock analysis requests.

## Key Features

### 🤖 AI-Powered Correction
- Uses **Google Gemini 2.5 Flash** to detect misspellings
- Handles typos, phonetic similarities, and partial names
- Works for any publicly traded company, not just a predefined list

### 🔄 Interactive Confirmation Flow
- Prompts users when a misspelling is detected
- Shows corrected company name and ticker symbol
- Waits for user confirmation before proceeding
- Allows users to reject and provide alternative input

### 📊 Confidence Levels
- **High**: Clear misspelling with obvious correction
- **Medium**: Likely misspelling with reasonable correction
- **Low**: Uncertain correction, user should verify

## How It Works

### 1. User Input Detection
When a user submits a query like:
```
"Analyze matae for 1 month"
```

### 2. Smart Correction Analysis
The system:
1. Sends the input to Gemini AI
2. Gemini analyzes the text for potential misspellings
3. Returns correction suggestion with confidence level

### 3. Confirmation Prompt
If a misspelling is detected, the system responds:
```json
{
  "needs_confirmation": true,
  "confirmation_prompt": {
    "type": "confirmation",
    "message": "Did you mean **Meta Platforms Inc.** (META)?",
    "suggestion": {
      "original_input": "matae",
      "corrected_name": "Meta Platforms Inc.",
      "ticker": "META",
      "confidence": "high",
      "explanation": "Detected likely misspelling of 'Meta'"
    },
    "conversation_id": "abc-123-def"
  }
}
```

### 4. User Response
The user can respond:
- **"Yes"** / **"Y"** / **"Sure"** → Proceeds with META analysis
- **"No"** / **"N"** → Asks for clarification
- Provide alternative company name → Re-processes the input

### 5. Follow-up Request
User sends confirmation:
```json
{
  "query": "Analyze matae for 1 month",
  "conversation_id": "abc-123-def",
  "confirmation_response": "Yes"
}
```

### 6. Analysis Proceeds
System analyzes META and returns full research insights.

## API Changes

### Updated Request Model
```python
class AnalysisRequest(BaseModel):
    query: str
    max_iterations: Optional[int] = 3
    timeout_seconds: Optional[int] = 30
    conversation_id: Optional[str] = None  # NEW
    confirmation_response: Optional[str] = None  # NEW
```

### Updated Response Model
```python
class AnalysisResponse(BaseModel):
    # ... existing fields ...
    needs_confirmation: bool = False  # NEW
    confirmation_prompt: Optional[ConfirmationPrompt] = None  # NEW
```

### New Models
```python
class CorrectionSuggestion(BaseModel):
    original_input: str
    corrected_name: str
    ticker: str
    confidence: str
    explanation: str

class ConfirmationPrompt(BaseModel):
    type: str  # "confirmation", "selection", "clarification"
    message: str
    suggestion: Optional[CorrectionSuggestion]
    conversation_id: str
```

## Example Usage Scenarios

### Scenario 1: Simple Typo
**Input:** `"Analyze microsft for 6 months"`

**Response:**
```
Did you mean **Microsoft Corporation** (MSFT)?
```

**User:** `"Yes"`

**Result:** Analyzes MSFT

---

### Scenario 2: Phonetic Similarity
**Input:** `"Compare gogle and amazn"`

**Response:**
```
Did you mean **Alphabet Inc.** (GOOGL)?
```

**User:** `"Yes"`

**System:** Now processes second company "amazn"

**Response:**
```
Did you mean **Amazon.com Inc.** (AMZN)?
```

**User:** `"Yes"`

**Result:** Analyzes both GOOGL and AMZN

---

### Scenario 3: User Rejection
**Input:** `"Analyze metae"`

**Response:**
```
Did you mean **Meta Platforms Inc.** (META)?
```

**User:** `"No"`

**Response:**
```
Got it. Which company or ticker would you like to analyze?
```

**User:** `"Tesla"`

**Result:** Analyzes TSLA

---

### Scenario 4: Already Correct
**Input:** `"Analyze Apple for 1 month"`

**Response:** No confirmation needed, directly proceeds with AAPL analysis

---

### Scenario 5: Valid Ticker
**Input:** `"Analyze NVDA and AMD"`

**Response:** No confirmation needed, directly analyzes both tickers

## Implementation Details

### New Service: `SmartCorrectionService`
Located at: `backend/services/smart_correction_service.py`

**Key Methods:**
- `detect_and_correct(user_input)` - Main correction logic
- `generate_confirmation_message(correction_result)` - Creates user-friendly prompts

### Updated Services

#### `ConversationManager`
- Manages conversation state across multiple interactions
- Stores pending confirmations
- Processes user responses (Yes/No/Alternative)

#### `API Endpoint` (`/api/v1/analyze`)
Enhanced flow:
1. Check for conversation_id + confirmation_response (follow-up)
2. If new query, run smart correction
3. If misspelling detected, return confirmation prompt
4. If confirmed or no issues, proceed with analysis

### Fallback Mechanism
If Gemini API fails or is unavailable:
1. Falls back to traditional fuzzy matching (difflib)
2. Uses predefined company dictionary
3. Still provides confirmation prompts for ambiguous matches

## Configuration

### Environment Variables
```bash
# Required for smart correction
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Gemini Model
- **Model:** `gemini-2.5-flash`
- **Purpose:** Fast, cost-effective for text analysis
- **Fallback:** Traditional fuzzy matching if unavailable

## Testing Examples

### Test 1: Common Typos
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze matae for 1 month"
  }'
```

Expected: Confirmation prompt for META

### Test 2: Confirmation Response
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze matae for 1 month",
    "conversation_id": "abc-123",
    "confirmation_response": "Yes"
  }'
```

Expected: Full analysis for META

### Test 3: Multiple Companies
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare microsft, gogle, and amazn"
  }'
```

Expected: Sequential confirmation prompts for each

## Frontend Integration

### Handling Confirmation Prompts

```javascript
async function analyzeStock(query, conversationId = null, confirmationResponse = null) {
  const response = await fetch('/api/v1/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      conversation_id: conversationId,
      confirmation_response: confirmationResponse
    })
  });
  
  const data = await response.json();
  
  if (data.needs_confirmation) {
    // Show confirmation prompt to user
    const userResponse = await showConfirmationDialog(
      data.confirmation_prompt.message
    );
    
    // Send follow-up request with user's response
    return analyzeStock(
      query,
      data.confirmation_prompt.conversation_id,
      userResponse
    );
  }
  
  // Process normal analysis results
  return data;
}
```

### UI Components

#### Confirmation Dialog
```jsx
function ConfirmationDialog({ prompt, onConfirm, onReject }) {
  return (
    <div className="confirmation-dialog">
      <p>{prompt.message}</p>
      {prompt.suggestion && (
        <div className="suggestion-details">
          <p>Original: {prompt.suggestion.original_input}</p>
          <p>Suggested: {prompt.suggestion.corrected_name} ({prompt.suggestion.ticker})</p>
          <p>Confidence: {prompt.suggestion.confidence}</p>
        </div>
      )}
      <button onClick={() => onConfirm("Yes")}>Yes</button>
      <button onClick={() => onReject("No")}>No</button>
    </div>
  );
}
```

## Benefits

### 1. **Improved User Experience**
- No need to know exact company names or tickers
- Forgiving of typos and misspellings
- Clear, interactive feedback

### 2. **Broader Coverage**
- Works for any publicly traded company
- Not limited to predefined dictionary
- Handles new companies and IPOs

### 3. **Intelligent Corrections**
- Context-aware suggestions
- Confidence levels help users make decisions
- Explanations build trust

### 4. **Reduced Errors**
- Catches mistakes before processing
- Prevents failed analyses
- Saves API calls and processing time

## Limitations

1. **API Dependency**: Requires Gemini API to be available
2. **Latency**: Adds ~500-1000ms for Gemini API call
3. **Cost**: Small cost per API call (minimal with Gemini Flash)
4. **Conversation State**: Requires conversation management (in-memory or Redis)

## Future Enhancements

1. **Multi-turn Conversations**: Handle complex clarifications
2. **Learning System**: Remember user preferences
3. **Batch Corrections**: Handle multiple misspellings at once
4. **Voice Input**: Integrate with speech-to-text for voice queries
5. **Multilingual Support**: Support company names in other languages

## Troubleshooting

### Issue: Smart correction not working
**Solution:** Check GEMINI_API_KEY is set correctly

### Issue: Always falls back to fuzzy matching
**Solution:** Verify Gemini API quota and connectivity

### Issue: Conversation expired
**Solution:** Conversations expire after 30 minutes. Start a new query.

### Issue: Incorrect suggestions
**Solution:** User can always reject and provide correct input

## Logging

All smart correction events are logged:
```python
logger.info("Smart correction detected misspelling",
           original="matae",
           corrected="Meta Platforms Inc.",
           ticker="META",
           confidence="high")
```

Check logs at: `logs/app.log`

---

**Built with ❤️ using Google Gemini 2.5 Flash**

**🚀 Making stock research more accessible and user-friendly!**

