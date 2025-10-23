"""
Research Orchestrator - Manages the multi-agent workflow for stock research.
"""
import asyncio
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from backend.app.models import (
    TickerInsight, 
    AgentTrace, 
    AgentStep, 
    SourceInfo,
    StanceType,
    ConfidenceLevel
)
from backend.agents.base_agent import BaseResearchAgent
from backend.agents.news_agent import NewsAgent
from backend.agents.filings_agent import FilingsAgent
from backend.agents.earnings_agent import EarningsAgent
from backend.agents.insider_agent import InsiderAgent
from backend.agents.patents_agent import PatentsAgent
from backend.agents.price_agent import PriceAgent
from backend.agents.synthesis_agent import SynthesisAgent
from backend.config.settings import get_settings

logger = structlog.get_logger()


class ResearchState:
    """State object for the research workflow."""
    
    def __init__(self):
        self.query: str = ""
        self.tickers: List[str] = []
        self.max_iterations: int = 3
        self.timeout_seconds: int = 30
        self.request_id: str = ""
        
        # Results storage
        self.agent_results: Dict[str, Dict[str, Any]] = {}
        self.insights: List[TickerInsight] = []
        
        # Execution tracking
        self.start_time: float = 0.0
        self.current_step: str = ""
        self.errors: List[str] = []
        self.warnings: List[str] = []


class ResearchOrchestrator:
    """
    Orchestrates the multi-agent research workflow using LangGraph.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.settings.gemini_api_key,
            temperature=0.1
        )
        
        # Initialize agents
        self.agents = {
            "news": NewsAgent(self.llm),
            "filings": FilingsAgent(self.llm),
            "earnings": EarningsAgent(self.llm),
            "insider": InsiderAgent(self.llm),
            "patents": PatentsAgent(self.llm),
            "price": PriceAgent(self.llm)
        }
        
        self.synthesis_agent = SynthesisAgent(self.llm)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
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
    
    def _build_workflow(self) -> CompiledStateGraph:
        """Build the LangGraph workflow for research orchestration."""
        
        def parse_query(state: ResearchState) -> ResearchState:
            """Parse the input query and extract tickers."""
            logger.info("Parsing query", query=state.query)
            state.tickers = self._extract_tickers(state.query)
            state.current_step = f"Extracted tickers: {', '.join(state.tickers)}"
            
            if not state.tickers:
                state.errors.append("No valid stock tickers found in query")
                logger.warning("No tickers found", query=state.query)
            
            return state
        
        def run_parallel_research(state: ResearchState) -> ResearchState:
            """Run parallel research agents for each ticker."""
            logger.info("Starting parallel research", 
                       tickers=state.tickers, 
                       agent_count=len(self.agents))
            
            state.current_step = "Running parallel research agents"
            
            # Create tasks for each ticker-agent combination
            async def run_agent_for_ticker(agent_name: str, agent: BaseResearchAgent, ticker: str):
                try:
                    logger.info("Running agent", agent=agent_name, ticker=ticker)
                    result = await agent.research(
                        ticker=ticker,
                        query=state.query,
                        max_iterations=state.max_iterations
                    )
                    return agent_name, ticker, result
                except Exception as e:
                    logger.error("Agent failed", agent=agent_name, ticker=ticker, error=str(e))
                    return agent_name, ticker, {"error": str(e)}
            
            # Run all agent-ticker combinations in parallel
            async def run_all_research():
                tasks = []
                for ticker in state.tickers:
                    for agent_name, agent in self.agents.items():
                        task = run_agent_for_ticker(agent_name, agent, ticker)
                        tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Organize results by ticker
                for result in results:
                    if isinstance(result, Exception):
                        state.errors.append(f"Research task failed: {str(result)}")
                        continue
                    
                    agent_name, ticker, agent_result = result
                    
                    if ticker not in state.agent_results:
                        state.agent_results[ticker] = {}
                    
                    state.agent_results[ticker][agent_name] = agent_result
            
            # Run the async research
            try:
                asyncio.run(run_all_research())
            except Exception as e:
                state.errors.append(f"Parallel research failed: {str(e)}")
                logger.error("Parallel research failed", error=str(e))
            
            return state
        
        def synthesize_insights(state: ResearchState) -> ResearchState:
            """Synthesize research results into actionable insights."""
            logger.info("Synthesizing insights", ticker_count=len(state.tickers))
            state.current_step = "Synthesizing insights"
            
            try:
                # Process each ticker
                for ticker in state.tickers:
                    if ticker not in state.agent_results:
                        state.warnings.append(f"No research results for ticker {ticker}")
                        continue
                    
                    # Get agent results for this ticker
                    ticker_results = state.agent_results[ticker]
                    
                    # Synthesize using the synthesis agent
                    insight = asyncio.run(self.synthesis_agent.synthesize(
                        ticker=ticker,
                        agent_results=ticker_results,
                        query=state.query
                    ))
                    
                    state.insights.append(insight)
                
            except Exception as e:
                state.errors.append(f"Synthesis failed: {str(e)}")
                logger.error("Synthesis failed", error=str(e))
            
            return state
        
        # Build the graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("parse_query", parse_query)
        workflow.add_node("run_research", run_parallel_research)
        workflow.add_node("synthesize", synthesize_insights)
        
        # Add edges
        workflow.add_edge("parse_query", "run_research")
        workflow.add_edge("run_research", "synthesize")
        workflow.add_edge("synthesize", END)
        
        # Set entry point
        workflow.set_entry_point("parse_query")
        
        return workflow.compile()
    
    async def analyze(
        self, 
        query: str, 
        max_iterations: int = 3, 
        timeout_seconds: int = 30,
        request_id: str = ""
    ) -> List[TickerInsight]:
        """
        Run the complete stock analysis workflow.
        
        Args:
            query: Natural language query with stock tickers
            max_iterations: Maximum iterations per agent
            timeout_seconds: Timeout for the entire analysis
            request_id: Unique request identifier
            
        Returns:
            List of ticker insights
        """
        start_time = time.time()
        
        logger.info("Starting stock analysis", 
                   query=query, 
                   max_iterations=max_iterations,
                   timeout_seconds=timeout_seconds,
                   request_id=request_id)
        
        # Initialize state
        state = ResearchState()
        state.query = query
        state.max_iterations = max_iterations
        state.timeout_seconds = timeout_seconds
        state.request_id = request_id
        state.start_time = start_time
        
        try:
            # Run the workflow with timeout
            result = await asyncio.wait_for(
                self._run_workflow_async(state),
                timeout=timeout_seconds
            )
            
            execution_time = time.time() - start_time
            logger.info("Analysis completed", 
                       request_id=request_id,
                       execution_time=execution_time,
                       insights_count=len(result.insights))
            
            return result.insights
            
        except asyncio.TimeoutError:
            logger.error("Analysis timed out", 
                        request_id=request_id,
                        timeout_seconds=timeout_seconds)
            raise Exception(f"Analysis timed out after {timeout_seconds} seconds")
        
        except Exception as e:
            logger.error("Analysis failed", 
                        request_id=request_id,
                        error=str(e))
            raise
    
    async def _run_workflow_async(self, state: ResearchState) -> ResearchState:
        """Run the workflow asynchronously."""
        # Since LangGraph doesn't natively support async, we'll simulate it
        # In a real implementation, you'd use LangGraph's async capabilities
        
        # For now, we'll run a simplified version
        try:
            # Parse query
            state.tickers = self._extract_tickers(state.query)
            
            if not state.tickers:
                raise Exception("No valid stock tickers found in query")
            
            # Run research for each ticker
            for ticker in state.tickers:
                ticker_results = {}
                
                # Run each agent for this ticker
                for agent_name, agent in self.agents.items():
                    try:
                        result = await agent.research(
                            ticker=ticker,
                            query=state.query,
                            max_iterations=state.max_iterations
                        )
                        ticker_results[agent_name] = result
                    except Exception as e:
                        logger.error("Agent failed", 
                                   agent=agent_name, 
                                   ticker=ticker, 
                                   error=str(e))
                        ticker_results[agent_name] = {"error": str(e)}
                
                state.agent_results[ticker] = ticker_results
                
                # Synthesize insights for this ticker
                insight = await self.synthesis_agent.synthesize(
                    ticker=ticker,
                    agent_results=ticker_results,
                    query=state.query
                )
                
                state.insights.append(insight)
            
            return state
            
        except Exception as e:
            logger.error("Workflow execution failed", error=str(e))
            raise
