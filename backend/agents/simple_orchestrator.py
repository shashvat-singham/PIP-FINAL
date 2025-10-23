"""
Simplified Research Orchestrator for testing and demonstration.
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

logger = structlog.get_logger()


class SimpleResearchOrchestrator:
    """
    Simplified orchestrator that generates sample data for testing.
    """
    
    def __init__(self):
        self.settings = get_settings()
    
    def _extract_tickers(self, query: str) -> List[str]:
        """Extract stock tickers from the query."""
        # Simple regex to find ticker symbols (3-5 uppercase letters)
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        potential_tickers = re.findall(ticker_pattern, query)
        
        # Filter out common words that might match the pattern
        common_words = {"THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "HAD", "BUT", "WHAT", "SO", "UP", "OUT", "IF", "ABOUT", "WHO", "GET", "WHICH", "GO", "ME", "WHEN", "MAKE", "CAN", "LIKE", "TIME", "NO", "JUST", "HIM", "KNOW", "TAKE", "PEOPLE", "INTO", "YEAR", "YOUR", "GOOD", "SOME", "COULD", "THEM", "SEE", "OTHER", "THAN", "THEN", "NOW", "LOOK", "ONLY", "COME", "ITS", "OVER", "THINK", "ALSO", "BACK", "AFTER", "USE", "TWO", "HOW", "OUR", "WORK", "FIRST", "WELL", "WAY", "EVEN", "NEW", "WANT", "BECAUSE", "ANY", "THESE", "GIVE", "DAY", "MOST", "US", "BEST"}
        
        tickers = [ticker for ticker in potential_tickers if ticker not in common_words]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tickers = []
        for ticker in tickers:
            if ticker not in seen:
                seen.add(ticker)
                unique_tickers.append(ticker)
        
        return unique_tickers
    
    def _generate_sample_sources(self, ticker: str) -> List[SourceInfo]:
        """Generate sample sources for a ticker."""
        return [
            SourceInfo(
                url=f"https://finance.yahoo.com/{ticker.lower()}-earnings-q3-2024",
                title=f"{ticker} Reports Strong Q3 Earnings, Beats Expectations",
                published_at=datetime(2024, 10, 8, 10, 30),
                snippet=f"{ticker} reported quarterly earnings that exceeded analyst expectations, driven by strong revenue growth and improved margins."
            ),
            SourceInfo(
                url=f"https://www.marketwatch.com/{ticker.lower()}-analyst-upgrade",
                title=f"Analyst Upgrades {ticker} to Buy Rating",
                published_at=datetime(2024, 10, 7, 14, 15),
                snippet=f"Leading investment firm upgrades {ticker} to Buy rating with a price target of $150, citing strong fundamentals."
            ),
            SourceInfo(
                url=f"https://www.reuters.com/{ticker.lower()}-product-launch",
                title=f"{ticker} Announces New Product Launch",
                published_at=datetime(2024, 10, 6, 9, 0),
                snippet=f"{ticker} unveiled its latest product innovation, expected to drive significant revenue growth."
            )
        ]
    
    def _generate_sample_agent_traces(self, ticker: str) -> List[AgentTrace]:
        """Generate sample agent traces for a ticker."""
        traces = []
        
        # News Agent Trace
        news_steps = [
            AgentStep(
                step_number=1,
                thought=f"I need to search for recent news about {ticker} to understand current market sentiment and developments.",
                action=f"web_search: {ticker} recent news earnings 2024",
                observation=f"Found 3 recent articles about {ticker}: Strong Q3 earnings beat, analyst upgrade to Buy rating, and new product launch announcement.",
                sources=self._generate_sample_sources(ticker)[:1],
                latency_ms=1250.5
            ),
            AgentStep(
                step_number=2,
                thought="The earnings beat and analyst upgrade are positive signals. Let me gather more details about the financial performance.",
                action=f"web_search: {ticker} Q3 2024 earnings financial results",
                observation=f"{ticker} reported revenue growth of 15% YoY and EPS beat by $0.05. Management raised full-year guidance.",
                sources=self._generate_sample_sources(ticker)[1:2],
                latency_ms=980.3
            )
        ]
        
        news_trace = AgentTrace(
            agent_type="news",
            ticker=ticker,
            steps=news_steps,
            success=True,
            total_latency_ms=2230.8
        )
        traces.append(news_trace)
        
        # Price Agent Trace
        price_steps = [
            AgentStep(
                step_number=1,
                thought=f"I should analyze the recent price movement and technical indicators for {ticker}.",
                action=f"stock_data: {ticker} price technical analysis",
                observation=f"{ticker} is trading near 52-week highs with strong momentum. RSI at 65 indicates bullish but not overbought conditions.",
                sources=[],
                latency_ms=850.2
            )
        ]
        
        price_trace = AgentTrace(
            agent_type="price",
            ticker=ticker,
            steps=price_steps,
            success=True,
            total_latency_ms=850.2
        )
        traces.append(price_trace)
        
        return traces
    
    def _generate_sample_insight(self, ticker: str, query: str) -> TickerInsight:
        """Generate a sample insight for a ticker."""
        
        # Determine stance based on ticker (for demo purposes)
        stance_map = {
            "AAPL": StanceType.BUY,
            "NVDA": StanceType.BUY,
            "TSLA": StanceType.HOLD,
            "META": StanceType.BUY,
            "GOOGL": StanceType.HOLD,
            "MSFT": StanceType.BUY,
            "AMZN": StanceType.HOLD
        }
        
        stance = stance_map.get(ticker, StanceType.HOLD)
        confidence = ConfidenceLevel.HIGH if stance == StanceType.BUY else ConfidenceLevel.MEDIUM
        
        # Generate company name
        company_names = {
            "AAPL": "Apple Inc.",
            "NVDA": "NVIDIA Corporation",
            "TSLA": "Tesla, Inc.",
            "META": "Meta Platforms, Inc.",
            "GOOGL": "Alphabet Inc.",
            "MSFT": "Microsoft Corporation",
            "AMZN": "Amazon.com, Inc."
        }
        
        company_name = company_names.get(ticker, f"{ticker} Corporation")
        
        return TickerInsight(
            ticker=ticker,
            company_name=company_name,
            stance=stance,
            confidence=confidence,
            summary=f"Based on recent analysis, {ticker} shows strong fundamentals with positive earnings momentum and favorable analyst sentiment. The company's strategic initiatives and market position support a {stance.value.lower()} recommendation.",
            rationale=f"The {stance.value.lower()} rating is based on: (1) Strong Q3 earnings beat with 15% revenue growth, (2) Positive analyst upgrades and price target increases, (3) Successful product launches driving future growth, and (4) Strong technical momentum with the stock trading near 52-week highs.",
            key_drivers=[
                "Strong Q3 earnings performance with revenue beat",
                "Positive analyst sentiment and rating upgrades",
                "Successful new product launches and innovation pipeline",
                "Strong market position in key growth segments",
                "Improved operational efficiency and margin expansion"
            ],
            risks=[
                "Potential market volatility and macroeconomic headwinds",
                "Increased competition in core business segments",
                "Regulatory scrutiny and compliance costs",
                "Supply chain disruptions and cost inflation",
                "Currency exchange rate fluctuations"
            ],
            catalysts=[
                "Upcoming product launches and market expansion",
                "Potential strategic partnerships and acquisitions",
                "Earnings guidance updates and investor communications",
                "Industry trends and technological advancements",
                "Market share gains and competitive positioning"
            ],
            sources=self._generate_sample_sources(ticker),
            agent_traces=self._generate_sample_agent_traces(ticker)
        )
    
    async def analyze(
        self, 
        query: str, 
        max_iterations: int = 3, 
        timeout_seconds: int = 30,
        request_id: str = ""
    ) -> List[TickerInsight]:
        """
        Run a simplified stock analysis workflow that generates sample data.
        
        Args:
            query: Natural language query with stock tickers
            max_iterations: Maximum iterations per agent (ignored in this simple version)
            timeout_seconds: Timeout for the entire analysis
            request_id: Unique request identifier
            
        Returns:
            List of ticker insights
        """
        start_time = time.time()
        
        logger.info("Starting simplified stock analysis", 
                   query=query, 
                   request_id=request_id)
        
        try:
            # Extract tickers from query
            tickers = self._extract_tickers(query)
            
            if not tickers:
                raise Exception("No valid stock tickers found in query")
            
            logger.info("Extracted tickers", tickers=tickers, request_id=request_id)
            
            # Simulate some processing time
            await asyncio.sleep(2)
            
            # Generate insights for each ticker
            insights = []
            for ticker in tickers:
                insight = self._generate_sample_insight(ticker, query)
                insights.append(insight)
                
                # Add small delay between tickers
                await asyncio.sleep(0.5)
            
            execution_time = time.time() - start_time
            logger.info("Simplified analysis completed", 
                       request_id=request_id,
                       execution_time=execution_time,
                       insights_count=len(insights))
            
            return insights
            
        except Exception as e:
            logger.error("Simplified analysis failed", 
                        request_id=request_id,
                        error=str(e))
            raise
