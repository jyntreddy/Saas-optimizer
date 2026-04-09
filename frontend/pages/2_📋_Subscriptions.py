"""Subscriptions management page"""

import streamlit as st
from datetime import datetime, timedelta
from utils.session import init_session_state, is_logged_in, get_token
from utils.api import get_subscriptions, create_subscription, update_subscription, delete_subscription
from utils.formatting import format_currency, format_date, get_status_color
from components.sidebar import render_sidebar

# Page config
st.set_page_config(page_title="Subscriptions", page_icon="📋", layout="wide")

# Initialize session
init_session_state()

# Render sidebar
render_sidebar()

# Main content
st.title("📋 Subscriptions")

if not is_logged_in():
    st.warning("👈 Please login from the sidebar to manage subscriptions")
    st.stop()

token = get_token()

# Tabs for list and add
tab1, tab2 = st.tabs(["📋 My Subscriptions", "➕ Add New"])

# List subscriptions
with tab1:
    with st.spinner("Loading subscriptions..."):
        subscriptions = get_subscriptions(token)
    
    if subscriptions:
        st.markdown(f"### Total: {len(subscriptions)} subscription(s)")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "active", "cancelled", "expired", "trial"]
            )
        
        with col2:
            cycle_filter = st.selectbox(
                "Filter by Billing Cycle",
                ["All", "monthly", "yearly", "quarterly"]
            )
        
        # Apply filters
        filtered_subs = subscriptions
        if status_filter != "All":
            filtered_subs = [s for s in filtered_subs if s.get('status') == status_filter]
        if cycle_filter != "All":
            filtered_subs = [s for s in filtered_subs if s.get('billing_cycle') == cycle_filter]
        
        st.divider()
        
        # Display subscriptions as cards
        for idx, sub in enumerate(filtered_subs):
            with st.expander(f"{get_status_color(sub.get('status', ''))} {sub['service_name']} - {format_currency(sub['cost'])}/{sub.get('billing_cycle', 'month')}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Provider:** {sub.get('provider', 'N/A')}")
                    st.markdown(f"**Cost:** {format_currency(sub['cost'])}")
                    st.markdown(f"**Billing Cycle:** {sub.get('billing_cycle', 'monthly')}")
                    st.markdown(f"**Status:** {sub.get('status', 'active')}")
                    
                    if sub.get('start_date'):
                        st.markdown(f"**Start Date:** {format_date(sub['start_date'])}")
                    if sub.get('renewal_date'):
                        st.markdown(f"**Renewal Date:** {format_date(sub['renewal_date'])}")
                
                with col2:
                    st.markdown("**Actions:**")
                    
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_{sub['id']}"):
                        st.session_state[f"editing_{sub['id']}"] = True
                        st.rerun()
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_{sub['id']}", type="secondary"):
                        if delete_subscription(token, sub['id']):
                            st.success("Deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete")
                
                # Edit form
                if st.session_state.get(f"editing_{sub['id']}", False):
                    st.divider()
                    st.markdown("**Edit Subscription:**")
                    
                    with st.form(f"edit_form_{sub['id']}"):
                        new_cost = st.number_input("Cost", value=float(sub['cost']), min_value=0.01, step=0.01)
                        new_status = st.selectbox("Status", ["active", "cancelled", "expired", "trial"], 
                                                 index=["active", "cancelled", "expired", "trial"].index(sub.get('status', 'active')))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save"):
                                data = {"cost": new_cost, "status": new_status}
                                if update_subscription(token, sub['id'], data):
                                    st.success("Updated successfully!")
                                    st.session_state[f"editing_{sub['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"editing_{sub['id']}"] = False
                                st.rerun()
    else:
        st.info("No subscriptions yet. Add your first subscription!")

# Add new subscription
with tab2:
    st.markdown("### ➕ Add New Subscription")
    
    with st.form("add_subscription_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            service_name = st.text_input("Service Name *", placeholder="e.g., Netflix")
            provider = st.text_input("Provider", placeholder="e.g., Netflix Inc")
            cost = st.number_input("Cost *", min_value=0.01, value=9.99, step=0.01)
        
        with col2:
            billing_cycle = st.selectbox("Billing Cycle *", ["monthly", "yearly", "quarterly"])
            status = st.selectbox("Status", ["active", "trial", "cancelled", "expired"])
            
            # Dates
            start_date = st.date_input("Start Date", value=datetime.now())
            
            # Calculate default renewal date
            if billing_cycle == "monthly":
                default_renewal = datetime.now() + timedelta(days=30)
            elif billing_cycle == "yearly":
                default_renewal = datetime.now() + timedelta(days=365)
            else:  # quarterly
                default_renewal = datetime.now() + timedelta(days=90)
            
            renewal_date = st.date_input("Renewal Date", value=default_renewal)
        
        submitted = st.form_submit_button("➕ Add Subscription", use_container_width=True)
        
        if submitted:
            if service_name and cost:
                subscription_data = {
                    "service_name": service_name,
                    "provider": provider if provider else None,
                    "cost": cost,
                    "billing_cycle": billing_cycle,
                    "status": status,
                    "start_date": start_date.isoformat() if start_date else None,
                    "renewal_date": renewal_date.isoformat() if renewal_date else None,
                }
                
                with st.spinner("Adding subscription..."):
                    result = create_subscription(token, subscription_data)
                    
                    if result:
                        st.success(f"✅ {service_name} added successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to add subscription")
            else:
                st.error("Please fill in required fields (marked with *)")
