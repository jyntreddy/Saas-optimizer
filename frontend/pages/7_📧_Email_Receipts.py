"""Email receipts from Chrome extension"""

import streamlit as st
from datetime import datetime
from utils.session import init_session_state, is_logged_in, get_token
from utils.api import get_email_receipts, get_receipt_stats, update_receipt_status
from utils.formatting import format_currency, format_date
from components.sidebar import render_sidebar

# Page config
st.set_page_config(page_title="Email Receipts", page_icon="📧", layout="wide")

# Initialize session
init_session_state()

# Render sidebar
render_sidebar()

# Main content
st.title("📧 Email Receipts")
st.markdown("**Receipts scanned from Gmail using Chrome Extension**")

if not is_logged_in():
    st.warning("👈 Please login from the sidebar to view email receipts")
    st.stop()

token = get_token()

# Get statistics
stats = get_receipt_stats(token)

if stats:
    # Stats cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Receipts",
            stats.get('total_receipts', 0),
            help="All receipts scanned from Gmail"
        )
    
    with col2:
        st.metric(
            "From Extension",
            stats.get('from_extension', 0),
            help="Receipts scanned by Chrome extension"
        )
    
    with col3:
        st.metric(
            "Pending Review",
            stats.get('pending', 0),
            help="Receipts waiting to be matched to subscriptions"
        )
    
    with col4:
        st.metric(
            "Matched",
            stats.get('matched', 0),
            help="Receipts matched to existing subscriptions"
        )
    
    with col5:
        st.metric(
            "Total Detected",
            format_currency(stats.get('total_detected_spending', 0)),
            help="Total spending detected from receipts"
        )
    
    st.divider()

# Chrome Extension Setup Guide
with st.expander("🔧 Chrome Extension Setup", expanded=False):
    st.markdown("""
    ### Getting Started with Gmail Scanner Extension
    
    1. **Install Extension**:
       - Open Chrome → `chrome://extensions/`
       - Enable "Developer mode"
       - Click "Load unpacked"
       - Select `browser-extension` folder from the project
    
    2. **Configure Google OAuth**:
       - Get OAuth Client ID from [Google Cloud Console](https://console.cloud.google.com/)
       - Enable Gmail API
       - Update `manifest.json` with your Client ID
    
    3. **Connect & Scan**:
       - Click extension icon in Chrome toolbar
       - Click "Connect Gmail Account"
       - Authorize Gmail access (read-only)
       - Click "Scan Gmail for Receipts"
    
    4. **View Results Here**:
       - Scanned receipts appear in the table below
       - Match receipts to subscriptions or create new ones
       - Track all your subscription spending automatically
    
    📚 **Full Guide**: See `CHROME_EXTENSION_SETUP.md` in the project root
    """)

# Filter options
st.subheader("📋 Receipt List")

col1, col2, col3 = st.columns([2, 2, 6])

with col1:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "pending", "matched", "ignored", "processed"],
        index=0
    )

with col2:
    sort_by = st.selectbox(
        "Sort by",
        ["Newest First", "Oldest First", "Amount High-Low", "Amount Low-High"],
        index=0
    )

# Load receipts
with st.spinner("Loading receipts..."):
    receipts = get_email_receipts(token, status=None if status_filter == "All" else status_filter)

if not receipts:
    st.info("""
    📭 **No receipts found!**
    
    Install and use the Chrome Extension to scan your Gmail for subscription receipts.
    
    👉 See the setup guide above to get started.
    """)
    st.stop()

# Sort receipts
if sort_by == "Newest First":
    receipts.sort(key=lambda x: x.get('received_date', ''), reverse=True)
elif sort_by == "Oldest First":
    receipts.sort(key=lambda x: x.get('received_date', ''))
elif sort_by == "Amount High-Low":
    receipts.sort(key=lambda x: x.get('amount', 0) or 0, reverse=True)
else:  # Amount Low-High
    receipts.sort(key=lambda x: x.get('amount', 0) or 0)

st.markdown(f"**Showing {len(receipts)} receipt(s)**")

# Display receipts
for receipt in receipts:
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            # Vendor and subject
            vendor = receipt.get('vendor', 'Unknown')
            subject = receipt.get('email_subject', '')
            
            st.markdown(f"### {vendor}")
            st.caption(f"📧 {subject[:60]}...")
            
            # Gmail message ID badge if from extension
            if receipt.get('gmail_message_id'):
                st.markdown("🔵 **Chrome Extension**")
        
        with col2:
            # Amount and confidence
            amount = receipt.get('amount')
            if amount:
                st.markdown(f"**{format_currency(amount)}**")
            else:
                st.markdown("❓ *Amount not detected*")
            
            confidence = receipt.get('confidence_score', 0)
            if confidence:
                st.progress(confidence, text=f"Confidence: {int(confidence * 100)}%")
        
        with col3:
            # Date and sender
            received_date = receipt.get('received_date')
            if received_date:
                try:
                    date_obj = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
                    st.markdown(f"📅 {format_date(date_obj.strftime('%Y-%m-%d'))}")
                except:
                    st.markdown(f"📅 {received_date[:10]}")
            
            sender = receipt.get('sender_email', '')
            st.caption(f"From: {sender[:30]}...")
        
        with col4:
            # Status and actions
            status = receipt.get('status', 'pending')
            status_colors = {
                'pending': '🟡',
                'matched': '🟢',
                'ignored': '⚫',
                'processed': '✅'
            }
            
            st.markdown(f"{status_colors.get(status, '⚪')} **{status.title()}**")
            
            # Actions
            receipt_id = receipt.get('id')
            
            if status == 'pending':
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("✅ Match", key=f"match_{receipt_id}", use_container_width=True):
                        if update_receipt_status(token, receipt_id, 'matched'):
                            st.success("Matched!")
                            st.rerun()
                        else:
                            st.error("Failed to update")
                
                with col_b:
                    if st.button("❌ Ignore", key=f"ignore_{receipt_id}", use_container_width=True):
                        if update_receipt_status(token, receipt_id, 'ignored'):
                            st.success("Ignored!")
                            st.rerun()
                        else:
                            st.error("Failed to update")
        
        # Expandable details
        with st.expander("View Details"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Email Details:**")
                st.json({
                    "Subject": subject,
                    "From": receipt.get('sender_email'),
                    "Received": received_date,
                    "Gmail Message ID": receipt.get('gmail_message_id', 'N/A')
                })
            
            with col_b:
                st.markdown("**Extracted Data:**")
                st.json({
                    "Vendor": vendor,
                    "Amount": amount,
                    "Currency": receipt.get('currency', 'USD'),
                    "Category": receipt.get('category'),
                    "Is Subscription": receipt.get('is_subscription'),
                    "Confidence": f"{int((confidence or 0) * 100)}%"
                })
            
            # Raw snippet
            extracted = receipt.get('extracted_data', {})
            snippet = extracted.get('snippet') if isinstance(extracted, dict) else None
            
            if snippet:
                st.markdown("**Email Snippet:**")
                st.text(snippet)
        
        st.divider()

# Instructions at bottom
st.info("""
💡 **Tips:**
- **Match**: Link this receipt to an existing subscription
- **Ignore**: Mark as not relevant (won't appear in pending)
- **Processed**: System has automatically processed this receipt

Use the Chrome extension to automatically scan new emails hourly!
""")
