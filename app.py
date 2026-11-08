import streamlit as st
from utils.auth import init_session, check_login
from utils.db_utils import init_db
from backend.database import SessionLocal
from backend.models.employee import Employee
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="HRMS - Premium Suite",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
init_session()
init_db()

# ============================================================
# LOAD DATA FROM DATABASE INTO SESSION STATE
# ============================================================
def load_data_from_db():
    db = SessionLocal()
    try:
        active_emps = db.query(Employee).filter(
            Employee.status == "Active",
            Employee.department != "HR"
        ).all()
        current_data = []
        for emp in active_emps:
            current_data.append({
                "emp_id": emp.emp_id or f"EMP-{emp.id:06d}",
                "Name": emp.name,
                "Type": emp.employee_type or "Permanent",
                "Department": emp.department or "IT",
                "Salary": emp.salary or 0,
                "Active Days": emp.active_days or 0,
                "Extra Work (Hrs)": emp.extra_work or 0,
                "Email": emp.email,
                "Joining Date": emp.joining_date.strftime("%Y-%m-%d") if emp.joining_date else "N/A"
            })
        st.session_state.current_employees_data = current_data
        
        inactive_emps = db.query(Employee).filter(
            Employee.status == "Inactive",
            Employee.department != "HR"
        ).all()
        old_data = []
        for emp in inactive_emps:
            old_data.append({
                "Name": emp.name,
                "Exit Type": emp.exit_type or "N/A",
                "Last Designation": emp.designation or "N/A",
                "Exit Date": emp.exit_date.strftime("%Y-%m-%d") if emp.exit_date else "N/A",
                "Reason": emp.exit_reason or "N/A",
                "Email": emp.email,
                "Emp ID": emp.emp_id or f"EMP-{emp.id:06d}"
            })
        st.session_state.old_employees_data = old_data
        
        all_emps = db.query(Employee).filter(Employee.department != "HR").all()
        for emp in all_emps:
            st.session_state.employee_profiles[emp.email] = {
                "emp_id": emp.emp_id or f"EMP-{emp.id:06d}",
                "first_name": emp.first_name or "",
                "last_name": emp.last_name or "",
                "full_name": emp.name,
                "email": emp.email,
                "phone": emp.phone or "",
                "address": emp.address or "",
                "city": emp.city or "",
                "linkedin": emp.linkedin or "",
                "github": emp.github or "",
                "dob": emp.dob or "",
                "education": emp.education or {},
                "skills": emp.skills or [],
                "cv_path": emp.cv_path or "",
                "photo1": emp.photo1 or "",
                "photo2": emp.photo2 or "",
                "additional_docs": emp.additional_docs or [],
                "criminal_letter": emp.criminal_letter or "",
                "salary": emp.salary or 0,
                "employee_type": emp.employee_type or "Permanent",
                "department": emp.department or "IT",
                "joining_date": emp.joining_date.strftime("%Y-%m-%d") if emp.joining_date else "N/A",
                "active_days": emp.active_days or 0,
                "extra_work": emp.extra_work or 0,
                "status": emp.status
            }
    finally:
        db.close()

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'notification_categories' not in st.session_state:
    st.session_state.notification_categories = ["Weather", "Leaves", "Event", "Emergency", "General"]
if 'current_employees_data' not in st.session_state:
    st.session_state.current_employees_data = []
if 'old_employees_data' not in st.session_state:
    st.session_state.old_employees_data = []
if 'employee_profiles' not in st.session_state:
    st.session_state.employee_profiles = {}
if 'show_profile' not in st.session_state:
    st.session_state.show_profile = None
if 'old_show_profile' not in st.session_state:
    st.session_state.old_show_profile = None
if 'data_loaded' not in st.session_state:
    load_data_from_db()
    st.session_state.data_loaded = True

# ============================================================
# RESPONSIVE CSS - HIDE STREAMLIT DEFAULT UI
# ============================================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp [data-testid="stSidebarNav"] {display: none !important;}
        .stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:first-child {display: none !important;}
        .stApp [data-testid="collapsedControl"] {display: none !important;}
        
        section[data-testid="stSidebar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            transform: translateX(0px) !important;
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
            padding-top: 20px !important;
            padding-bottom: 15px !important;
            height: 100vh !important;
            overflow: hidden !important;
            z-index: 999 !important;
            border-right: 1px solid rgba(255,255,255,0.05) !important;
            transition: all 0.3s ease !important;
            width: 280px !important;
            min-width: 280px !important;
            max-width: 280px !important;
            
            display: flex !important;
            flex-direction: column !important;
        }
        section[data-testid="stSidebar"] + section {
            margin-left: 280px !important;
        }
        
        .sidebar-content {
            flex: 1 1 auto !important;
            overflow-y: auto !important;
            padding-right: 5px !important;
        }
        .sidebar-content::-webkit-scrollbar {
            width: 3px;
        }
        .sidebar-content::-webkit-scrollbar-track {
            background: transparent;
        }
        .sidebar-content::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
        }
        
        .sidebar-footer {
            flex-shrink: 0 !important;
            padding-top: 12px !important;
            margin-top: auto !important;
            border-top: 1px solid rgba(255,255,255,0.05) !important;
            width: 100% !important;
        }
        .sidebar-footer .logout-label {
            text-align: center;
            color: #4a5568;
            font-size: 10px;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .sidebar-footer .logout-btn .stButton button {
            background: linear-gradient(135deg, #fc8181 0%, #e53e3e 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 30px !important;
            padding: 10px 20px !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            width: 100% !important;
            letter-spacing: 1px;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            box-shadow: 0 4px 15px rgba(229, 62, 62, 0.2) !important;
        }
        .sidebar-footer .logout-btn .stButton button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 8px 30px rgba(229, 62, 62, 0.4) !important;
        }
        .sidebar-footer .footer-version {
            text-align: center;
            color: #4a5568;
            font-size: 9px;
            padding-top: 6px;
            letter-spacing: 1px;
        }
        
        @media (max-width: 1024px) {
            section[data-testid="stSidebar"] {
                width: 240px !important;
                min-width: 240px !important;
                max-width: 240px !important;
            }
            section[data-testid="stSidebar"] + section {
                margin-left: 240px !important;
            }
        }
        
        @media (max-width: 768px) {
            section[data-testid="stSidebar"] {
                width: 0px !important;
                min-width: 0px !important;
                max-width: 0px !important;
                padding: 0 !important;
                overflow: hidden !important;
                border-right: none !important;
            }
            section[data-testid="stSidebar"] + section {
                margin-left: 0px !important;
            }
            .stApp [data-testid="collapsedControl"] {
                display: flex !important;
                position: fixed !important;
                top: 10px !important;
                left: 10px !important;
                z-index: 1000 !important;
                background: linear-gradient(135deg, #667eea, #764ba2) !important;
                border-radius: 50% !important;
                padding: 8px 12px !important;
                color: white !important;
                font-size: 18px !important;
                cursor: pointer !important;
                border: none !important;
                box-shadow: 0 4px 15px rgba(102,126,234,0.4) !important;
            }
            .stApp [data-testid="collapsedControl"]:hover {
                transform: scale(1.05) !important;
                box-shadow: 0 6px 25px rgba(102,126,234,0.6) !important;
            }
        }
        
        .main .block-container {
            padding: 1rem !important;
            max-width: 100% !important;
        }
        
        .stDataFrame {
            overflow-x: auto !important;
        }
        .stDataFrame table {
            width: 100% !important;
            min-width: 600px !important;
        }
        
        .metric-card, .stat-box, .section-card {
            width: 100% !important;
        }
        
        @media (max-width: 576px) {
            .row {
                flex-direction: column !important;
            }
            .col {
                width: 100% !important;
                flex: 0 0 100% !important;
                max-width: 100% !important;
            }
        }
        
        @media (max-width: 768px) {
            .page-title {
                font-size: 22px !important;
            }
            .metric-value {
                font-size: 24px !important;
            }
            .stat-box .number {
                font-size: 22px !important;
            }
            .dash-title {
                font-size: 22px !important;
            }
        }
        @media (max-width: 576px) {
            .page-title {
                font-size: 18px !important;
            }
            .metric-value {
                font-size: 20px !important;
            }
            .stat-box .number {
                font-size: 18px !important;
            }
        }
        
        @media (max-width: 768px) {
            .login-container {
                flex-direction: column !important;
                border-radius: 20px !important;
                max-height: 95vh !important;
                margin: 10px !important;
            }
            .login-left {
                padding: 20px !important;
                text-align: center !important;
            }
            .login-left .brand-title {
                font-size: 28px !important;
            }
            .login-right {
                margin: 10px !important;
                padding: 20px !important;
            }
            .login-bottom-links {
                flex-direction: column !important;
                gap: 8px !important;
                align-items: center !important;
            }
        }
        
        .stButton button {
            width: 100% !important;
        }
        @media (min-width: 768px) {
            .stButton button {
                width: auto !important;
            }
        }
        
        .out-modal, .rejected-card, .section-card {
            margin: 10px !important;
        }
        @media (max-width: 576px) {
            .out-modal, .rejected-card, .section-card {
                margin: 5px !important;
                padding: 12px !important;
            }
        }
        
        .stRadio > div {
            gap: 2px !important;
        }
        .stRadio label {
            padding: 6px 14px !important;
            font-size: 13px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# LOGIN PAGE
# ============================================================
if not st.session_state.get('logged_in', False):
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {display: none !important;}
            .stApp [data-testid="collapsedControl"] {display: none !important;}
            .stApp [data-testid="stSidebarNav"] {display: none !important;}
            
            .stApp {
                background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
                height: 100vh;
                overflow: hidden;
            }
            
            .login-bg {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 0;
                background: 
                    linear-gradient(135deg, rgba(15, 12, 41, 0.6) 0%, rgba(48, 43, 99, 0.7) 50%, rgba(36, 36, 62, 0.8) 100%),
                    url('https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1600&q=80');
                background-size: cover;
                background-position: center;
                filter: blur(6px) brightness(0.5);
                transform: scale(1.05);
            }
            
            .login-wrapper {
                position: relative;
                z-index: 2;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                padding: 20px;
                overflow: hidden;
            }
            
            .login-container {
                display: flex;
                max-width: 850px;
                width: 100%;
                background: rgba(255, 255, 255, 0.06);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
                max-height: 90vh;
            }
            
            .login-left {
                flex: 0.9;
                padding: 40px 35px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .login-left .brand-title {
                font-size: 38px;
                font-weight: 800;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: 1px;
            }
            .login-left .brand-sub {
                color: #a0aec0;
                font-size: 12px;
                letter-spacing: 4px;
                text-transform: uppercase;
                margin-top: 4px;
            }
            
            .login-right {
                flex: 1.1;
                background: rgba(255, 255, 255, 0.10);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 20px;
                padding: 30px 35px 25px 35px;
                margin: 15px 20px 15px 10px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .login-right .form-title {
                font-size: 24px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 4px;
            }
            .login-right .form-subtitle {
                color: #a0aec0;
                font-size: 14px;
                margin-bottom: 18px;
            }
            
            .login-right .input-label {
                color: #cbd5e0 !important;
                font-weight: 500;
                font-size: 13px;
                margin-bottom: 4px;
                display: block;
            }
            .login-right .input-field input, .login-right .role-select select {
                background: rgba(255,255,255,0.08) !important;
                border: 1px solid rgba(255,255,255,0.12) !important;
                border-radius: 10px !important;
                padding: 10px 14px !important;
                color: #ffffff !important;
                font-size: 14px !important;
                width: 100% !important;
            }
            .login-right .input-field input:focus, .login-right .role-select select:focus {
                border-color: #667eea !important;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
            }
            .login-right .role-select select option {
                background: #1a1a2e;
                color: #ffffff;
            }
            
            .login-right .signin-btn button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 30px !important;
                padding: 12px !important;
                font-weight: 700 !important;
                font-size: 15px !important;
                width: 100% !important;
                letter-spacing: 1px;
                transition: all 0.3s ease !important;
                cursor: pointer !important;
            }
            .login-right .signin-btn button:hover {
                transform: scale(1.02) !important;
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4) !important;
            }
            
            .login-right .login-error {
                text-align: center;
                color: #fc8181;
                font-size: 14px;
                margin-top: 10px;
                background: rgba(252, 129, 129, 0.1);
                padding: 8px;
                border-radius: 10px;
                border: 1px solid rgba(252, 129, 129, 0.2);
            }
            
            .login-bottom-links {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 12px;
                padding: 0 5px;
            }
            .login-bottom-links a {
                color: #a0aec0;
                font-size: 13px;
                text-decoration: none;
                transition: all 0.3s ease;
            }
            .login-bottom-links a:hover {
                color: #667eea;
                text-decoration: underline;
            }
            
            .form-options {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 12px 0 18px 0;
            }
            .form-options .remember {
                color: #cbd5e0;
                font-size: 13px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .form-options .remember input {
                accent-color: #667eea;
                width: 16px;
                height: 16px;
            }
            
            @media (max-width: 768px) {
                .login-container {
                    flex-direction: column;
                    border-radius: 20px;
                    max-height: 95vh;
                    margin: 10px;
                }
                .login-left {
                    padding: 20px;
                    text-align: center;
                }
                .login-left .brand-title {
                    font-size: 28px;
                }
                .login-right {
                    margin: 10px;
                    padding: 20px;
                }
                .login-bottom-links {
                    flex-direction: column;
                    gap: 8px;
                    align-items: center;
                }
            }
        </style>
    """, unsafe_allow_html=True)
    
    # ===== BACKGROUND =====
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # LEFT SIDE
    st.markdown("""
        <div class="login-left">
            <div class="brand-title">HRMS Portal</div>
            <div class="brand-sub">Enterprise Suite</div>
        </div>
    """, unsafe_allow_html=True)
    
    # RIGHT SIDE
    st.markdown("""
        <div class="login-right">
            <div class="form-title">Welcome Back</div>
            <div class="form-subtitle">Sign in to your HRMS account</div>
    """, unsafe_allow_html=True)
    
    # ROLE
    st.markdown('<div class="input-label">Select Role</div>', unsafe_allow_html=True)
    st.markdown('<div class="role-select">', unsafe_allow_html=True)
    role = st.selectbox("Role", ["HR", "Admin"], key="login_role", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # USERNAME
    st.markdown('<div class="input-label" style="margin-top:12px;">Email / Username</div>', unsafe_allow_html=True)
    st.markdown('<div class="input-field">', unsafe_allow_html=True)
    username = st.text_input("Username", placeholder="Enter your email or username", key="login_user", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PASSWORD
    st.markdown('<div class="input-label" style="margin-top:12px;">Password</div>', unsafe_allow_html=True)
    st.markdown('<div class="input-field">', unsafe_allow_html=True)
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # OPTIONS
    st.markdown("""
        <div class="form-options">
            <label class="remember"><input type="checkbox" checked> Remember me</label>
        </div>
    """, unsafe_allow_html=True)
    
    # SIGN IN
    st.markdown('<div class="signin-btn">', unsafe_allow_html=True)
    if st.button("SIGN IN", width="stretch"):
        if role == "HR" and username == "hr" and password == "hr@portal1166":
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.session_state.user_role = "HR"
            load_data_from_db()
            st.rerun()
        elif role == "Admin" and username == "admin" and password == "admin@portal1166":
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.session_state.user_role = "Admin"
            load_data_from_db()
            st.rerun()
        else:
            st.markdown(f'<div class="login-error">Invalid credentials! Use <b>{role.lower()}</b> / <b>{role.lower()}@portal1166</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="login-bottom-links">
            <a>Sign in with Google</a>
            <a>Forgot Password?</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# DASHBOARD (Role-Based Interface)
# ============================================================
else:
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("""
            <style>
                .stApp [data-testid="stSidebarNav"] {display: none !important;}
                .stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:first-child {display: none !important;}
                .stApp [data-testid="stSidebar"] {
                    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                    padding-top: 20px;
                    padding-bottom: 15px;
                    min-height: 100vh;
                    display: flex !important;
                    flex-direction: column !important;
                    overflow: hidden !important;
                    height: 100vh !important;
                }
                .stApp [data-testid="stSidebar"] * {color: #ffffff !important;}
                .stApp [data-testid="stSidebar"] .stRadio label {
                    color: #a0aec0 !important;
                    font-weight: 400;
                    padding: 6px 14px !important;
                    border-radius: 8px;
                    transition: all 0.3s ease;
                    font-size: 13px !important;
                }
                .stApp [data-testid="stSidebar"] .stRadio label:hover {
                    background: rgba(255,255,255,0.08);
                    color: #ffffff !important;
                }
                .stApp [data-testid="stSidebar"] .stRadio [role="radiogroup"] [aria-checked="true"] {
                    background: rgba(102, 126, 234, 0.2) !important;
                    border-radius: 8px;
                    border-left: 3px solid #667eea;
                }
                .stApp [data-testid="stSidebar"] hr {
                    border-color: rgba(255,255,255,0.05) !important;
                    margin: 6px 0 !important;
                }
                
                .sidebar-content {
                    flex: 1 1 auto !important;
                    overflow-y: auto !important;
                    padding-right: 3px !important;
                }
                .sidebar-content::-webkit-scrollbar {
                    width: 3px;
                }
                .sidebar-content::-webkit-scrollbar-track {
                    background: transparent;
                }
                .sidebar-content::-webkit-scrollbar-thumb {
                    background: rgba(255,255,255,0.15);
                    border-radius: 10px;
                }
                
                .sidebar-footer {
                    flex-shrink: 0 !important;
                    padding-top: 10px !important;
                    margin-top: auto !important;
                    border-top: 1px solid rgba(255,255,255,0.05) !important;
                    width: 100% !important;
                }
                .sidebar-footer .logout-label {
                    text-align: center;
                    color: #4a5568;
                    font-size: 10px;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }
                .sidebar-footer .logout-btn .stButton button {
                    background: linear-gradient(135deg, #fc8181 0%, #e53e3e 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 30px !important;
                    padding: 10px 20px !important;
                    font-weight: 700 !important;
                    font-size: 14px !important;
                    width: 100% !important;
                    letter-spacing: 1px;
                    transition: all 0.3s ease !important;
                    cursor: pointer !important;
                    box-shadow: 0 4px 15px rgba(229, 62, 62, 0.2) !important;
                }
                .sidebar-footer .logout-btn .stButton button:hover {
                    transform: scale(1.02) !important;
                    box-shadow: 0 8px 30px rgba(229, 62, 62, 0.4) !important;
                }
                .sidebar-footer .footer-version {
                    text-align: center;
                    color: #4a5568;
                    font-size: 9px;
                    padding-top: 4px;
                    letter-spacing: 1px;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # ===== SIDEBAR CONTENT (Scrollable) =====
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # LOGO
        st.markdown("""
            <div style="text-align:center;padding:5px 0 10px 0;">
                <div style="font-size:36px;font-weight:800;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:2px;">HRMS</div>
                <div style="font-size:9px;color:#718096;letter-spacing:4px;text-transform:uppercase;">Enterprise Suite</div>
                <hr style="border:none;height:2px;width:40px;margin:6px auto;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:10px;">
            </div>
        """, unsafe_allow_html=True)
        
        # ABOUT
        st.markdown("""
            <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:10px 12px;margin:4px 0 8px 0;border:1px solid rgba(255,255,255,0.06);text-align:center;">
                <div style="font-size:12px;font-weight:700;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:1px;">About HR</div>
                <hr style="border:none;height:1px;width:25px;margin:4px auto;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:10px;">
                <div style="color:#a0aec0;font-size:10px;line-height:1.3;">
                    Streamline workforce with <span style="color:#cbd5e0;font-weight:500;">AI-powered</span><br>
                    HR solutions for modern enterprises.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # STATS
        total_emps = len(st.session_state.current_employees_data) + len(st.session_state.old_employees_data)
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:8px 12px;margin:4px 0 8px 0;border:1px solid rgba(255,255,255,0.06);">
                <div style="display:flex;justify-content:space-between;padding:3px 0;font-size:12px;">
                    <span style="color:#a0aec0;">Total Employees</span>
                    <span style="color:#9f7aea;font-weight:600;">{total_emps}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:3px 0;font-size:12px;">
                    <span style="color:#a0aec0;">Active</span>
                    <span style="color:#48bb78;font-weight:600;">{len(st.session_state.current_employees_data)}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:3px 0;font-size:12px;">
                    <span style="color:#a0aec0;">Inactive</span>
                    <span style="color:#fc8181;font-weight:600;">{len(st.session_state.old_employees_data)}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<hr style="border:none;height:1px;background:rgba(255,255,255,0.05);margin:6px 0;">', unsafe_allow_html=True)
        
        # USER
        role_display = "HR" if st.session_state.user_role == "HR" else "Admin"
        st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:4px 0;">
                <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-size:18px;color:white;font-weight:600;box-shadow:0 4px 15px rgba(102,126,234,0.3);">{role_display[0]}</div>
                <div>
                    <div style="font-size:15px;font-weight:700;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{st.session_state.current_user}</div>
                    <span style="background:rgba(102,126,234,0.2);border:1px solid rgba(102,126,234,0.3);color:#a0aec0;padding:1px 10px;border-radius:20px;font-size:8px;font-weight:600;">{role_display}</span>
                    <div style="color:#48bb78;font-size:10px;display:flex;align-items:center;gap:3px;">
                        <span style="width:5px;height:5px;border-radius:50%;background:#48bb78;display:inline-block;"></span> Online
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<hr style="border:none;height:1px;background:rgba(255,255,255,0.05);margin:6px 0;">', unsafe_allow_html=True)
        
        # ===== NAVIGATION =====
        st.markdown('<div style="font-size:10px;font-weight:600;color:#718096;text-transform:uppercase;letter-spacing:1.5px;padding:6px 0 3px 0;">Navigation</div>', unsafe_allow_html=True)
        
        if st.session_state.user_role == "HR":
            menu = st.radio(
                "Navigation Menu",
                ["Dashboard", "Old Employees", "Current Employees", "New Employee", "Notifications", "Payroll", "Attendance", "Leaves"],
                index=0,
                label_visibility="collapsed"
            )
        else:
            menu = st.radio(
                "Navigation Menu",
                ["Admin Dashboard", "HR Management", "Current & Old HR", "HR Salary", "HR Promotion", "System Settings", "Audit Logs"],
                index=0,
                label_visibility="collapsed"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)  # End sidebar-content
        
        # ===== LOGOUT BUTTON - FIXED AND VISIBLE =====
        st.markdown("""
            <div class="sidebar-footer">
                <div class="logout-label">Account</div>
                <div class="logout-btn">
        """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("LOGOUT", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.current_user = None
            st.rerun()
        
        st.markdown("""
                </div>
                <div class="footer-version">v2.0 HRMS</div>
            </div>
        """, unsafe_allow_html=True)
    
    # ============================================================
    # PAGE ROUTER
    # ============================================================
    if st.session_state.user_role == "HR":
        if menu == "Dashboard":
            from pages import _1_Dashboard as dash
            dash.show()
        elif menu == "Old Employees":
            from pages import _2_Old_Employees as old
            old.show()
        elif menu == "Current Employees":
            from pages import _3_Current_Employees as current
            current.show()
        elif menu == "New Employee":
            from pages import _4_New_Employee as new
            new.show()
        elif menu == "Notifications":
            from pages import _5_Notifications as notif
            notif.show()
        elif menu == "Payroll":
            from pages import _6_Payroll as payroll
            payroll.show()
        elif menu == "Attendance":
            from pages import _7_Attendance as attendance
            attendance.show()
        elif menu == "Leaves":
            from pages import _8_Leaves as leaves
            leaves.show()
    
    else:  # Admin
        if menu == "Admin Dashboard":
            try:
                from pages import _9_Admin_Dashboard as admin_dash
                admin_dash.show()
            except ImportError:
                st.info("Admin Dashboard - Coming Soon")
        
        elif menu == "HR Management":
            try:
                from pages import _10_HR_Management as hr_mgmt
                hr_mgmt.show()
            except ImportError:
                st.info("HR Management - Coming Soon")
        
        elif menu == "Current & Old HR":
            try:
                from pages import _11_HR_Current_Old as hr_current_old
                hr_current_old.show()
            except ImportError:
                st.info("Current & Old HR - Coming Soon")
        
        elif menu == "HR Salary":
            try:
                from pages import _11_HR_Salary as hr_salary
                hr_salary.show()
            except ImportError:
                st.info("HR Salary - Coming Soon")
        
        elif menu == "HR Promotion":
            try:
                from pages import _12_HR_Promotion as hr_promo
                hr_promo.show()
            except ImportError:
                st.info("HR Promotion - Coming Soon")
        
        elif menu == "System Settings":
            try:
                from pages import _13_System_Settings as sys_settings
                sys_settings.show()
            except ImportError:
                st.info("System Settings - Coming Soon")
        
        elif menu == "Audit Logs":
            try:
                from pages import _14_Audit_Logs as audit_logs
                audit_logs.show()
            except ImportError:
                st.info("Audit Logs - Coming Soon")