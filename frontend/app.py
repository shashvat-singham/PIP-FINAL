"""
Streamlit frontend for the Stock Research Chatbot.
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page configuration
st.set_page_config(
    page_title="Stock Research Chatbot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .ticker-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stance-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stance-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stance-hold {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .confidence-high {
        background-color: #cce5ff;
        color: #004085;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .confidence-medium {
        background-color: #e2e3e5;
        color: #383d41;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .confidence-low {
        background-color: #f5c6cb;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📈 Stock Research Chatbot</h1>
        <p>AI-powered multi-agent research for informed investment decisions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        max_iterations = st.slider(
            "Max Iterations per Agent",
            min_value=1,
            max_value=5,
            value=3,
            help="Maximum number of research iterations each agent will perform"
        )
        
        timeout_seconds = st.slider(
            "Analysis Timeout (seconds)",
            min_value=30,
            max_value=300,
            value=60,
            help="Maximum time to wait for analysis completion"
        )
        
        st.header("📊 Available Agents")
        st.info("""
        **News Agent**: Recent news and press releases
        
        **Filings Agent**: SEC filings and regulatory documents
        
        **Earnings Agent**: Earnings calls and transcripts
        
        **Insider Agent**: Insider trading and ownership
        
        **Patents Agent**: Patents and research papers
        
        **Price Agent**: Technical analysis and price trends
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Research Query")
        
        # Query input
        query = st.text_area(
            "Enter your research query with stock tickers:",
            placeholder="Analyze NVDA, AMD, TSM for AI datacenter demand; short-term outlook 3-6 months...",
            height=100,
            help="Include stock tickers and describe what you want to research about them"
        )
        
        # Analysis button
        if st.button("🧠 Start Analysis", type="primary", disabled=not query.strip()):
            analyze_stocks(query, max_iterations, timeout_seconds)
    
    with col2:
        st.header("📈 Quick Stats")
        
        if "analysis_result" in st.session_state:
            result = st.session_state.analysis_result
            
            # Display metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Tickers Analyzed", len(result.get("tickers_analyzed", [])))
                st.metric("Agents Used", len(result.get("agents_used", [])))
            
            with col_b:
                analysis_time = result.get("total_latency_ms", 0) / 1000
                st.metric("Analysis Time", f"{analysis_time:.1f}s")
                
                success_rate = 100 if result.get("success", False) else 0
                st.metric("Success Rate", f"{success_rate}%")
    
    # Display results
    if "analysis_result" in st.session_state:
        display_analysis_results(st.session_state.analysis_result)

def analyze_stocks(query: str, max_iterations: int, timeout_seconds: int):
    """Perform stock analysis using the backend API."""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🚀 Starting analysis...")
        progress_bar.progress(10)
        
        # Make API request
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={
                "query": query,
                "max_iterations": max_iterations,
                "timeout_seconds": timeout_seconds
            },
            timeout=timeout_seconds + 10
        )
        
        progress_bar.progress(50)
        status_text.text("🔄 Processing results...")
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.analysis_result = result
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis completed successfully!")
            
            # Auto-clear status after 2 seconds
            time.sleep(2)
            status_text.empty()
            progress_bar.empty()
            
            st.rerun()
            
        else:
            st.error(f"Analysis failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        st.error("Analysis timed out. Please try again with a shorter timeout or simpler query.")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the analysis service. Please ensure the backend is running.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        progress_bar.empty()
        status_text.empty()

def display_analysis_results(result: Dict[str, Any]):
    """Display the analysis results in a structured format."""
    
    st.header("📊 Analysis Results")
    
    insights = result.get("insights", [])
    
    if not insights:
        st.warning("No insights were generated. Please try a different query.")
        return
    
    # Create tabs for each ticker
    ticker_tabs = st.tabs([insight["ticker"] for insight in insights])
    
    for i, (tab, insight) in enumerate(zip(ticker_tabs, insights)):
        with tab:
            display_ticker_insight(insight)
    
    # Cross-ticker comparison
    if len(insights) > 1:
        st.header("🔄 Cross-Ticker Comparison")
        display_comparison_table(insights)
    
    # Agent execution details
    st.header("🤖 Agent Execution Details")
    display_agent_traces(insights)

def display_ticker_insight(insight: Dict[str, Any]):
    """Display detailed insight for a single ticker."""
    
    ticker = insight["ticker"]
    company_name = insight.get("company_name", "")
    
    # Header with ticker and stance
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"{ticker}")
        if company_name:
            st.caption(company_name)
    
    with col2:
        stance = insight.get("stance", "hold").upper()
        stance_class = f"stance-{stance.lower()}"
        st.markdown(f'<span class="{stance_class}">{stance}</span>', unsafe_allow_html=True)
    
    with col3:
        confidence = insight.get("confidence", "medium").upper()
        confidence_class = f"confidence-{confidence.lower()}"
        st.markdown(f'<span class="{confidence_class}">{confidence} CONFIDENCE</span>', unsafe_allow_html=True)
    
    # Summary
    st.subheader("📝 Executive Summary")
    st.write(insight.get("summary", "No summary available."))
    
    # Rationale
    st.subheader("💭 Investment Rationale")
    st.write(insight.get("rationale", "No rationale provided."))
    
    # Three columns for drivers, risks, catalysts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🚀 Key Drivers")
        drivers = insight.get("key_drivers", [])
        if drivers:
            for driver in drivers:
                st.write(f"• {driver}")
        else:
            st.write("No key drivers identified.")
    
    with col2:
        st.subheader("⚠️ Risks")
        risks = insight.get("risks", [])
        if risks:
            for risk in risks:
                st.write(f"• {risk}")
        else:
            st.write("No significant risks identified.")
    
    with col3:
        st.subheader("⚡ Catalysts")
        catalysts = insight.get("catalysts", [])
        if catalysts:
            for catalyst in catalysts:
                st.write(f"• {catalyst}")
        else:
            st.write("No upcoming catalysts identified.")
    
    # Sources
    st.subheader("📚 Sources")
    sources = insight.get("sources", [])
    if sources:
        for i, source in enumerate(sources[:5], 1):  # Limit to top 5 sources
            with st.expander(f"Source {i}: {source.get('title', 'Untitled')}"):
                st.write(f"**URL:** {source.get('url', 'N/A')}")
                if source.get("published_at"):
                    pub_date = datetime.fromisoformat(source["published_at"].replace('Z', '+00:00'))
                    st.write(f"**Published:** {pub_date.strftime('%Y-%m-%d %H:%M')}")
                if source.get("snippet"):
                    st.write(f"**Snippet:** {source['snippet']}")
    else:
        st.write("No sources available.")

def display_comparison_table(insights: List[Dict[str, Any]]):
    """Display a comparison table of all analyzed tickers."""
    
    comparison_data = []
    
    for insight in insights:
        comparison_data.append({
            "Ticker": insight["ticker"],
            "Company": insight.get("company_name", ""),
            "Stance": insight.get("stance", "hold").upper(),
            "Confidence": insight.get("confidence", "medium").upper(),
            "Key Drivers": len(insight.get("key_drivers", [])),
            "Risks": len(insight.get("risks", [])),
            "Catalysts": len(insight.get("catalysts", [])),
            "Sources": len(insight.get("sources", []))
        })
    
    df = pd.DataFrame(comparison_data)
    
    # Style the dataframe
    def style_stance(val):
        if val == "BUY":
            return "background-color: #d4edda; color: #155724"
        elif val == "SELL":
            return "background-color: #f8d7da; color: #721c24"
        else:
            return "background-color: #fff3cd; color: #856404"
    
    def style_confidence(val):
        if val == "HIGH":
            return "background-color: #cce5ff; color: #004085"
        elif val == "LOW":
            return "background-color: #f5c6cb; color: #721c24"
        else:
            return "background-color: #e2e3e5; color: #383d41"
    
    styled_df = df.style.applymap(style_stance, subset=["Stance"]) \
                       .applymap(style_confidence, subset=["Confidence"])
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Create a simple visualization
    fig = px.scatter(
        df, 
        x="Key Drivers", 
        y="Risks",
        size="Sources",
        color="Stance",
        hover_name="Ticker",
        title="Risk vs. Drivers Analysis",
        color_discrete_map={
            "BUY": "green",
            "HOLD": "orange", 
            "SELL": "red"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_agent_traces(insights: List[Dict[str, Any]]):
    """Display agent execution traces."""
    
    for insight in insights:
        ticker = insight["ticker"]
        traces = insight.get("agent_traces", [])
        
        if not traces:
            continue
            
        st.subheader(f"🔍 {ticker} Agent Execution")
        
        for trace in traces:
            agent_type = trace.get("agent_type", "unknown")
            success = trace.get("success", False)
            latency = trace.get("total_latency_ms", 0)
            
            with st.expander(f"{agent_type.title()} Agent - {'✅ Success' if success else '❌ Failed'} ({latency:.0f}ms)"):
                steps = trace.get("steps", [])
                
                if steps:
                    for step in steps:
                        st.write(f"**Step {step.get('step_number', 0)}:**")
                        st.write(f"*Thought:* {step.get('thought', 'N/A')}")
                        st.write(f"*Action:* {step.get('action', 'N/A')}")
                        st.write(f"*Observation:* {step.get('observation', 'N/A')}")
                        
                        step_latency = step.get("latency_ms", 0)
                        if step_latency:
                            st.caption(f"Step completed in {step_latency:.0f}ms")
                        
                        st.divider()
                else:
                    st.write("No execution steps recorded.")
                
                if trace.get("error_message"):
                    st.error(f"Error: {trace['error_message']}")

if __name__ == "__main__":
    main()
