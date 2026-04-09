"""Session state management"""

import streamlit as st


def init_session_state():
    """Initialize session state variables"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "token" not in st.session_state:
        st.session_state.token = None
    
    if "user" not in st.session_state:
        st.session_state.user = None
    
    if "refresh_data" not in st.session_state:
        st.session_state.refresh_data = False


def login_user(token: str, user: dict):
    """Set user as logged in"""
    st.session_state.logged_in = True
    st.session_state.token = token
    st.session_state.user = user


def logout_user():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.user = None


def is_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.get("logged_in", False)


def get_token() -> str:
    """Get current user token"""
    return st.session_state.get("token", None)


def trigger_refresh():
    """Trigger data refresh"""
    st.session_state.refresh_data = True


def clear_refresh():
    """Clear refresh flag"""
    st.session_state.refresh_data = False
