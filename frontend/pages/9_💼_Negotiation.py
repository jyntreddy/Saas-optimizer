"""Negotiation Center - AI-powered price reduction bot"""

import streamlit as st
import pandas as pd
import sys
sys.path.append('..')
from utils.api import make_request
from utils.session import require_auth

require_auth()

st.title("💼 Negotiation Center")
st.markdown("Automated SaaS price negotiation with 20% success fee")

# Start negotiation
st.subheader("🚀 Start New Negotiation")

subscriptions = make_request("GET", "/subscriptions/")

if subscriptions:
    with st.form("negotiation_form"):
        sub_options = {f"{s['service_name']} (${s['cost']}/mo)": s['id'] for s in subscriptions}
        selected_sub = st.selectbox("Select Subscription", options=list(sub_options.keys()))
        
        target_discount = st.slider("Target Discount %", 10, 40, 20)
        
        submitted = st.form_submit_button("Start Negotiation")
        
        if submitted and selected_sub:
            sub_id = sub_options[selected_sub]
            selected = next(s for s in subscriptions if s['id'] == sub_id)
            target_price = selected['cost'] * (1 - target_discount / 100)
            
            payload = {
                "subscription_id": sub_id,
                "target_price": target_price
            }
            
            result = make_request("POST", "/negotiate/sessions", json=payload)
            
            if result:
                st.success(f"✅ Negotiation started! Target: ${target_price:.2f}/mo")
                st.rerun()

# Active negotiations
st.subheader("📋 Active Negotiations")

sessions = make_request("GET", "/negotiate/sessions")

if sessions:
    if not sessions:
        st.info("No negotiations yet. Start your first one above!")
    else:
        for session in sessions:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{session['vendor']}**")
                    st.caption(f"Started: {session['started_at'][:10]}")
                
                with col2:
                    st.metric("Current", f"${session['current_price']:.2f}")
                
                with col3:
                    target = session.get('target_price', 0)
                    st.metric("Target", f"${target:.2f}")
                
                with col4:
                    status = session['status']
                    
                    if status == 'initiated':
                        st.warning("⏳ In Progress")
                    elif status == 'completed':
                        achieved = session.get('achieved_price', 0)
                        savings = session['current_price'] - achieved
                        st.success(f"✅ Saved ${savings:.2f}/mo")
                    else:
                        st.info(f"Status: {status}")
                    
                    # Complete button
                    if status == 'initiated':
                        with st.expander(f"Complete #{session['id']}"):
                            achieved_price = st.number_input(
                                "Final Price", 
                                min_value=0.0, 
                                value=target,
                                key=f"achieved_{session['id']}"
                            )
                            
                            if st.button("Mark as Completed", key=f"complete_{session['id']}"):
                                result = make_request(
                                    "PATCH",
                                    f"/negotiate/sessions/{session['id']}/complete",
                                    params={"achieved_price": achieved_price}
                                )
                                
                                if result:
                                    st.success(f"✅ Saved ${result['savings']:.2f}/mo!")
                                    st.rerun()
                
                st.divider()

# Price intelligence
st.subheader("💡 Community Price Intelligence")

col1, col2 = st.columns(2)

with col1:
    with st.expander("📤 Submit Price Data"):
        with st.form("price_intel_form"):
            vendor = st.text_input("Vendor Name*")
            plan = st.text_input("Plan Name")
            price = st.number_input("Monthly Price ($)*", min_value=0.0)
            discount_pct = st.number_input("Discount Achieved (%)", min_value=0.0, max_value=100.0)
            
            submit_intel = st.form_submit_button("Submit")
            
            if submit_intel:
                if vendor and price:
                    payload = {
                        "vendor": vendor,
                        "plan_name": plan,
                        "reported_price": price,
                        "billing_cycle": "monthly",
                        "negotiated_discount": discount_pct
                    }
                    
                    result = make_request("POST", "/negotiate/price-intel", json=payload)
                    
                    if result:
                        st.success("✅ Price data submitted!")

with col2:
    st.info("""
    **How it works:**
    
    1️⃣ Our AI bot analyzes your subscription  
    2️⃣ Crafts personalized negotiation emails  
    3️⃣ Sends requests on your behalf  
    4️⃣ Tracks responses and counters  
    5️⃣ You only pay 20% of savings!
    
    **Average Results:**
    - 68% success rate
    - $127/mo average savings
    - 14 days average time
    """)

# Success stories
st.subheader("🏆 Recent Wins")

completed = [s for s in sessions if s.get('status') == 'completed'] if sessions else []

if completed:
    total_savings = sum(s['current_price'] - s.get('achieved_price', 0) for s in completed if s.get('achieved_price'))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Saved", f"${total_savings:.2f}/mo")
    with col2:
        st.metric("Annual Impact", f"${total_savings * 12:.2f}")
    with col3:
        st.metric("Negotiations Won", len(completed))
