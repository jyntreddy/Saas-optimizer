"""Team Usage - Track team member subscription usage"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
sys.path.append('..')
from utils.api import make_request
from utils.session import require_auth

require_auth()

st.title("👥 Team Usage Analytics")
st.markdown("Track team member activity across subscriptions")

# Add team member
with st.expander("➕ Add Team Member", expanded=False):
    with st.form("add_member_form"):
        email = st.text_input("Email*")
        full_name = st.text_input("Full Name")
        role = st.text_input("Role")
        department = st.text_input("Department")
        
        submitted = st.form_submit_button("Add Member")
        
        if submitted:
            if not email:
                st.error("Email is required")
            else:
                payload = {
                    "email": email,
                    "full_name": full_name,
                    "role": role,
                    "department": department
                }
                
                result = make_request("POST", "/team/members", json=payload)
                
                if result:
                    st.success(f"✅ Added {email} to team")
                    st.rerun()

# Team members list
st.subheader("👤 Team Members")

members = make_request("GET", "/team/members")

if members:
    if not members:
        st.info("No team members yet. Add your first member above!")
    else:
        df = pd.DataFrame(members)
        st.dataframe(
            df[['email', 'full_name', 'role', 'department']],
            use_container_width=True,
            hide_index=True
        )

# Usage analytics
st.subheader("📊 Usage Analytics")

days = st.slider("Time Period (days)", 7, 90, 30)
analytics = make_request("GET", f"/team/analytics/usage-by-member", params={"days": days})

if analytics:
    if not analytics:
        st.info("No usage data yet")
    else:
        df = pd.DataFrame(analytics)
        
        # Usage by member chart
        fig = px.bar(
            df,
            x='name',
            y='usage_count',
            color='service',
            title=f'Usage by Team Member (Last {days} days)',
            labels={'usage_count': 'Activities', 'name': 'Team Member'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top users
        st.subheader("🏆 Top Users")
        top_users = df.groupby('name')['usage_count'].sum().sort_values(ascending=False).head(5)
        
        for i, (name, count) in enumerate(top_users.items(), 1):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{i}. **{name}**")
            with col2:
                st.write(f"{int(count)} activities")

# Shadow IT detection
st.subheader("⚠️ Shadow IT Detections")

shadow_it = make_request("GET", "/team/shadow-it")

if shadow_it:
    if not shadow_it:
        st.success("✅ No shadow IT detected")
    else:
        st.warning(f"Found {len(shadow_it)} unauthorized tools")
        
        for detection in shadow_it:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**{detection['tool_name']}**")
                    st.caption(f"Used by: {detection.get('team_member_email', 'Unknown')}")
                
                with col2:
                    risk = detection.get('risk_level', 'medium')
                    if risk == 'high':
                        st.error(f"🔴 High Risk")
                    elif risk == 'medium':
                        st.warning(f"🟡 Medium Risk")
                    else:
                        st.info(f"🟢 Low Risk")
                
                with col3:
                    cost = detection.get('estimated_cost', 0)
                    if cost:
                        st.metric("Est. Cost", f"${cost:.2f}")
                
                st.divider()
else:
    st.info("Enable team tracking to detect shadow IT")
