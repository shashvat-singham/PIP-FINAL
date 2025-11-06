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

# Custom CSS - Professional purple theme styling
st.markdown("""
<style>
/* Global dark mode styling */
.main {
    background: radial-gradient(circle at top left, #0f172a 0%, #1e1b4b 100%);
    padding: 2rem 1rem;
    color: #e2e8f0;
}
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0rem !important;
}

/* Remove default focus outlines and blue boxes */
div:focus-visible, textarea:focus-visible, button:focus-visible {
    outline: none !important;
    box-shadow: none !important;
}

/* Header styling */
.main-header {
    text-align: center;
    padding: 1.5rem 0;
}
.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #f8fafc;
}
.main-subtitle {
    font-size: 1.125rem;
    color: #c7d2fe;
}

/* Research card */
.stCard {
    background: #111827;
    border: 1px solid #272d3d;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
}

/* Text area (input) */
.stTextArea textarea {
    background: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 10px;
    font-size: 1rem;
}
.stTextArea textarea:focus {
    border-color: #8b5cf6;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.4);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #a855f7);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
    padding: 0.6rem 2rem;
}
.stButton > button:hover {
    transform: translateY(-1px);
    background: linear-gradient(90deg, #8b5cf6, #c084fc);
    box-shadow: 0 0 10px rgba(168, 85, 247, 0.4);
}

/* Confirmation card */
.confirmation-card {
    border-radius: 16px;
    background: linear-gradient(145deg, #111827, #1e1b4b);
    border: 1px solid rgba(139,92,246,0.4);
    padding: 2rem;
    box-shadow: 0 0 15px rgba(139,92,246,0.2);
    margin-top: 1rem;
}
.confirmation-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #c084fc;
    margin-bottom: 1rem;
    text-align: center;
}
.confirmation-message {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 8px;
    padding: 1rem;
    color: #e2e8f0;
    margin-bottom: 1.5rem;
}

/* Metric cards inside confirmation */
.metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1rem;
    color: #f8fafc;
}

/* Confirmation buttons */
#confirm_btn button {
    background: linear-gradient(90deg, #7c3aed, #9333ea);
    color: #fff;
    border-radius: 8px;
    font-weight: 600;
    border: none;
}
#reject_btn button {
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid #475569;
    border-radius: 8px;
    font-weight: 600;
}
#reject_btn button:hover {
    background: #334155;
}

/* Alerts */
.alert-info {
    background: rgba(99,102,241,0.1);
    border-left: 4px solid #818cf8;
    color: #c7d2fe;
    border-radius: 8px;
    padding: 1rem;
}
.alert-error {
    background: rgba(239,68,68,0.1);
    border-left: 4px solid #ef4444;
    color: #fecaca;
    border-radius: 8px;
    padding: 1rem;
}
.alert-success {
    background: rgba(16,185,129,0.1);
    border-left: 4px solid #10b981;
    color: #a7f3d0;
    border-radius: 8px;
    padding: 1rem;
}

/* Text colors */
p, span, div, label {
    color: #f1f5f9 !important;
}

/* Hide branding */
#MainMenu, header, footer {visibility: hidden;}
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
         
        st.markdown('<h3 style="color: #ffffff;">🔍 Research Query</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; margin-bottom: 1rem;">Enter company names or tickers - typos are OK! (e.g., "Analyze matae for 1 month" or "Compare microsft and gogle")</p>', unsafe_allow_html=True)
        
        query = st.text_area(
            "Enter your research query:",
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
    
    if confirmation_response == "No":
        st.session_state.confirmation_prompt = None
        st.session_state.conversation_id = None
        st.session_state.analysis_result = None
        st.session_state.query_input = ""

        st.markdown(
            '<div class="alert-error">❌ Sorry, please type your query again.</div>',
            unsafe_allow_html=True
        )
        time.sleep(5.0)
        st.rerun()
        return

    # Progress tracking
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        status_text.markdown('<div class="alert-info">🚀 Starting analysis...</div>', unsafe_allow_html=True)
        progress_bar.progress(10)
        
        # Match React frontend request structure exactly
        request_body = {
            "query": st.session_state.original_query if confirmation_response else query,
            "max_iterations": 3,
            "timeout_seconds": 60
        }
        
        # Add conversation fields exactly like React frontend
        if confirmation_response and st.session_state.conversation_id:
            request_body["conversation_id"] = st.session_state.conversation_id
            request_body["confirmation_response"] = confirmation_response
        
        # Make API request with adjusted timeout
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=request_body,
            timeout=90  # Reduced timeout to match backend better
        )
        
        progress_bar.progress(50)
        status_text.markdown('<div class="alert-info">🔄 Processing results...</div>', unsafe_allow_html=True)
        
        if response.status_code == 200:
            try:
                result = response.json()
                
                # Handle the response based on its content
                if isinstance(result, dict):
                        # Handle response exactly like React frontend
                    if result.get("needs_confirmation") and result.get("confirmation_prompt"):
                        st.session_state.confirmation_prompt = result["confirmation_prompt"]
                        st.session_state.conversation_id = result["confirmation_prompt"].get("conversation_id")
                        if not confirmation_response:
                            st.session_state.original_query = query
                    else:
                        st.session_state.analysis_result = result
            except ValueError as e:
                status_text.markdown('<div class="alert-error">❌ Error processing response. Please try again.</div>', unsafe_allow_html=True)
                return
                
            if isinstance(result, dict):
                if result.get("needs_confirmation") and result.get("confirmation_prompt"):
                    # Store confirmation info and original query
                    st.session_state.confirmation_prompt = result["confirmation_prompt"]
                    st.session_state.conversation_id = result["confirmation_prompt"].get("conversation_id")
                    if not st.session_state.original_query:
                        st.session_state.original_query = query
                    
                    # Show confirmation UI
                    progress_bar.progress(0)
                    status_text.markdown('<div class="alert-info">⏳ Waiting for confirmation...</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    status_text.empty()
                    progress_bar.empty()
                    st.rerun()
                else:
                    # Process successful analysis
                    progress_bar.progress(75)
                    
                    # Store only the insights and related data
                    st.session_state.analysis_result = result
                    progress_bar.progress(100)
                    status_text.markdown('<div class="alert-success">✅ Analysis completed successfully!</div>', unsafe_allow_html=True)
                    
                    # Clear confirmation state
                    st.session_state.confirmation_prompt = None
                    st.session_state.conversation_id = None
                    st.session_state.original_query = None
                
                # Auto-clear status after 2 seconds
                time.sleep(2)
                status_text.empty()
                progress_bar.empty()
                
                st.rerun()
        else:
            try:
                error_detail = response.json()
                if isinstance(error_detail, dict):
                    error_msg = error_detail.get('detail', error_detail.get('error', 'Analysis failed'))
                else:
                    error_msg = "Analysis failed"
            except:
                error_msg = "Analysis failed. Please try again."
            
            # Show user-friendly error message
            st.markdown(f'<div class="alert-error">❌ {error_msg}</div>', unsafe_allow_html=True)
            
    except requests.exceptions.Timeout:
        status_text.markdown('<div class="alert-error">⏱️ The request is taking longer than expected. Please try a simpler query.</div>', unsafe_allow_html=True)
    except requests.exceptions.RequestException as e:
        if "RemoteDisconnected" in str(e):
            status_text.markdown('<div class="alert-error">🔌 Lost connection to the analysis service. Please try again.</div>', unsafe_allow_html=True)
        else:
            status_text.markdown(f'<div class="alert-error">🌐 Connection error: Please try again.</div>', unsafe_allow_html=True)
    except Exception as e:
        status_text.markdown(f'<div class="alert-error">❌ An error occurred: {str(e)}</div>', unsafe_allow_html=True)
        
        # Clean up the progress bar and status text after a delay
        time.sleep(2)
        progress_bar.empty()
        status_text.empty()
    finally:
        progress_bar.empty()
        status_text.empty()

def display_confirmation_dialog(prompt: Dict[str, Any]):
    """Display confirmation dialog for smart correction."""
    
    # st.markdown('<div class="confirmation-card">', unsafe_allow_html=True)
    st.markdown('<div class="confirmation-title"> Confirmation Needed ❓</div>', unsafe_allow_html=True)
    
    # Display message with proper styling
    message = prompt.get("message", "")
    st.markdown(f'<div class="confirmation-message"><strong style="color: #1e293b !important;">Did you mean this?</strong><br><span style="color: #374151 !important;">{message}</span></div>', unsafe_allow_html=True)
    
    # Display suggestion details if available
    if prompt.get("suggestion"):
        suggestion = prompt["suggestion"]
        
        col1, col2 = st.columns(2)
        with col1:
            
            st.markdown('<div style="font-size: 1rem; font-weight: 500; color: #6b7280 !important; margin-bottom: 0.5rem;">Original Input</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.125rem; font-weight: 600; color: #111827 !important; font-family: monospace;">{suggestion.get("original_input", "")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            
            st.markdown('<div style="font-size: 1rem; font-weight: 500; color: #6b7280 !important; margin-bottom: 0.5rem;">Suggested</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.125rem; font-weight: 600; color: #111827 !important;">{suggestion.get("corrected_name", "")} ({suggestion.get("ticker", "")})</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        with col3:
            
            st.markdown('<div style="font-size: 1rem; font-weight: 500; color: #6b7280 !important; margin-bottom: 0.5rem;">Confidence</div>', unsafe_allow_html=True)
            confidence = suggestion.get("confidence", "medium")
            badge_class = f"badge-{confidence}"
            st.markdown(f'<span class="badge {badge_class}" style="font-size: 1rem;">{confidence.upper()}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            
            st.markdown('<div style="font-size: 1rem; font-weight: 500; color: #6b7280 !important; margin-bottom: 0.5rem;">Explanation</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1rem; color: #4b5563 !important;">{suggestion.get("explanation", "")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("👎 No, that's not right", use_container_width=True, key="reject_btn"):
            st.session_state.confirmation_prompt = None
            st.session_state.conversation_id = None
            analyze_stocks(st.session_state.original_query, "No")
    
    with col3:
        ticker = prompt.get("suggestion", {}).get("ticker", "this")
        if st.button(f"👍 Yes, proceed with {ticker}", type="primary", use_container_width=True, key="confirm_btn"):
            st.session_state.confirmation_prompt = None
            analyze_stocks(st.session_state.original_query, "Yes")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_analysis_results(result: Dict[str, Any]):
    """Display the analysis results in a structured format."""
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Handle both direct insights and response-wrapped insights
    insights = result.get("insights", []) if isinstance(result.get("insights"), list) else []
    
    if not insights:
        st.markdown('<div class="alert-info">⚠️ No insights were generated. Please try a different query.</div>', unsafe_allow_html=True)
        return
    
    # Summary metrics
    st.markdown('<h2 style="color: #ffffff;">📊 Analysis Summary</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        
        st.markdown('<div style="font-size: 1.5rem; font-weight: 500; color: #6b7280 !important; margin-bottom: 0.5rem;">Tickers Analyzed</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 2rem; font-weight: 600; color: #111827 !important;">{len(result.get("tickers_analyzed", []))}</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        
        st.markdown('<div style="font-size: 1.5rem; font-weight: 500; color: #6b7280 !important; margin-bottom: 0.5rem;">Agents Used</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 2rem; font-weight: 600; color: #111827 !important;">{len(result.get("agents_used", []))}</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        
        st.markdown('<div style="font-size: 1.5rem; font-weight: 500; color: #6b7280 !important; margin-bottom: 0.5rem;">Analysis Time</div>', unsafe_allow_html=True)
        analysis_time = result.get("total_latency_ms", 0) / 1000
        st.markdown(f'<div style="font-size: 2rem; font-weight: 600; color: #111827 !important;">{analysis_time:.1f}s</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ticker insights
    st.markdown('<h3 style="color: #ffffff;">📈 Ticker Insights</h3>', unsafe_allow_html=True)
    
    for insight in insights:
        display_ticker_insight(insight)

def display_ticker_insight(insight: Dict[str, Any]):
    """Display detailed insight for a single ticker."""
    
    ticker = insight["ticker"]
    company_name = insight.get("company_name", "")
    stance = insight.get("stance", "hold")
    confidence = insight.get("confidence", "medium")
    
    with st.container():
        
        
        # Header
       
        col1, col2 = st.columns([2, 1])
        
        with col1:
           
            if company_name:
                st.markdown(f'<div class="ticker-company" style="font-size: 1.5rem; font-weight: 700; ">{company_name}</div>', unsafe_allow_html=True)
        
        with col2:
            stance_icon = {"buy": "📈", "sell": "📉", "hold": "➖"}.get(stance, "➖")
            st.markdown(f'<span class="badge badge-{stance}">{stance_icon} {stance.upper()}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="badge badge-{confidence}">{confidence.upper()} CONFIDENCE</span>', unsafe_allow_html=True)
        
        
        
        # Tabs for different sections
        st.markdown("""
         <style> .stTabs [data-baseweb="tab"] p {
            font-size: 18px !important;
            font-weight: 600 !important;
           }
         </style>""", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Summary", "🚀 Drivers", "⚠️ Risks", "⚡ Catalysts", "📚 Sources"])
        
        with tab1:
            # Price and Market Data
            if insight.get("current_price"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    
                    st.markdown('<div style="font-size: 1rem; font-weight: 500; color: #6b7280 !important;">Current Price</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size: 1.25rem; font-weight: 700; color: #111827 !important;">${insight["current_price"]:.2f}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    if insight.get("market_cap"):
                        
                        st.markdown('<div style="font-size: 1rem; font-weight: 500; color: #6b7280 !important;">Market Cap</div>', unsafe_allow_html=True)
                        market_cap = insight["market_cap"]
                        if market_cap >= 1e12:
                            cap_str = f"${market_cap / 1e12:.2f}T"
                        elif market_cap >= 1e9:
                            cap_str = f"${market_cap / 1e9:.2f}B"
                        elif market_cap >= 1e6:
                            cap_str = f"${market_cap / 1e6:.2f}M"
                        else:
                            cap_str = f"${market_cap:.2f}"
                        st.markdown(f'<div style="font-size: 1.25rem; font-weight: 700; color: #111827 !important;">{cap_str}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    if insight.get("pe_ratio"):
                        
                        st.markdown('<div style="font-size: 1rem; font-weight: 500; color: #6b7280 !important;">P/E Ratio</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-size: 1.25rem; font-weight: 700; color: #111827 !important;">{insight["pe_ratio"]:.2f}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    if insight.get("trend"):
                        
                        st.markdown('<div style="font-size: 1rem; font-weight: 500; color: #6b7280 !important;">Trend</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-size: 1.25rem; font-weight: 700; text-transform: capitalize; color: #111827 !important;">{insight["trend"]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Technical Levels
            if insight.get("support_levels") or insight.get("resistance_levels"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if insight.get("support_levels"):
                        
                        st.markdown('<div style="font-weight: 600; margin-bottom: 0.5rem; color: #1e293b !important;">Support Levels</div>', unsafe_allow_html=True)
                        for level in insight["support_levels"]:
                            st.markdown(f'<span class="badge">${level:.2f}</span>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    if insight.get("resistance_levels"):
                        
                        st.markdown('<div style="font-weight: 600; margin-bottom: 0.5rem; color: #1e293b !important;">Resistance Levels</div>', unsafe_allow_html=True)
                        for level in insight["resistance_levels"]:
                            st.markdown(f'<span class="badge" >${level:.2f}</span>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Summary and Rationale
            st.markdown('<h4 style="color: #1e293b !important;">Executive Summary</h4>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #374151 !important; line-height: 1.6;">{insight.get("summary", "No summary available.")}</p>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<h4 style="color: #1e293b !important;">Investment Rationale</h4>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #374151 !important; line-height: 1.6;">{insight.get("rationale", "No rationale provided.")}</p>', unsafe_allow_html=True)
        
        with tab2:
            drivers = insight.get("key_drivers", [])
            if drivers:
                for driver in drivers:
                    st.markdown(f'<div style="display: flex; align-items: start; gap: 0.5rem; margin-bottom: 0.75rem;"><span style="color: #16a34a; font-size: 1.25rem;">✓</span><span style="color: #374151 !important;">{driver}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #6b7280 !important;">No key drivers identified.</p>', unsafe_allow_html=True)
        
        with tab3:
            risks = insight.get("risks", [])
            if risks:
                for risk in risks:
                    st.markdown(f'<div style="display: flex; align-items: start; gap: 0.5rem; margin-bottom: 0.75rem;"><span style="color: #dc2626; font-size: 1.25rem;">⚠</span><span style="color: #374151 !important;">{risk}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #6b7280 !important;">No significant risks identified.</p>', unsafe_allow_html=True)
        
        with tab4:
            catalysts = insight.get("catalysts", [])
            if catalysts:
                for catalyst in catalysts:
                    st.markdown(f'<div style="display: flex; align-items: start; gap: 0.5rem; margin-bottom: 0.75rem;"><span style="color: #2563eb; font-size: 1.25rem;">⚡</span><span style="color: #374151 !important;">{catalyst}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #6b7280 !important;">No upcoming catalysts identified.</p>', unsafe_allow_html=True)
        
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
                st.markdown('<p style="color: #6b7280 !important;">No sources available.</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
