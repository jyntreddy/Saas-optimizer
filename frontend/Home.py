"""
SaaS Optimizer - Streamlit Frontend
Main entry point for the application
"""

import streamlit as st
from utils.api import get_api_url, test_connection
from utils.session import init_session_state

# Page config
st.set_page_config(
    page_title="SaaS Optimizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #0ea5e9;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8fafc;
        border-left: 4px solid #0ea5e9;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0ea5e9;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #0284c7;
    }
    </style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<div class="main-header">💰 SaaS Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Manage and optimize your SaaS subscriptions with AI-powered insights</div>', unsafe_allow_html=True)

# Check API connection
api_url = get_api_url()
with st.spinner("Checking API connection..."):
    api_status = test_connection()

if api_status:
    st.success(f"✅ Connected to API at {api_url}")
else:
    st.error(f"❌ Cannot connect to API at {api_url}")
    st.info("Make sure the FastAPI backend is running on http://localhost:8000")

st.divider()

# Features section
st.markdown("## 🚀 Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>📊 Subscription Management</h3>
        <p>Track all your SaaS subscriptions in one centralized dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>💡 AI Recommendations</h3>
        <p>Get intelligent suggestions for cost optimization and savings</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>📈 Cost Analytics</h3>
        <p>Visualize spending patterns and track trends over time</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>🔔 Renewal Alerts</h3>
        <p>Never miss a renewal date with automated notifications</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Quick actions
st.markdown("## ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("pages/1_📊_Dashboard.py")

with col2:
    if st.button("➕ Add Subscription", use_container_width=True):
        st.switch_page("pages/2_📋_Subscriptions.py")

with col3:
    if st.button("💡 Get Recommendations", use_container_width=True):
        st.switch_page("pages/4_💡_Recommendations.py")

# Info section
if not st.session_state.get("logged_in", False):
    st.divider()
    st.info("👈 Login from the sidebar to access all features")
    
    with st.expander("📝 Demo Credentials"):
        st.code("""
Email: demo@example.com
Password: demo123
        """)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 1rem;'>
        <p>SaaS Optimizer v1.0.0 | Built with FastAPI + Streamlit</p>
    </div>
""", unsafe_allow_html=True)
