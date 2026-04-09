"""Dashboard page with overview and stats"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.session import init_session_state, is_logged_in, get_token
from utils.api import get_spending_summary, get_subscriptions
from utils.formatting import format_currency
from components.sidebar import render_sidebar

# Page config
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Initialize session
init_session_state()

# Render sidebar
render_sidebar()

# Main content
st.title("📊 Dashboard")

if not is_logged_in():
    st.warning("👈 Please login from the sidebar to access the dashboard")
    st.stop()

# Get data
token = get_token()

with st.spinner("Loading dashboard data..."):
    from utils.api import get_subscription_summary
    
    # Get enhanced summary
    enhanced_summary = get_subscription_summary(token)
    summary = get_spending_summary(token)
    subscriptions = get_subscriptions(token)

if not summary:
    st.error("Failed to load spending summary")
    st.stop()

# Key Metrics
st.markdown("### 📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Monthly Spend",
        value=format_currency(summary.get("total_monthly_spend", 0)),
        delta=None
    )

with col2:
    st.metric(
        label="Active Subscriptions",
        value=summary.get("total_subscriptions", 0)
    )

with col3:
    st.metric(
        label="Annual Cost",
        value=format_currency(summary.get("estimated_annual_cost", 0))
    )

with col4:
    st.metric(
        label="Yearly Agreements",
        value=format_currency(summary.get("total_yearly_spend", 0))
    )

st.divider()

# Alerts Section
if enhanced_summary:
    duplicates = enhanced_summary.get("duplicates", [])
    low_usage = enhanced_summary.get("low_usage_subscriptions", [])
    
    if duplicates or low_usage:
        st.markdown("### ⚠️ Alerts & Opportunities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if duplicates:
                st.warning(f"🔄 {len(duplicates)} duplicate or similar subscriptions detected")
                if st.button("View Duplicates", use_container_width=True):
                    st.switch_page("pages/3_📈_Analytics.py")
        
        with col2:
            if low_usage:
                st.warning(f"⏸️ {len(low_usage)} subscriptions with low usage")
                if st.button("View Details", use_container_width=True):
                    st.switch_page("pages/3_📈_Analytics.py")
        
        st.divider()

# Charts
if subscriptions:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Spending by Service")
        
        # Create dataframe
        df = pd.DataFrame(subscriptions)
        
        # Pie chart
        fig = px.pie(
            df,
            values='cost',
            names='service_name',
            title='Subscription Costs',
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Cost by Billing Cycle")
        
        # Group by billing cycle
        cycle_costs = df.groupby('billing_cycle')['cost'].sum().reset_index()
        
        # Bar chart
        fig = px.bar(
            cycle_costs,
            x='billing_cycle',
            y='cost',
            title='Costs by Billing Cycle',
            labels={'cost': 'Cost ($)', 'billing_cycle': 'Billing Cycle'},
            color='cost',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent subscriptions table
    st.markdown("### 📋 Recent Subscriptions")
    
    # Format data for display
    display_df = df[['service_name', 'provider', 'cost', 'billing_cycle', 'status']].copy()
    display_df['cost'] = display_df['cost'].apply(lambda x: f"${x:.2f}")
    display_df.columns = ['Service', 'Provider', 'Cost', 'Billing Cycle', 'Status']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.info("No subscriptions found. Add your first subscription to see analytics!")
    
    if st.button("➕ Add Subscription"):
        st.switch_page("pages/2_📋_Subscriptions.py")

# Refresh button
st.divider()
if st.button("🔄 Refresh Data", use_container_width=False):
    st.rerun()
