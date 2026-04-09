"""AI-powered recommendations page"""

import streamlit as st
from utils.session import init_session_state, is_logged_in, get_token
from utils.api import get_recommendations
from utils.formatting import format_currency
from components.sidebar import render_sidebar

# Page config
st.set_page_config(page_title="Recommendations", page_icon="💡", layout="wide")

# Initialize session
init_session_state()

# Render sidebar
render_sidebar()

# Main content
st.title("💡 Cost Optimization Recommendations")

if not is_logged_in():
    st.warning("👈 Please login from the sidebar to view recommendations")
    st.stop()

token = get_token()

st.markdown("""
Our AI-powered recommendation engine analyzes your subscriptions and provides 
personalized suggestions to optimize your spending.
""")

st.divider()

with st.spinner("Analyzing your subscriptions..."):
    recommendations = get_recommendations(token)

if recommendations:
    st.success(f"Found {len(recommendations)} recommendation(s)")
    
    total_savings = sum(rec.get('potential_savings', 0) for rec in recommendations)
    
    # Potential savings banner
    st.markdown(f"""
    <div style='background-color: #dcfce7; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #16a34a;'>
        <h3 style='color: #16a34a; margin: 0;'>💰 Potential Annual Savings: {format_currency(total_savings * 12)}</h3>
        <p style='margin: 0.5rem 0 0 0;'>Based on current recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Display recommendations
    for idx, rec in enumerate(recommendations, 1):
        rec_type = rec.get('type', 'general')
        
        # Icon based on type
        icon_map = {
            'high_cost': '💸',
            'duplicate': '🔄',
            'unused': '⏸️',
            'alternative': '🔀',
            'general': '💡'
        }
        icon = icon_map.get(rec_type, '💡')
        
        with st.container():
            st.markdown(f"### {icon} Recommendation #{idx}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Service:** {rec.get('service_name', 'N/A')}")
                st.markdown(f"**Type:** {rec_type.replace('_', ' ').title()}")
                st.markdown(f"**Suggestion:** {rec.get('message', 'No message')}")
            
            with col2:
                if rec.get('potential_savings'):
                    savings = rec['potential_savings']
                    st.markdown("**Potential Savings:**")
                    st.markdown(f"### {format_currency(savings)}/mo")
                    st.markdown(f"*{format_currency(savings * 12)}/year*")
            
            st.divider()
    
    # Action buttons
    st.markdown("### 🎯 Take Action")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Review Subscriptions", use_container_width=True):
            st.switch_page("pages/2_📋_Subscriptions.py")
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/3_📈_Analytics.py")

else:
    st.info("No recommendations available at this time.")
    st.markdown("""
    Recommendations are generated based on:
    - High-cost subscriptions
    - Duplicate or overlapping services
    - Unused or underutilized subscriptions
    - Better alternatives available
    
    Add more subscriptions to get personalized recommendations!
    """)
    
    if st.button("➕ Add Subscriptions"):
        st.switch_page("pages/2_📋_Subscriptions.py")

# Refresh button
st.divider()
if st.button("🔄 Refresh Recommendations"):
    st.rerun()
