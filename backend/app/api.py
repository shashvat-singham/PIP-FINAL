"""
API routes for the Stock Research Chatbot.
Enhanced with multi-correction support - ALL corrections in ONE response.
"""
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import structlog

from backend.app.models import (
    AnalysisRequest, 
    AnalysisResponse, 
    AnalysisStatus,
    TickerInsight,
    StanceType,
    ConfidenceLevel,
    CorrectionSuggestion,
    ConfirmationPrompt
)
from backend.agents.yahoo_finance_orchestrator import YahooFinanceOrchestrator
from backend.config.settings import get_settings
from backend.services.ticker_mapper import get_ticker_mapper
from backend.services.conversation_manager import get_conversation_manager
from backend.services.smart_correction_service import get_smart_correction_service
from backend.utils.formatters import format_analysis_response

logger = structlog.get_logger()
router = APIRouter()

# In-memory storage for analysis status (in production, use Redis or similar)
analysis_status_store: Dict[str, Dict[str, Any]] = {}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stocks(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze stocks based on natural language query.
    
    This endpoint triggers the multi-agent research process for the specified stocks.
    Includes smart correction for misspelled company names using Gemini AI.
    ALL corrections are presented in a SINGLE response - no multiple confirmations.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    started_at = datetime.now()
    
    logger.info("Starting stock analysis", 
                request_id=request_id, 
                query=request.query)
    
    try:
        # Initialize services
        orchestrator = YahooFinanceOrchestrator()
        ticker_mapper = get_ticker_mapper()
        conversation_manager = get_conversation_manager()
        smart_correction_service = get_smart_correction_service()
        
        tickers = []
        unresolved_names = []
        
        # Handle follow-up confirmation responses
        if request.conversation_id and request.confirmation_response:
            conversation = conversation_manager.get_conversation(request.conversation_id)
            if conversation:
                response_result = conversation_manager.process_confirmation_response(
                    conversation, 
                    request.confirmation_response
                )
                
                if response_result["status"] == "confirmed":
                    # User confirmed ALL corrections at once
                    logger.info("User confirmed all corrections",
                               conversation_id=request.conversation_id,
                               confirmed_tickers=conversation.confirmed_tickers)
                    
                    # Use confirmed tickers for analysis
                    tickers = conversation.confirmed_tickers
                    unresolved_names = []
                    
                elif response_result["status"] == "rejected":
                    # User rejected, ask for clarification
                    return AnalysisResponse(
                        request_id=request_id,
                        query=request.query,
                        insights=[],
                        total_latency_ms=(time.time() - start_time) * 1000,
                        tickers_analyzed=[],
                        agents_used=[],
                        started_at=started_at,
                        completed_at=datetime.now(),
                        success=False,
                        needs_confirmation=True,
                        confirmation_prompt=ConfirmationPrompt(
                            type="clarification",
                            message=response_result["message"],
                            suggestion=None,
                            conversation_id=request.conversation_id
                        )
                    )
            else:
                logger.warning("Conversation not found or expired",
                              conversation_id=request.conversation_id)
                raise HTTPException(status_code=400, detail="Conversation expired. Please start a new query.")
        
        # If not a follow-up, process as new query
        if not request.conversation_id or not request.confirmation_response:
            # First, try smart correction with Gemini (supports MULTIPLE corrections)
            if smart_correction_service:
                try:
                    correction_result = smart_correction_service.detect_and_correct_multiple(request.query)
                    
                    if correction_result.get('has_misspellings') and correction_result.get('corrections'):
                        corrections = correction_result.get('corrections', [])
                        
                        # Create a conversation for confirmation
                        conversation = conversation_manager.create_conversation(request_id)
                        conversation.original_query = request.query
                        
                        # Store ALL confirmed tickers at once
                        conversation.confirmed_tickers = [corr['ticker'] for corr in corrections]
                        
                        # Build a SINGLE confirmation message for ALL corrections
                        if len(corrections) == 1:
                            first_correction = corrections[0]
                            confirmation_message = f"Did you mean **{first_correction['corrected_name']}** ({first_correction['ticker']})?"
                        else:
                            # Multiple corrections - show all at once
                            corrections_list = []
                            for i, corr in enumerate(corrections, 1):
                                corrections_list.append(
                                    f"{i}. '{corr['original']}' → **{corr['corrected_name']}** ({corr['ticker']})"
                                )
                            
                            confirmation_message = (
                                f"I found {len(corrections)} potential misspellings:\n\n" +
                                "\n".join(corrections_list) +
                                "\n\nDid you mean these corrections?"
                            )
                        
                        logger.info("Smart correction detected misspellings - presenting ALL at once",
                                   original=correction_result.get('original_input'),
                                   corrections_count=len(corrections))
                        
                        # Return confirmation prompt for ALL corrections at once
                        return AnalysisResponse(
                            request_id=request_id,
                            query=request.query,
                            insights=[],
                            total_latency_ms=(time.time() - start_time) * 1000,
                            tickers_analyzed=[],
                            agents_used=[],
                            started_at=started_at,
                            completed_at=datetime.now(),
                            success=False,
                            needs_confirmation=True,
                            confirmation_prompt=ConfirmationPrompt(
                                type="confirmation",
                                message=confirmation_message,
                                suggestion=CorrectionSuggestion(
                                    original_input=request.query,
                                    corrected_name=", ".join([c['corrected_name'] for c in corrections]),
                                    ticker=", ".join([c['ticker'] for c in corrections]),
                                    confidence=corrections[0].get('confidence', 'medium'),
                                    explanation=f"Found {len(corrections)} potential misspelling(s)"
                                ),
                                conversation_id=request_id
                            )
                        )
                except Exception as e:
                    logger.warning("Smart correction failed, falling back to traditional method",
                                  error=str(e))
            
            # If no misspellings detected or smart correction failed, extract tickers normally
            if not tickers:
                tickers, unresolved_names = ticker_mapper.extract_tickers_from_query(request.query)
        
        # Validate tickers
        if not tickers:
            raise HTTPException(
                status_code=400,
                detail="No valid stock tickers found in query. Please specify at least one ticker or company name."
            )
        
        logger.info("Extracted tickers", tickers=tickers)
        
        # Execute orchestrated analysis
        # Pass confirmed tickers directly if available to avoid re-extraction
        results = await orchestrator.analyze(
            query=request.query,
            max_iterations=request.max_iterations,
            timeout_seconds=request.timeout_seconds,
            request_id=request_id,
            confirmed_tickers=tickers if tickers else None
        )
        
        # Format response
        response = format_analysis_response(
            request_id=request_id,
            query=request.query,
            insights=results,
            started_at=started_at,
            total_latency_ms=(time.time() - start_time) * 1000
        )
        
        logger.info("Stock analysis completed", 
                   request_id=request_id,
                   tickers_count=len(results))
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Stock analysis failed", 
                    request_id=request_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/status/{request_id}")
async def get_analysis_status(request_id: str) -> Dict[str, Any]:
    """Get the status of an analysis request."""
    if request_id not in analysis_status_store:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return analysis_status_store[request_id]


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "stock-research-chatbot"
    }
