# utils/audit_logger.py
import streamlit as st
from datetime import datetime

def add_audit_log(user, action, details, ip="192.168.0.1"):
    """Add audit log entry to session state"""
    if 'audit_logs' not in st.session_state:
        st.session_state.audit_logs = []
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_logs.insert(0, {
        "User": user or "system",
        "Action": action,
        "Details": details,
        "IP": ip,
        "Timestamp": timestamp
    })
    
    # Keep only last 500 logs
    if len(st.session_state.audit_logs) > 500:
        st.session_state.audit_logs = st.session_state.audit_logs[:500]

def get_current_user():
    """Get current logged in user"""
    return st.session_state.get('current_user', 'system')