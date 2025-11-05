"""
Streamlit frontend for the Stock Research Chatbot.
Professional UI matching React implementation with confirmation flow.
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page configuration
st.set_page_config(
    page_title="Stock Research Chatbot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Professional styling matching React UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 1.125rem;
        color: #64748b;
        margin-bottom: 1rem;
    }
    
    /* Card styling */
    .stCard {
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        background: white;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-buy {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .badge-sell {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    
    .badge-hold {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    
    .badge-high {
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    
    .badge-medium {
        background-color: #e9d5ff;
        color: #6b21a8;
        border: 1px solid #d8b4fe;
    }
    
    .badge-low {
        background-color: #e5e7eb;
        color: #374151;
        border: 1px solid #d1d5db;
    }
    
    .badge-blue {
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    
    /* Confirmation dialog styling */
    .confirmation-card {
        border: 2px solid #93c5fd;
        background: #eff6ff;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .confirmation-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
    }
    
    /* Ticker card header */
    .ticker-header {
        background: linear-gradient(90deg, #eff6ff 0%, #e0e7ff 100%);
        border-radius: 12px 12px 0 0;
        padding: 1.5rem;
        margin: -1.5rem -1.5rem 1.5rem -1.5rem;
    }
    
    .ticker-title {
        font-size: 1.875rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    
    .ticker-company {
        font-size: 1.125rem;
        color: #6b7280;
    }
    
    /* Source card */
    .source-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        background: white;
    }
    
    .source-title {
        font-weight: 600;
        font-size: 0.875rem;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    
    .source-snippet {
        font-size: 0.75rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    
    .source-date {
        font-size: 0.75rem;
        color: #9ca3af;
    }
    
    /* Agent trace styling */
    .agent-trace {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
    
    .agent-header {
        font-weight: 600;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .agent-step {
        margin-left: 1.5rem;
        border-left: 2px solid #e5e7eb;
        padding-left: 1rem;
        padding-bottom: 0.5rem;
        font-size: 0.875rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Textarea styling */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        font-size: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #3b82f6;
        border-radius: 9999px;
    }
    
    /* Alert styling */
    .alert-info {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .alert-error {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #991b1b;
    }
    
    .alert-success {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #166534;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "confirmation_prompt" not in st.session_state:
    st.session_state.confirmation_prompt = None
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "original_query" not in st.session_state:
    st.session_state.original_query = ""
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📈 Stock Research Chatbot</h1>
        <p class="main-subtitle">AI-powered multi-agent research with smart spelling correction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # New Feature Badge
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><span class="badge badge-blue">🆕 Gemini-Powered Smart Correction</span></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Query Input Card
    with st.container():
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### 🔍 Research Query")
        st.markdown('<p style="color: #64748b; margin-bottom: 1rem;">Enter company names or tickers - typos are OK! (e.g., "Analyze matae for 1 month" or "Compare microsft and gogle")</p>', unsafe_allow_html=True)
        
        query = st.text_area(
            "",
            value=st.session_state.query_input,
            placeholder='Try: "Analyze matae for 1 month" or "Compare microsft, gogle, and amazn"',
            height=100,
            disabled=st.session_state.confirmation_prompt is not None,
            key="query_textarea",
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            analyze_button = st.button(
                "🧠 Analyze",
                type="primary",
                disabled=not query.strip() or st.session_state.confirmation_prompt is not None,
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle analyze button click
    if analyze_button and query.strip():
        st.session_state.query_input = query
        st.session_state.original_query = query
        analyze_stocks(query)
    
    # Confirmation Dialog
    if st.session_state.confirmation_prompt:
        display_confirmation_dialog(st.session_state.confirmation_prompt)
    
    # Display results
    if st.session_state.analysis_result:
        display_analysis_results(st.session_state.analysis_result)

def analyze_stocks(query: str, confirmation_response: str = None):
    """Perform stock analysis using the backend API."""
    
    # Progress tracking
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        status_text.markdown('<div class="alert-info">🚀 Starting analysis...</div>', unsafe_allow_html=True)
        progress_bar.progress(10)
        
        # Prepare request body
        request_body = {
            "query": st.session_state.original_query if confirmation_response else query,
            "max_iterations": 3,
            "timeout_seconds": 60
        }
        
        # Add conversation fields if this is a confirmation response
        if confirmation_response and st.session_state.conversation_id:
            request_body["conversation_id"] = st.session_state.conversation_id
            request_body["confirmation_response"] = confirmation_response
        
        # Make API request
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=request_body,
            timeout=70
        )
        
        progress_bar.progress(50)
        status_text.markdown('<div class="alert-info">🔄 Processing results...</div>', unsafe_allow_html=True)
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if confirmation is needed
            if result.get("needs_confirmation") and result.get("confirmation_prompt"):
                st.session_state.confirmation_prompt = result["confirmation_prompt"]
                st.session_state.conversation_id = result["confirmation_prompt"].get("conversation_id")
                progress_bar.progress(0)
                status_text.markdown('<div class="alert-info">⏳ Waiting for confirmation...</div>', unsafe_allow_html=True)
                time.sleep(1)
                status_text.empty()
                progress_bar.empty()
                st.rerun()
            else:
                # Normal analysis result
                st.session_state.analysis_result = result
                st.session_state.confirmation_prompt = None
                st.session_state.conversation_id = None
                
                progress_bar.progress(100)
                status_text.markdown('<div class="alert-success">✅ Analysis completed successfully!</div>', unsafe_allow_html=True)
                
                # Auto-clear status after 2 seconds
                time.sleep(2)
                status_text.empty()
                progress_bar.empty()
                
                st.rerun()
        else:
            error_msg = f"Analysis failed: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('detail', response.text)}"
            except:
                error_msg += f" - {response.text}"
            st.markdown(f'<div class="alert-error">❌ {error_msg}</div>', unsafe_allow_html=True)
            
    except requests.exceptions.Timeout:
        st.markdown('<div class="alert-error">⏱️ Analysis timed out. Please try again with a shorter timeout or simpler query.</div>', unsafe_allow_html=True)
    except requests.exceptions.ConnectionError:
        st.markdown('<div class="alert-error">🔌 Could not connect to the analysis service. Please ensure the backend is running.</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f'<div class="alert-error">❌ An error occurred: {str(e)}</div>', unsafe_allow_html=True)
    finally:
        progress_bar.empty()
        status_text.empty()

def display_confirmation_dialog(prompt: Dict[str, Any]):
    """Display confirmation dialog for smart correction."""
    
    st.markdown('<div class="confirmation-card">', unsafe_allow_html=True)
    st.markdown('<div class="confirmation-title">❓ Confirmation Needed</div>', unsafe_allow_html=True)
    
    # Display message
    st.markdown(f'<div class="alert-info"><strong>Did you mean this?</strong><br>{prompt.get("message", "")}</div>', unsafe_allow_html=True)
    
    # Display suggestion details if available
    if prompt.get("suggestion"):
        suggestion = prompt["suggestion"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Original Input</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family: monospace; font-size: 1.125rem; color: #111827;">{suggestion.get("original_input", "")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Suggested</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.125rem; font-weight: 600; color: #111827;">{suggestion.get("corrected_name", "")} ({suggestion.get("ticker", "")})</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Confidence</div>', unsafe_allow_html=True)
            confidence = suggestion.get("confidence", "medium")
            badge_class = f"badge-{confidence}"
            st.markdown(f'<span class="badge {badge_class}">{confidence.upper()}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Explanation</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.875rem; color: #4b5563;">{suggestion.get("explanation", "")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("👎 No, that's not right", use_container_width=True):
            st.session_state.confirmation_prompt = None
            st.session_state.conversation_id = None
            analyze_stocks(st.session_state.original_query, "No")
    
    with col3:
        ticker = prompt.get("suggestion", {}).get("ticker", "this")
        if st.button(f"👍 Yes, proceed with {ticker}", type="primary", use_container_width=True):
            st.session_state.confirmation_prompt = None
            analyze_stocks(st.session_state.original_query, "Yes")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_analysis_results(result: Dict[str, Any]):
    """Display the analysis results in a structured format."""
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    insights = result.get("insights", [])
    
    if not insights:
        st.markdown('<div class="alert-info">⚠️ No insights were generated. Please try a different query.</div>', unsafe_allow_html=True)
        return
    
    # Summary metrics
    st.markdown("### 📊 Analysis Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Tickers Analyzed</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(result.get("tickers_analyzed", []))}</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 0.5rem;">🏢</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Agents Used</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(result.get("agents_used", []))}</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 0.5rem;">🤖</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Analysis Time</div>', unsafe_allow_html=True)
        analysis_time = result.get("total_latency_ms", 0) / 1000
        st.markdown(f'<div class="metric-value">{analysis_time:.1f}s</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 0.5rem;">⏱️</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ticker insights
    st.markdown("### 📈 Ticker Insights")
    
    for insight in insights:
        display_ticker_insight(insight)

def display_ticker_insight(insight: Dict[str, Any]):
    """Display detailed insight for a single ticker."""
    
    ticker = insight["ticker"]
    company_name = insight.get("company_name", "")
    stance = insight.get("stance", "hold")
    confidence = insight.get("confidence", "medium")
    
    with st.container():
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        
        # Header
        st.markdown('<div class="ticker-header">', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f'<div class="ticker-title">{ticker}</div>', unsafe_allow_html=True)
            if company_name:
                st.markdown(f'<div class="ticker-company">{company_name}</div>', unsafe_allow_html=True)
        
        with col2:
            stance_icon = {"buy": "📈", "sell": "📉", "hold": "➖"}.get(stance, "➖")
            st.markdown(f'<span class="badge badge-{stance}">{stance_icon} {stance.upper()}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="badge badge-{confidence}">{confidence.upper()} CONFIDENCE</span>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Summary", "🚀 Drivers", "⚠️ Risks", "⚡ Catalysts", "📚 Sources"])
        
        with tab1:
            # Price and Market Data
            if insight.get("current_price"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div style="background: #f9fafb; padding: 1rem; border-radius: 8px;">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Current Price</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size: 1.25rem; font-weight: 700;">${insight["current_price"]:.2f}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    if insight.get("market_cap"):
                        st.markdown('<div style="background: #f9fafb; padding: 1rem; border-radius: 8px;">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Market Cap</div>', unsafe_allow_html=True)
                        market_cap = insight["market_cap"]
                        if market_cap >= 1e12:
                            cap_str = f"${market_cap / 1e12:.2f}T"
                        elif market_cap >= 1e9:
                            cap_str = f"${market_cap / 1e9:.2f}B"
                        elif market_cap >= 1e6:
                            cap_str = f"${market_cap / 1e6:.2f}M"
                        else:
                            cap_str = f"${market_cap:.2f}"
                        st.markdown(f'<div style="font-size: 1.25rem; font-weight: 700;">{cap_str}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    if insight.get("pe_ratio"):
                        st.markdown('<div style="background: #f9fafb; padding: 1rem; border-radius: 8px;">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">P/E Ratio</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-size: 1.25rem; font-weight: 700;">{insight["pe_ratio"]:.2f}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    if insight.get("trend"):
                        st.markdown('<div style="background: #f9fafb; padding: 1rem; border-radius: 8px;">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Trend</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-size: 1.25rem; font-weight: 700; text-transform: capitalize;">{insight["trend"]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Technical Levels
            if insight.get("support_levels") or insight.get("resistance_levels"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if insight.get("support_levels"):
                        st.markdown('<div style="background: #eff6ff; padding: 1rem; border-radius: 8px;">', unsafe_allow_html=True)
                        st.markdown('<div style="font-weight: 600; margin-bottom: 0.5rem;">Support Levels</div>', unsafe_allow_html=True)
                        for level in insight["support_levels"]:
                            st.markdown(f'<span class="badge" style="background: #dcfce7; color: #166534;">${level:.2f}</span>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    if insight.get("resistance_levels"):
                        st.markdown('<div style="background: #eff6ff; padding: 1rem; border-radius: 8px;">', unsafe_allow_html=True)
                        st.markdown('<div style="font-weight: 600; margin-bottom: 0.5rem;">Resistance Levels</div>', unsafe_allow_html=True)
                        for level in insight["resistance_levels"]:
                            st.markdown(f'<span class="badge" style="background: #fee2e2; color: #991b1b;">${level:.2f}</span>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Summary and Rationale
            st.markdown("#### Executive Summary")
            st.markdown(f'<p style="color: #374151; line-height: 1.6;">{insight.get("summary", "No summary available.")}</p>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Investment Rationale")
            st.markdown(f'<p style="color: #374151; line-height: 1.6;">{insight.get("rationale", "No rationale provided.")}</p>', unsafe_allow_html=True)
        
        with tab2:
            drivers = insight.get("key_drivers", [])
            if drivers:
                for driver in drivers:
                    st.markdown(f'<div style="display: flex; align-items: start; gap: 0.5rem; margin-bottom: 0.75rem;"><span style="color: #16a34a; font-size: 1.25rem;">✓</span><span style="color: #374151;">{driver}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #6b7280;">No key drivers identified.</p>', unsafe_allow_html=True)
        
        with tab3:
            risks = insight.get("risks", [])
            if risks:
                for risk in risks:
                    st.markdown(f'<div style="display: flex; align-items: start; gap: 0.5rem; margin-bottom: 0.75rem;"><span style="color: #dc2626; font-size: 1.25rem;">⚠</span><span style="color: #374151;">{risk}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #6b7280;">No significant risks identified.</p>', unsafe_allow_html=True)
        
        with tab4:
            catalysts = insight.get("catalysts", [])
            if catalysts:
                for catalyst in catalysts:
                    st.markdown(f'<div style="display: flex; align-items: start; gap: 0.5rem; margin-bottom: 0.75rem;"><span style="color: #2563eb; font-size: 1.25rem;">⚡</span><span style="color: #374151;">{catalyst}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #6b7280;">No upcoming catalysts identified.</p>', unsafe_allow_html=True)
        
        with tab5:
            sources = insight.get("sources", [])
            if sources:
                for i, source in enumerate(sources[:10], 1):
                    st.markdown('<div class="source-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="source-title">{source.get("title", "Untitled")}</div>', unsafe_allow_html=True)
                    if source.get("snippet"):
                        st.markdown(f'<div class="source-snippet">{source["snippet"]}</div>', unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        if source.get("published_at"):
                            try:
                                pub_date = datetime.fromisoformat(source["published_at"].replace('Z', '+00:00'))
                                st.markdown(f'<div class="source-date">Published: {pub_date.strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
                            except:
                                pass
                    with col_b:
                        if source.get("url"):
                            st.markdown(f'<a href="{source["url"]}" target="_blank" style="font-size: 0.875rem; color: #2563eb;">🔗 View</a>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #6b7280;">No sources available.</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
