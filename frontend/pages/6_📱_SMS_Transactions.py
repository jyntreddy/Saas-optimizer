"""SMS Transactions page for viewing and managing detected subscriptions"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.session import init_session_state, is_logged_in, get_token
from utils.api import (
    get_sms_transactions,
    update_sms_status,
    create_subscription_from_sms
)
from utils.formatting import format_currency, format_date
from components.sidebar import render_sidebar

# Page config
st.set_page_config(page_title="SMS Transactions", page_icon="📱", layout="wide")

# Initialize session
init_session_state()

# Render sidebar
render_sidebar()

# Main content
st.title("📱 SMS Transactions")

if not is_logged_in():
    st.warning("👈 Please login from the sidebar to view SMS transactions")
    st.stop()

token = get_token()

st.markdown("""
View and manage subscription charges detected from your SMS messages.
Confirm genuine subscriptions or mark spam/incorrect detections as ignored.
""")

st.divider()

# Filter options
col1, col2 = st.columns([3, 1])

with col1:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "pending", "confirmed", "ignored", "matched"],
        index=0
    )

with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.divider()

# Get transactions
with st.spinner("Loading SMS transactions..."):
    filter_status = None if status_filter == "All" else status_filter
    transactions = get_sms_transactions(token, filter_status)

if transactions:
    st.success(f"Found {len(transactions)} transaction(s)")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    pending = len([t for t in transactions if t.get("status") == "pending"])
    confirmed = len([t for t in transactions if t.get("status") == "confirmed"])
    matched = len([t for t in transactions if t.get("status") == "matched"])
    ignored = len([t for t in transactions if t.get("status") == "ignored"])
    
    with col1:
        st.metric("Pending Review", pending, help="Transactions waiting for confirmation")
    
    with col2:
        st.metric("Confirmed", confirmed, help="User-confirmed transactions")
    
    with col3:
        st.metric("Auto-Matched", matched, help="Automatically matched to subscriptions")
    
    with col4:
        st.metric("Ignored", ignored, help="Marked as spam or incorrect")
    
    st.divider()
    
    # Display transactions
    st.markdown("### 📋 Transaction Details")
    
    for idx, trans in enumerate(transactions):
        status = trans.get("status", "pending")
        vendor = trans.get("vendor", "Unknown")
        amount = trans.get("amount")
        confidence = trans.get("confidence_score", 0)
        created_at = trans.get("created_at")
        message = trans.get("raw_message", "")
        trans_id = trans.get("id")
        subscription_id = trans.get("subscription_id")
        
        # Status emoji
        status_emoji = {
            "pending": "⏳",
            "confirmed": "✅",
            "matched": "🔗",
            "ignored": "❌"
        }
        emoji = status_emoji.get(status, "❓")
        
        # Confidence color
        if confidence >= 0.7:
            confidence_color = "🟢"
        elif confidence >= 0.4:
            confidence_color = "🟡"
        else:
            confidence_color = "🔴"
        
        with st.expander(
            f"{emoji} {vendor} - {format_currency(amount) if amount else 'Amount unknown'} | {status.upper()}",
            expanded=(status == "pending" and idx < 3)
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Vendor:** {vendor or 'Unknown'}")
                st.markdown(f"**Amount:** {format_currency(amount) if amount else 'N/A'}")
                st.markdown(f"**Date:** {format_date(created_at) if created_at else 'Unknown'}")
                st.markdown(f"**Confidence:** {confidence_color} {confidence*100:.0f}%")
                
                if subscription_id:
                    st.markdown(f"**Linked to Subscription ID:** {subscription_id}")
                
                st.markdown("**Original Message:**")
                st.text_area(
                    "SMS Content",
                    value=message,
                    height=100,
                    disabled=True,
                    key=f"msg_{trans_id}",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("**Actions:**")
                
                if status == "pending" or status == "matched":
                    if st.button("✅ Confirm", key=f"confirm_{trans_id}", use_container_width=True):
                        if update_sms_status(token, trans_id, "confirmed"):
                            st.success("✅ Confirmed!")
                            st.rerun()
                        else:
                            st.error("Failed to update")
                    
                    if st.button("❌ Ignore", key=f"ignore_{trans_id}", use_container_width=True):
                        if update_sms_status(token, trans_id, "ignored"):
                            st.success("Marked as ignored")
                            st.rerun()
                        else:
                            st.error("Failed to update")
                    
                    if not subscription_id and vendor and amount:
                        if st.button("➕ Create Subscription", key=f"create_{trans_id}", use_container_width=True):
                            result = create_subscription_from_sms(token, trans_id)
                            if result:
                                st.success(f"✅ Subscription created! ID: {result.get('subscription_id')}")
                                st.rerun()
                            else:
                                st.error("Failed to create subscription")
                
                elif status == "confirmed":
                    st.info("✅ Confirmed transaction")
                    
                    if st.button("↩️ Mark Pending", key=f"pending_{trans_id}", use_container_width=True):
                        if update_sms_status(token, trans_id, "pending"):
                            st.success("Moved back to pending")
                            st.rerun()
                
                elif status == "ignored":
                    st.info("❌ Ignored transaction")
                    
                    if st.button("↩️ Restore", key=f"restore_{trans_id}", use_container_width=True):
                        if update_sms_status(token, trans_id, "pending"):
                            st.success("Restored to pending")
                            st.rerun()
            
            st.markdown("---")

else:
    st.info("No SMS transactions found.")
    st.markdown("""
    **How SMS detection works:**
    
    1. 📱 Connect your phone number to receive SMS webhooks from Twilio
    2. 💳 When you receive a subscription charge SMS, it's automatically parsed
    3. 🤖 AI extracts vendor name, amount, and other details
    4. ✅ Review and confirm or ignore detected transactions
    5. 📊 Confirmed transactions are added to your subscription tracking
    
    **Configure SMS forwarding:**
    - Set up Twilio webhook pointing to: `https://your-domain.com/api/v1/sms/webhook`
    - Forward bank SMS notifications to your Twilio number
    - Transactions will appear here automatically
    """)
    
    if st.button("📋 View All Subscriptions"):
        st.switch_page("pages/2_📋_Subscriptions.py")

# Help section
st.divider()
with st.expander("❓ Need Help?"):
    st.markdown("""
    **Status Meanings:**
    - ⏳ **Pending**: Detected but not yet reviewed
    - ✅ **Confirmed**: You've verified this is a real subscription charge
    - 🔗 **Matched**: Automatically linked to an existing subscription
    - ❌ **Ignored**: Marked as spam or incorrect detection
    
    **Tips:**
    - Focus on pending transactions first
    - High confidence (🟢) detections are more accurate
    - You can always restore ignored transactions
    - Create subscriptions from confirmed transactions for tracking
    """)
