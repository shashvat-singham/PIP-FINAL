"""
Smart Correction Service - Uses Gemini AI to detect and correct misspelled company names.
"""
import google.generativeai as genai
import json
import os
from typing import Optional, Dict, Any
import structlog
from dotenv import load_dotenv

load_dotenv()

logger = structlog.get_logger()


class SmartCorrectionService:
    """
    Service for detecting and correcting misspelled company names using Gemini AI.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Smart Correction service.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found, smart correction will not work")
            raise ValueError("GEMINI_API_KEY is required for smart correction")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        logger.info("SmartCorrectionService initialized")
    
    def detect_and_correct(self, user_input: str) -> Dict[str, Any]:
        """
        Detect if the user input contains a misspelled company name and suggest corrections.
        
        Args:
            user_input: The user's input text (e.g., "matae" or "analyze metae for 1 month")
            
        Returns:
            Dictionary containing:
            - is_misspelled: bool - Whether a misspelling was detected
            - original_input: str - The original user input
            - corrected_name: str - The corrected company name (if found)
            - ticker: str - The stock ticker symbol (if found)
            - confidence: str - Confidence level (high, medium, low)
            - explanation: str - Brief explanation of the correction
        """
        prompt = f"""You are a financial assistant that helps users identify company names and stock tickers.

USER INPUT: "{user_input}"

TASK:
Analyze the user input and determine if it contains a misspelled or ambiguous company name. If so, identify the most likely correct company name and its stock ticker symbol.

RULES:
1. Look for company names or partial names that might be misspelled
2. Consider common typos, missing letters, extra letters, or phonetic similarities
3. Only suggest corrections for well-known publicly traded companies
4. If the input already contains a valid ticker (e.g., "AAPL", "MSFT"), mark is_misspelled as false
5. If the input contains a correctly spelled company name, mark is_misspelled as false
6. Be confident in your suggestions - only suggest corrections when you're reasonably sure

EXAMPLES:
- "matae" → Meta Platforms Inc. (META)
- "metae" → Meta Platforms Inc. (META)
- "microsft" → Microsoft Corporation (MSFT)
- "gogle" → Alphabet Inc. (GOOGL)
- "analyze apple for 1 month" → No correction needed (correctly spelled)
- "AAPL" → No correction needed (valid ticker)
- "analyze NVDA and AMD" → No correction needed (valid tickers)

Respond in JSON format:
{{
    "is_misspelled": true or false,
    "original_input": "the exact user input",
    "corrected_name": "Full Company Name" or null,
    "ticker": "TICKER" or null,
    "confidence": "high, medium, or low",
    "explanation": "Brief explanation of why you think this is/isn't a misspelling"
}}

Respond with ONLY the JSON, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            logger.info("Smart correction analysis completed",
                       user_input=user_input,
                       is_misspelled=result.get('is_misspelled'),
                       corrected_name=result.get('corrected_name'),
                       ticker=result.get('ticker'))
            
            return result
            
        except Exception as e:
            logger.error("Error in smart correction", 
                        user_input=user_input,
                        error=str(e))
            
            # Return a safe fallback
            return {
                "is_misspelled": False,
                "original_input": user_input,
                "corrected_name": None,
                "ticker": None,
                "confidence": "low",
                "explanation": f"Unable to analyze input due to error: {str(e)}"
            }
    
    def generate_confirmation_message(self, correction_result: Dict[str, Any]) -> str:
        """
        Generate a user-friendly confirmation message based on correction result.
        
        Args:
            correction_result: Result from detect_and_correct()
            
        Returns:
            Confirmation message string
        """
        if not correction_result.get('is_misspelled'):
            return None
        
        corrected_name = correction_result.get('corrected_name')
        ticker = correction_result.get('ticker')
        confidence = correction_result.get('confidence', 'medium')
        
        if corrected_name and ticker:
            if confidence == 'high':
                return f"Did you mean **{corrected_name}** ({ticker})?"
            elif confidence == 'medium':
                return f"Did you mean **{corrected_name}** ({ticker})? (I'm moderately confident about this)"
            else:
                return f"Did you possibly mean **{corrected_name}** ({ticker})? (I'm not very confident about this)"
        
        return None


# Global instance
_smart_correction_service = None


def get_smart_correction_service() -> SmartCorrectionService:
    """Get the global smart correction service instance."""
    global _smart_correction_service
    if _smart_correction_service is None:
        try:
            _smart_correction_service = SmartCorrectionService()
        except ValueError as e:
            logger.error("Failed to initialize SmartCorrectionService", error=str(e))
            # Return None if initialization fails
            return None
    return _smart_correction_service

