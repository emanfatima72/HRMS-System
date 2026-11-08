import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'employees' not in st.session_state:
        st.session_state.employees = []

def check_login(username, password):
    admin_user = os.getenv("ADMIN_USERNAME", "hr")
    admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
    return username == admin_user and password == admin_pass