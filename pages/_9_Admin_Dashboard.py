import streamlit as st
from datetime import datetime
from backend.database import SessionLocal
from backend.models.employee import Employee
from backend.models.user import User
from backend.models.notification import Notification

def show():
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            }
            .main .block-container {
                padding-top: 1rem;
            }
            .page-title {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 5px;
            }
            .page-subtitle {
                color: #a0aec0;
                font-size: 14px;
                margin-bottom: 20px;
            }
            
            .section-card {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 20px 24px;
                margin-bottom: 20px;
            }
            .section-title {
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .section-title .badge {
                font-size: 12px;
                font-weight: 400;
                color: #a0aec0;
                background: rgba(255,255,255,0.06);
                padding: 4px 14px;
                border-radius: 20px;
            }
            
            .metric-card {
                background: rgba(255,255,255,0.06);
                border-radius: 12px;
                padding: 20px 22px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.06);
                transition: all 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-4px);
                background: rgba(255,255,255,0.10);
                border-color: rgba(102, 126, 234, 0.3);
            }
            .metric-value {
                font-size: 32px;
                font-weight: 700;
                color: #ffffff;
            }
            .metric-label {
                color: #a0aec0;
                font-size: 13px;
            }
            
            .status-card {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                padding: 15px 18px;
                border: 1px solid rgba(255,255,255,0.06);
            }
            .status-card .status-label {
                color: #a0aec0;
                font-size: 12px;
            }
            .status-card .status-value {
                color: #48bb78;
                font-size: 15px;
                font-weight: 600;
            }
            .status-card .status-time {
                color: #4a5568;
                font-size: 11px;
            }
            
            .info-row {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            .info-row:last-child {
                border-bottom: none;
            }
            .info-row .label {
                color: #a0aec0;
                font-size: 13px;
            }
            .info-row .value {
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            
            .admin-card {
                background: rgba(102,126,234,0.08);
                border: 1px solid rgba(102,126,234,0.15);
                border-radius: 12px;
                padding: 15px 18px;
                transition: all 0.3s ease;
            }
            .admin-card:hover {
                background: rgba(102,126,234,0.15);
                border-color: rgba(102,126,234,0.3);
            }
            .admin-card .admin-label {
                color: #a0aec0;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .admin-card .admin-value {
                color: #ffffff;
                font-size: 18px;
                font-weight: 700;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Admin Dashboard</div>
        <div class="page-subtitle">System overview and management</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    # ============================================================
    # GET DATA
    # ============================================================
    total_employees = db.query(Employee).filter(Employee.department != "HR").count()
    total_hr = db.query(Employee).filter(Employee.department == "HR").count()
    total_users = db.query(User).count()
    total_notifications = db.query(Notification).count()
    
    # Active employees
    active_employees = db.query(Employee).filter(
        Employee.status == "Active",
        Employee.department != "HR"
    ).count()
    
    # Inactive employees
    inactive_employees = db.query(Employee).filter(
        Employee.status == "Inactive",
        Employee.department != "HR"
    ).count()
    
    db.close()
    
    # ============================================================
    # STATS
    # ============================================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_employees + total_hr}</div>
                <div class="metric-label">Total Staff</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_employees}</div>
                <div class="metric-label">Employees</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_hr}</div>
                <div class="metric-label">HR Staff</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_users}</div>
                <div class="metric-label">Total Users</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================================
    # SYSTEM STATUS
    # ============================================================
    st.markdown("""
        <div class="section-card">
            <div class="section-title">
                System Status
                <span class="badge">Health</span>
            </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="status-card">
                <div class="status-label">Database Status</div>
                <div class="status-value">Connected</div>
                <div class="status-time">Active</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="status-card">
                <div class="status-label">Total Records</div>
                <div class="status-value">{total_employees + total_hr}</div>
                <div class="status-time">Employees + HR</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="status-card">
                <div class="status-label">Notifications</div>
                <div class="status-value">{total_notifications}</div>
                <div class="status-time">Total Notifications</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # QUICK INFO
    # ============================================================
    st.markdown("""
        <div class="section-card">
            <div class="section-title">
                System Information
                <span class="badge">v2.0</span>
            </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="info-row">
                <span class="label">Total Employees</span>
                <span class="value">{total_employees}</span>
            </div>
            <div class="info-row">
                <span class="label">HR Staff</span>
                <span class="value">{total_hr}</span>
            </div>
            <div class="info-row">
                <span class="label">Active Employees</span>
                <span class="value">{active_employees}</span>
            </div>
            <div class="info-row">
                <span class="label">Inactive Employees</span>
                <span class="value">{inactive_employees}</span>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="info-row">
                <span class="label">Total Users</span>
                <span class="value">{total_users}</span>
            </div>
            <div class="info-row">
                <span class="label">Notifications</span>
                <span class="value">{total_notifications}</span>
            </div>
            <div class="info-row">
                <span class="label">System Version</span>
                <span class="value">v2.0.0</span>
            </div>
            <div class="info-row">
                <span class="label">Current Date</span>
                <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)