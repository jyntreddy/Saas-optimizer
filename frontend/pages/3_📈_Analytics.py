"""Analytics page with detailed spending insights"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.session import init_session_state, is_logged_in, get_token
from utils.api import get_spending_summary, get_subscriptions
from utils.formatting import format_currency, calculate_annual_cost
from components.sidebar import render_sidebar

# Page config
st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

# Initialize session
init_session_state()

# Render sidebar
render_sidebar()

# Main content
st.title("📈 Analytics")

if not is_logged_in():
    st.warning("👈 Please login from the sidebar to view analytics")
    st.stop()

token = get_token()

with st.spinner("Loading analytics data..."):
    summary = get_spending_summary(token)
    subscriptions = get_subscriptions(token)

if not summary:
    st.error("Failed to load analytics data")
    st.stop()

# Summary Section
st.markdown("### 💰 Spending Summary")

col1, col2, col3 = st.columns(3)

with col1:
    total_monthly = summary.get("total_monthly_spend", 0)
    st.metric("Total Monthly Spend", format_currency(total_monthly))

with col2:
    total_annual = summary.get("estimated_annual_cost", 0)
    st.metric("Estimated Annual Cost", format_currency(total_annual))

with col3:
    avg_sub = total_monthly / summary.get("total_subscriptions", 1)
    st.metric("Average per Subscription", format_currency(avg_sub))

st.divider()

if subscriptions:
    df = pd.DataFrame(subscriptions)
    
    # Cost breakdown
    st.markdown("### 📊 Cost Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 most expensive
        st.markdown("#### 💸 Most Expensive Services")
        top_5 = df.nlargest(5, 'cost')[['service_name', 'cost', 'billing_cycle']]
        
        for idx, row in top_5.iterrows():
            annual = calculate_annual_cost(row['cost'], row['billing_cycle'])
            st.markdown(f"""
            **{row['service_name']}**  
            {format_currency(row['cost'])}/{row['billing_cycle']} → {format_currency(annual)}/year
            """)
            st.progress(row['cost'] / df['cost'].max())
    
    with col2:
        # Status distribution
        st.markdown("#### 📋 Status Distribution")
        status_counts = df['status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title='Subscriptions by Status',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Trends
    st.markdown("### 📈 Spending Trends")
    
    # Mock monthly data (since we don't have historical data)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    spending = [
        total_monthly * 0.8,
        total_monthly * 0.9,
        total_monthly * 0.85,
        total_monthly * 1.1,
        total_monthly * 0.95,
        total_monthly
    ]
    
    trend_df = pd.DataFrame({'Month': months, 'Spending': spending})
    
    fig = px.line(
        trend_df,
        x='Month',
        y='Spending',
        title='Monthly Spending Trend (Last 6 Months)',
        markers=True
    )
    fig.update_layout(yaxis_title='Spending ($)', xaxis_title='Month')
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Detailed table
    st.markdown("### 📋 Detailed Subscription Data")
    
    # Calculate annual costs
    df['annual_cost'] = df.apply(
        lambda row: calculate_annual_cost(row['cost'], row['billing_cycle']),
        axis=1
    )
    
    # Format for display
    display_df = df[['service_name', 'provider', 'cost', 'billing_cycle', 'annual_cost', 'status']].copy()
    display_df['cost'] = display_df['cost'].apply(lambda x: f"${x:.2f}")
    display_df['annual_cost'] = display_df['annual_cost'].apply(lambda x: f"${x:.2f}")
    display_df.columns = ['Service', 'Provider', 'Cost', 'Billing', 'Annual Cost', 'Status']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Download data
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"subscriptions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

else:
    st.info("No subscription data available for analysis")

# Refresh button
st.divider()
if st.button("🔄 Refresh Analytics"):
    st.rerun()
