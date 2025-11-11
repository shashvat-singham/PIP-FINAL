"""
Yahoo Finance Orchestrator - Real-time stock analysis using Yahoo Finance and Gemini AI.
Enhanced with professional user-facing streaming logs.
"""
import asyncio
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

from backend.app.models import (
    TickerInsight, 
    AgentTrace, 
    AgentStep, 
    SourceInfo,
    StanceType,
    ConfidenceLevel
)
from backend.config.settings import get_settings
from backend.tools.yahoo_finance_tool import YahooFinanceTool
from backend.services.gemini_service import GeminiService
from backend.services.ticker_mapper import get_ticker_mapper
from backend.utils.formatters import format_ticker_insight

logger = structlog.get_logger()


class YahooFinanceOrchestrator:
    """
    Orchestrator that uses Yahoo Finance for real-time data and Gemini for analysis.
    Provides professional streaming logs for user-facing progress updates.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.yahoo_tool = YahooFinanceTool()
        self.gemini_service = GeminiService()
        self.ticker_mapper = get_ticker_mapper()
    
    def _extract_tickers(self, query: str) -> tuple[List[str], List[str]]:
        """Extract stock tickers from the query using ticker mapper.
        
        Returns:
            Tuple of (resolved_tickers, unresolved_names)
        """
        return self.ticker_mapper.extract_tickers_from_query(query)
    
    async def _analyze_ticker(self, ticker: str, query: str, max_iterations: int) -> TickerInsight:
        """
        Analyze a single ticker using Yahoo Finance and Gemini.
        
        Args:
            ticker: Stock ticker symbol
            query: Original user query
            max_iterations: Maximum iterations per agent
            
        Returns:
            TickerInsight with complete analysis
        """
        logger.info(f"Starting analysis for {ticker}")
        
        agent_traces = []
        sources = []
        
        # Step 1: Fetch stock info
        if self.log_broadcaster:
            await self.log_broadcaster.fetching_company_info(ticker)
        
        step_start = time.time()
        stock_info = self.yahoo_tool.get_stock_info(ticker)
        company_name = stock_info.get('company_name', ticker)
        
        if 'error' in stock_info:
            logger.error(f"Failed to fetch stock info for {ticker}", error=stock_info['error'])
            if self.log_broadcaster:
                await self.log_broadcaster.error(
                    f"Unable to fetch data for {ticker}. Please verify the ticker symbol.",
                    error_details={"ticker": ticker, "error": stock_info['error']}
                )
            # Return minimal insight with error
            return TickerInsight(
                ticker=ticker,
                company_name=ticker,
                stance=StanceType.HOLD,
                confidence=ConfidenceLevel.LOW,
                summary=f"Unable to fetch data for {ticker}. Please verify the ticker symbol.",
                rationale="Data unavailable",
                key_drivers=["Data unavailable"],
                risks=["Unable to analyze due to data fetch error"],
                catalysts=["N/A"],
                sources=[],
                agent_traces=[]
            )
        
        # Step 2: Fetch news (News Agent simulation)
        if self.log_broadcaster:
            await self.log_broadcaster.fetching_news(ticker, company_name)
        
        news_step_start = time.time()
        news_articles = self.yahoo_tool.get_news(ticker, limit=10)
        news_latency = (time.time() - news_step_start) * 1000
        
        if self.log_broadcaster:
            await self.log_broadcaster.news_found(ticker, len(news_articles))
        
        # Convert news to sources
        for article in news_articles[:5]:
            sources.append(SourceInfo(
                url=article['url'],
                title=article['title'],
                published_at=article['published_at'],
                snippet=article['snippet']
            ))
        
        # Summarize news using Gemini
        if self.log_broadcaster:
            await self.log_broadcaster.analyzing_news_sentiment(ticker)
        
        news_summary = self.gemini_service.summarize_news(ticker, news_articles)
        
        # Create News Agent trace
        news_trace = AgentTrace(
            agent_type="news",
            ticker=ticker,
            steps=[
                AgentStep(
                    step_number=1,
                    thought=f"I need to gather recent news about {ticker} to understand current market sentiment and developments.",
                    action=f"yahoo_finance_news: {ticker}",
                    observation=f"Found {len(news_articles)} recent news articles. {news_summary['summary']}",
                    sources=sources[:3],
                    latency_ms=news_latency
                )
            ],
            success=True,
            total_latency_ms=news_latency
        )
        agent_traces.append(news_trace)
        
        # Step 3: Fetch price data (Price Agent simulation)
        if self.log_broadcaster:
            await self.log_broadcaster.fetching_price_data(ticker, company_name)
        
        price_step_start = time.time()
        price_data = self.yahoo_tool.get_price_history(ticker, period="1mo")
        price_latency = (time.time() - price_step_start) * 1000
        
        # Analyze technical levels using Gemini
        if self.log_broadcaster:
            await self.log_broadcaster.analyzing_technicals(ticker)
        
        technical_analysis = self.gemini_service.analyze_support_resistance(ticker, price_data)
        
        if self.log_broadcaster:
            await self.log_broadcaster.price_analysis_complete(
                ticker, 
                price_data.get('trend', 'neutral')
            )
        
        # Create Price Agent trace
        price_trace = AgentTrace(
            agent_type="price",
            ticker=ticker,
            steps=[
                AgentStep(
                    step_number=1,
                    thought=f"I should analyze the recent price movement and technical indicators for {ticker}.",
                    action=f"yahoo_finance_price: {ticker}",
                    observation=f"Current price: ${price_data.get('current_price', 0):.2f}. Trend: {price_data.get('trend', 'neutral')}. {technical_analysis.get('technical_summary', '')}",
                    sources=[],
                    latency_ms=price_latency
                )
            ],
            success=True,
            total_latency_ms=price_latency
        )
        agent_traces.append(price_trace)
        
        # Step 4: Fetch financial metrics
        if self.log_broadcaster:
            await self.log_broadcaster.fetching_financials(ticker)
        
        financial_metrics = self.yahoo_tool.get_financial_metrics(ticker)
        
        # Step 5: Generate investment analysis using Gemini (Synthesis Agent)
        if self.log_broadcaster:
            await self.log_broadcaster.synthesizing_analysis(ticker)
        
        synthesis_start = time.time()
        
        if self.log_broadcaster:
            await self.log_broadcaster.generating_recommendation(ticker)
        
        investment_analysis = self.gemini_service.generate_investment_analysis(
            ticker=ticker,
            company_name=company_name,
            news_summary=news_summary,
            price_data=price_data,
            financial_metrics=financial_metrics
        )
        synthesis_latency = (time.time() - synthesis_start) * 1000
        
        if self.log_broadcaster:
            await self.log_broadcaster.recommendation_complete(
                ticker,
                investment_analysis['stance'],
                investment_analysis['confidence']
            )
        
        # Create Synthesis Agent trace
        synthesis_trace = AgentTrace(
            agent_type="synthesis",
            ticker=ticker,
            steps=[
                AgentStep(
                    step_number=1,
                    thought=f"I need to synthesize all gathered information to provide a comprehensive investment recommendation for {ticker}.",
                    action=f"gemini_analysis: Synthesize news, price, and financial data",
                    observation=f"Generated investment stance: {investment_analysis['stance']} with {investment_analysis['confidence']} confidence.",
                    sources=[],
                    latency_ms=synthesis_latency
                )
            ],
            success=True,
            total_latency_ms=synthesis_latency
        )
        agent_traces.append(synthesis_trace)
        
        # Map stance string to enum
        stance_map = {
            'buy': StanceType.BUY,
            'sell': StanceType.SELL,
            'hold': StanceType.HOLD
        }
        stance = stance_map.get(investment_analysis['stance'].lower(), StanceType.HOLD)
        
        # Map confidence string to enum
        confidence_map = {
            'high': ConfidenceLevel.HIGH,
            'medium': ConfidenceLevel.MEDIUM,
            'low': ConfidenceLevel.LOW
        }
        confidence = confidence_map.get(investment_analysis['confidence'].lower(), ConfidenceLevel.MEDIUM)
        
        # Create comprehensive summary
        summary = f"{news_summary['summary']} {investment_analysis['confidence_rationale']}"
        
        # Create TickerInsight with all data
        insight = TickerInsight(
            ticker=ticker,
            company_name=company_name,
            current_price=stock_info.get('current_price'),
            market_cap=stock_info.get('market_cap'),
            pe_ratio=stock_info.get('pe_ratio'),
            fifty_two_week_high=stock_info.get('fifty_two_week_high'),
            fifty_two_week_low=stock_info.get('fifty_two_week_low'),
            support_levels=technical_analysis.get('support_levels', []),
            resistance_levels=technical_analysis.get('resistance_levels', []),
            trend=price_data.get('trend'),
            stance=stance,
            confidence=confidence,
            summary=summary,
            rationale=investment_analysis['rationale'],
            key_drivers=investment_analysis['key_drivers'],
            risks=investment_analysis['risks'],
            catalysts=investment_analysis['catalysts'],
            sources=sources,
            agent_traces=agent_traces
        )
        
        logger.info(f"Completed analysis for {ticker}", stance=stance.value, confidence=confidence.value)
        
        # Emit completion log
        if self.log_broadcaster:
            await self.log_broadcaster.ticker_analysis_complete(ticker, company_name)
        
        return insight
    
    async def analyze(
        self, 
        query: str, 
        max_iterations: int = 3, 
        timeout_seconds: int = 60,
        request_id: str = "",
        confirmed_tickers: Optional[List[str]] = None,
        log_broadcaster = None
    ) -> List[TickerInsight]:
        """
        Run stock analysis workflow using Yahoo Finance and Gemini AI.
        
        Args:
            query: Natural language query with stock tickers
            max_iterations: Maximum iterations per agent
            timeout_seconds: Timeout for the entire analysis
            request_id: Unique request identifier
            confirmed_tickers: Pre-confirmed tickers to analyze (skips extraction)
            log_broadcaster: LogBroadcaster instance for streaming logs
            
        Returns:
            List of ticker insights
        """
        self.log_broadcaster = log_broadcaster
        start_time = time.time()
        
        logger.info("Starting Yahoo Finance stock analysis", 
                   query=query, 
                   request_id=request_id)
        
        try:
            # Use confirmed tickers if provided, otherwise extract from query
            if confirmed_tickers:
                tickers = confirmed_tickers
                unresolved_names = []
                logger.info("Using confirmed tickers", tickers=tickers, request_id=request_id)
            else:
                # Extract tickers from query
                tickers, unresolved_names = self._extract_tickers(query)
            
            if not tickers and unresolved_names:
                # Return information about unresolved names for conversation manager
                raise Exception(f"Could not resolve company names: {', '.join(unresolved_names)}. Please provide valid stock tickers or full company names.")
            
            if not tickers:
                raise Exception("No valid stock tickers found in query. Please include stock ticker symbols (e.g., AAPL, MSFT, GOOGL) or company names (e.g., Apple, Microsoft).")
            
            logger.info("Extracted tickers", tickers=tickers, unresolved_names=unresolved_names, request_id=request_id)
            
            # Emit log for starting analysis
            if self.log_broadcaster:
                await self.log_broadcaster.starting_analysis(tickers)
            
            # Analyze each ticker in parallel
            tasks = [self._analyze_ticker(ticker, query, max_iterations) for ticker in tickers]
            insights = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out any exceptions
            valid_insights = []
            for i, insight in enumerate(insights):
                if isinstance(insight, Exception):
                    logger.error(f"Error analyzing ticker {tickers[i]}", error=str(insight))
                    if self.log_broadcaster:
                        await self.log_broadcaster.error(
                            f"Failed to analyze {tickers[i]}: {str(insight)}",
                            error_details={"ticker": tickers[i], "error": str(insight)}
                        )
                else:
                    # Format insight with 2 decimal places
                    formatted_insight = format_ticker_insight(insight.model_dump())
                    valid_insights.append(TickerInsight(**formatted_insight))
            
            if not valid_insights:
                raise Exception("Failed to analyze any tickers. Please try again.")
            
            # Emit final completion message
            if self.log_broadcaster:
                await self.log_broadcaster.all_analysis_complete(len(valid_insights))
            
            execution_time = time.time() - start_time
            logger.info("Yahoo Finance analysis completed", 
                       request_id=request_id,
                       execution_time=execution_time,
                       insights_count=len(valid_insights))
            
            return valid_insights
            
        except Exception as e:
            logger.error("Yahoo Finance analysis failed", 
                        request_id=request_id,
                        error=str(e))
            if self.log_broadcaster:
                await self.log_broadcaster.error(
                    f"Analysis failed: {str(e)}",
                    error_details={"error": str(e)}
                )
            raise
