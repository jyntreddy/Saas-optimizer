"""Sidebar component with login/logout"""

import streamlit as st
from utils.api import login, create_user
from utils.session import login_user, logout_user, is_logged_in


def render_sidebar():
    """Render the sidebar with login/logout functionality"""
    
    with st.sidebar:
        st.title("🔐 SaaS Optimizer")
        
        if is_logged_in():
            # Show user info
            user = st.session_state.user
            st.success(f"👤 {user.get('email', 'User')}")
            
            if user.get('full_name'):
                st.caption(user['full_name'])
            
            st.divider()
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
        
        else:
            # Login/Register tabs
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="demo@example.com")
                    password = st.text_input("Password", type="password", placeholder="demo123")
                    submit = st.form_submit_button("Login", use_container_width=True)
                    
                    if submit:
                        if email and password:
                            with st.spinner("Logging in..."):
                                result = login(email, password)
                                
                                if result:
                                    token = result.get("access_token")
                                    # For demo, create a simple user object
                                    user = {"email": email, "full_name": "Demo User"}
                                    login_user(token, user)
                                    st.success("✅ Logged in successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid credentials")
                        else:
                            st.error("Please fill in all fields")
            
            with tab2:
                with st.form("register_form"):
                    reg_email = st.text_input("Email", key="reg_email")
                    reg_name = st.text_input("Full Name", key="reg_name")
                    reg_password = st.text_input("Password", type="password", key="reg_password")
                    reg_submit = st.form_submit_button("Register", use_container_width=True)
                    
                    if reg_submit:
                        if reg_email and reg_password:
                            with st.spinner("Creating account..."):
                                result = create_user(reg_email, reg_password, reg_name)
                                
                                if result:
                                    st.success("✅ Account created! Please login.")
                                else:
                                    st.error("❌ Registration failed. Email may already exist.")
                        else:
                            st.error("Please fill in email and password")
        
        st.divider()
        
        # Navigation
        st.markdown("### 📍 Navigation")
        
        # Always show these
        pages = {
            "🏠 Home": "Home.py",
            "📊 Dashboard": "pages/1_📊_Dashboard.py",
            "📋 Subscriptions": "pages/2_📋_Subscriptions.py",
            "📈 Analytics": "pages/3_📈_Analytics.py",
            "💡 Recommendations": "pages/4_💡_Recommendations.py",
            "💰 Alternatives": "pages/5_💰_Alternatives.py",
            "📱 SMS Transactions": "pages/6_📱_SMS_Transactions.py",
        }
        
        for label, page in pages.items():
            if st.button(label, use_container_width=True, key=f"nav_{page}"):
                st.switch_page(page)
