"""
API routes for the Stock Research Chatbot.
"""
import uuid
import time
from datetime import datetime
from typing import Dict, Any

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
        
        # Handle follow-up confirmation responses
        if request.conversation_id and request.confirmation_response:
            conversation = conversation_manager.get_conversation(request.conversation_id)
            if conversation:
                response_result = conversation_manager.process_confirmation_response(
                    conversation, 
                    request.confirmation_response
                )
                
                if response_result["status"] == "confirmed":
                    # User confirmed, proceed with analysis using the confirmed ticker
                    ticker = response_result["ticker"]
                    tickers = [ticker]
                    unresolved_names = []
                    
                    logger.info("User confirmed correction",
                               conversation_id=request.conversation_id,
                               ticker=ticker)
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
                # Treat as new query
                request.conversation_id = None
        
        # If not a follow-up, process as new query
        if not request.conversation_id or not request.confirmation_response:
            # First, try smart correction with Gemini
            if smart_correction_service:
                try:
                    correction_result = smart_correction_service.detect_and_correct(request.query)
                    
                    if correction_result.get('is_misspelled') and correction_result.get('ticker'):
                        # Create a conversation for confirmation
                        conversation = conversation_manager.create_conversation(request_id)
                        conversation.original_query = request.query
                        
                        # Store the correction suggestion
                        conversation.pending_confirmations = [{
                            "company": correction_result.get('corrected_name'),
                            "ticker": correction_result.get('ticker'),
                            "confidence": correction_result.get('confidence')
                        }]
                        
                        # Generate confirmation message
                        confirmation_message = smart_correction_service.generate_confirmation_message(
                            correction_result
                        )
                        
                        logger.info("Smart correction detected misspelling",
                                   original=correction_result.get('original_input'),
                                   corrected=correction_result.get('corrected_name'),
                                   ticker=correction_result.get('ticker'))
                        
                        # Return confirmation prompt
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
                                    original_input=correction_result.get('original_input'),
                                    corrected_name=correction_result.get('corrected_name'),
                                    ticker=correction_result.get('ticker'),
                                    confidence=correction_result.get('confidence'),
                                    explanation=correction_result.get('explanation')
                                ),
                                conversation_id=request_id
                            )
                        )
                except Exception as e:
                    logger.warning("Smart correction failed, falling back to traditional method",
                                  error=str(e))
            
            # Fallback to traditional ticker extraction
            tickers, unresolved_names = ticker_mapper.extract_tickers_from_query(request.query)
            
            # If there are unresolved names, check for suggestions using fuzzy matching
            if unresolved_names:
                for name in unresolved_names:
                    suggestions = ticker_mapper.find_suggestions(name, n=3)
                    if suggestions:
                        # Create conversation for confirmation
                        conversation = conversation_manager.create_conversation(request_id)
                        conversation.original_query = request.query
                        confirmation_prompt = conversation_manager.create_confirmation_prompt(
                            conversation, suggestions
                        )
                        
                        logger.info("Fuzzy matching found suggestions",
                                   name=name,
                                   suggestions_count=len(suggestions))
                        
                        # Return confirmation request
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
                                type=confirmation_prompt["type"],
                                message=confirmation_prompt["message"],
                                suggestion=CorrectionSuggestion(
                                    original_input=name,
                                    corrected_name=suggestions[0][0],
                                    ticker=suggestions[0][1],
                                    confidence="medium",
                                    explanation="Found using fuzzy matching"
                                ) if len(suggestions) == 1 else None,
                                conversation_id=request_id
                            )
                        )
        
        # If we get here, we have valid tickers to analyze
        if not tickers:
            raise ValueError("No valid stock tickers found in query. Please provide company names or ticker symbols.")
        
        # Update status
        analysis_status_store[request_id] = {
            "status": "processing",
            "progress": 0.0,
            "current_step": "Initializing analysis with Yahoo Finance",
            "started_at": started_at
        }
        
        # Run the analysis
        insights = await orchestrator.analyze(
            query=request.query,
            max_iterations=request.max_iterations or 3,
            timeout_seconds=request.timeout_seconds or 60,
            request_id=request_id
        )
        
        # Calculate execution time
        end_time = time.time()
        total_latency_ms = (end_time - start_time) * 1000
        
        # Extract tickers and agents used
        tickers_analyzed = [insight.ticker for insight in insights]
        agents_used = list(set([
            trace.agent_type 
            for insight in insights 
            for trace in insight.agent_traces
        ]))
        
        # Format response with 2 decimal places
        response_data = {
            "request_id": request_id,
            "query": request.query,
            "insights": [insight.model_dump() for insight in insights],
            "total_latency_ms": total_latency_ms,
            "tickers_analyzed": tickers_analyzed,
            "agents_used": agents_used,
            "started_at": started_at,
            "completed_at": datetime.now()
        }
        
        formatted_response = format_analysis_response(response_data)
        response = AnalysisResponse(**formatted_response)
        
        # Update final status
        analysis_status_store[request_id] = {
            "status": "completed",
            "progress": 100.0,
            "current_step": "Analysis complete",
            "completed_at": datetime.now()
        }
        
        logger.info("Stock analysis completed", 
                    request_id=request_id,
                    tickers_count=len(tickers_analyzed),
                    latency_ms=total_latency_ms)
        
        return response
        
    except Exception as e:
        logger.error("Stock analysis failed", 
                     request_id=request_id, 
                     error=str(e))
        
        # Update error status
        analysis_status_store[request_id] = {
            "status": "failed",
            "progress": 0.0,
            "current_step": f"Error: {str(e)}",
            "error": str(e)
        }
        
        if "No valid stock tickers found in query" in str(e):
            raise HTTPException(
                status_code=422,
                detail=f"Validation Error: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )



@router.get("/analyze/{request_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(request_id: str) -> AnalysisStatus:
    """Get the status of an ongoing analysis."""
    if request_id not in analysis_status_store:
        raise HTTPException(
            status_code=404,
            detail="Analysis request not found"
        )
    
    status_data = analysis_status_store[request_id]
    
    return AnalysisStatus(
        request_id=request_id,
        status=status_data["status"],
        progress=status_data["progress"],
        current_step=status_data.get("current_step"),
        estimated_completion=status_data.get("estimated_completion")
    )


@router.get("/analyze/{request_id}")
async def get_analysis_result(request_id: str) -> Dict[str, Any]:
    """Get the result of a completed analysis."""
    if request_id not in analysis_status_store:
        raise HTTPException(
            status_code=404,
            detail="Analysis request not found"
        )
    
    status_data = analysis_status_store[request_id]
    
    if status_data["status"] != "completed":
        return {
            "request_id": request_id,
            "status": status_data["status"],
            "message": "Analysis not yet completed"
        }
    
    # In a real implementation, you'd retrieve the full result from storage
    return {
        "request_id": request_id,
        "status": "completed",
        "message": "Analysis completed successfully"
    }


@router.delete("/analyze/{request_id}")
async def cancel_analysis(request_id: str) -> Dict[str, str]:
    """Cancel an ongoing analysis."""
    if request_id not in analysis_status_store:
        raise HTTPException(
            status_code=404,
            detail="Analysis request not found"
        )
    
    # Update status to cancelled
    analysis_status_store[request_id]["status"] = "cancelled"
    analysis_status_store[request_id]["current_step"] = "Analysis cancelled by user"
    
    logger.info("Analysis cancelled", request_id=request_id)
    
    return {
        "request_id": request_id,
        "message": "Analysis cancelled successfully"
    }


@router.get("/agents")
async def list_available_agents() -> Dict[str, Any]:
    """List all available research agents and their capabilities."""
    return {
        "agents": [
            {
                "type": "news",
                "description": "Fetches and analyzes recent news from Yahoo Finance",
                "capabilities": ["yahoo_finance_news", "news_summarization", "sentiment_analysis"]
            },
            {
                "type": "price",
                "description": "Analyzes price movements and technical indicators from Yahoo Finance",
                "capabilities": ["price_analysis", "technical_indicators", "support_resistance"]
            },
            {
                "type": "synthesis",
                "description": "Synthesizes all data using Gemini AI to generate investment recommendations",
                "capabilities": ["ai_analysis", "investment_rationale", "risk_assessment"]
            }
        ],
        "data_sources": [
            "Yahoo Finance (real-time stock data and news)",
            "Google Gemini AI (intelligent analysis and synthesis)"
        ],
        "features": [
            "Smart spelling correction using Gemini AI",
            "Interactive confirmation for ambiguous company names",
            "Multi-company parallel analysis"
        ]
    }

