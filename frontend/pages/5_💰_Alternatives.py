"""Alternative Plans page with savings recommendations"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.session import init_session_state, is_logged_in, get_token
from utils.api import get_subscription_alternatives, get_subscriptions
from utils.formatting import format_currency
from components.sidebar import render_sidebar

# Page config
st.set_page_config(page_title="Alternative Plans", page_icon="💰", layout="wide")

# Initialize session
init_session_state()

# Render sidebar
render_sidebar()

# Main content
st.title("💰 Alternative Plans & Savings")

if not is_logged_in():
    st.warning("👈 Please login from the sidebar to view alternatives")
    st.stop()

token = get_token()

st.markdown("""
Discover cheaper alternatives to your subscriptions and maximize your savings!
We compare your current plans with competitors and lower-tier options.
""")

st.divider()

with st.spinner("Finding alternative plans..."):
    alternatives = get_subscription_alternatives(token)
    subscriptions = get_subscriptions(token)

if alternatives:
    # Calculate total potential savings
    total_monthly_savings = sum(
        alt.get("total_potential_savings", 0) 
        for alt in alternatives
    )
    total_annual_savings = total_monthly_savings * 12
    
    # Savings banner
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                padding: 2rem; border-radius: 1rem; color: white; text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
        <h2 style='margin: 0; font-size: 2.5rem; font-weight: bold;'>
            💰 {format_currency(total_annual_savings)} / year
        </h2>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;'>
            Total Potential Savings ({format_currency(total_monthly_savings)} / month)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Subscriptions Analyzed", len(alternatives))
    
    with col2:
        total_alternatives = sum(len(alt.get("alternatives", [])) for alt in alternatives)
        st.metric("Alternative Plans Found", total_alternatives)
    
    with col3:
        avg_savings = total_monthly_savings / len(alternatives) if alternatives else 0
        st.metric("Avg Savings per Subscription", format_currency(avg_savings))
    
    st.divider()
    
    # Alternative suggestions
    st.markdown("### 🎯 Recommended Alternatives")
    
    for idx, suggestion in enumerate(alternatives, 1):
        subscription_name = suggestion.get("subscription_name", "Unknown")
        current_cost = suggestion.get("current_cost", 0)
        billing_cycle = suggestion.get("billing_cycle", "monthly")
        alt_list = suggestion.get("alternatives", [])
        total_savings = suggestion.get("total_potential_savings", 0)
        best_alternative = suggestion.get("best_alternative")
        
        with st.expander(
            f"🔹 {subscription_name} - Save up to {format_currency(total_savings)}/month",
            expanded=(idx == 1)
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Current Plan:**  
                {subscription_name} - {format_currency(current_cost)}/{billing_cycle}
                """)
                
                if best_alternative:
                    st.markdown(f"""
                    **🏆 Best Alternative:**  
                    {best_alternative.get('alternative_name')} by {best_alternative.get('alternative_provider')}  
                    💵 {format_currency(best_alternative.get('alternative_cost'))} / month  
                    💰 Save {format_currency(best_alternative.get('monthly_savings'))} / month
                    """)
            
            with col2:
                if total_savings > 0:
                    st.markdown("**Monthly Savings**")
                    st.markdown(f"### {format_currency(total_savings)}")
                    st.markdown(f"*{format_currency(total_savings * 12)} / year*")
            
            st.divider()
            
            # Show all alternatives
            st.markdown("**All Alternatives:**")
            
            for alt in alt_list:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**{alt.get('alternative_name')}**")
                    st.caption(f"by {alt.get('alternative_provider')}")
                
                with col2:
                    st.markdown(f"**Cost:** {format_currency(alt.get('alternative_cost'))}/mo")
                
                with col3:
                    savings = alt.get('monthly_savings', 0)
                    percentage = alt.get('savings_percentage', 0)
                    st.markdown(f"**Save:** {format_currency(savings)}/mo")
                    st.caption(f"{percentage:.0f}% savings")
                
                with col4:
                    if st.button(f"Learn More", key=f"learn_{suggestion.get('subscription_id')}_{alt.get('alternative_name')}"):
                        st.info(f"**Features:** {alt.get('features_comparison', 'N/A')}")
                        st.info(f"**Reason:** {alt.get('reason', 'Cheaper alternative')}")
                
                st.markdown("---")
    
    st.divider()
    
    # Savings visualization
    st.markdown("### 📊 Savings Breakdown")
    
    # Create dataframe for visualization
    savings_data = []
    for alt in alternatives:
        savings_data.append({
            "Subscription": alt.get("subscription_name", "Unknown"),
            "Current Cost": alt.get("current_cost", 0),
            "Potential Savings": alt.get("total_potential_savings", 0)
        })
    
    df = pd.DataFrame(savings_data)
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart - Current vs Potential Savings
            fig1 = px.bar(
                df,
                x="Subscription",
                y=["Current Cost", "Potential Savings"],
                title="Current Cost vs Potential Savings",
                barmode="group",
                color_discrete_map={
                    "Current Cost": "#ef4444",
                    "Potential Savings": "#10b981"
                }
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Pie chart - Savings distribution
            fig2 = px.pie(
                df,
                values="Potential Savings",
                names="Subscription",
                title="Savings Distribution by Subscription"
            )
            st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("No alternative suggestions available at this time.")
    st.markdown("""
    **Why no alternatives?**
    - Your subscriptions may already be at the best available price
    - We're constantly updating our alternative plans database
    - Add more subscriptions to get personalized recommendations
    """)

# Action buttons
st.divider()
st.markdown("### 🎯 Take Action")

col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Manage Subscriptions", use_container_width=True):
        st.switch_page("pages/2_📋_Subscriptions.py")

with col2:
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("pages/1_📊_Dashboard.py")

# Refresh button
st.divider()
if st.button("🔄 Refresh Alternatives"):
    st.rerun()
