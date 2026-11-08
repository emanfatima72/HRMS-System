import streamlit as st
import pandas as pd
from datetime import datetime
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.employee import Employee
from backend.models.attendance import Attendance
from backend.models.leave import Leave
from backend.models.payroll import Payroll
from backend.models.notification import Notification
from backend.models.admin_promotion import AdminPromotion
from backend.models.promotion import Promotion

def show():
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
            .main .block-container { padding-top: 1rem; }
            .page-title { font-size: 28px; font-weight: 700; color: #ffffff; margin-bottom: 5px; }
            .page-subtitle { color: #a0aec0; font-size: 14px; margin-bottom: 20px; }
            .section-card {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 20px 24px;
                margin-bottom: 20px;
            }
            .section-title {
                font-size: 16px; font-weight: 600; color: #ffffff; margin-bottom: 15px;
                display: flex; justify-content: space-between; align-items: center;
            }
            .section-title .badge { font-size: 12px; font-weight: 400; color: #a0aec0; background: rgba(255,255,255,0.06); padding: 4px 14px; border-radius: 20px; }
            .stDataFrame {
                background: rgba(255,255,255,0.05) !important; backdrop-filter: blur(10px) !important;
                border-radius: 16px !important; border: 1px solid rgba(255,255,255,0.08) !important;
                padding: 10px !important;
            }
            .stDataFrame th { color: #a0aec0 !important; font-weight: 500 !important; padding: 12px 8px !important; border-bottom: 1px solid rgba(255,255,255,0.1) !important; }
            .stDataFrame td { color: #cbd5e0 !important; padding: 12px 8px !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; }
            .stDataFrame tbody tr td:first-child { color: #ffffff !important; font-weight: 500 !important; }
            .form-row { display: flex; gap: 15px; flex-wrap: wrap; margin: 10px 0; }
            .form-row .form-group { flex: 1; min-width: 180px; }
            .form-row .form-group label { color: #a0aec0; font-size: 13px; display: block; margin-bottom: 4px; font-weight: 500; }
            .form-row .form-group select {
                width: 100%; padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.05); color: #ffffff; font-size: 13px;
            }
            .form-row .form-group select:focus {
                outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
            }
            .form-row .form-group select option {
                background: #1a1a2e; color: #ffffff;
            }
            .empty-state {
                text-align: center;
                padding: 40px 20px;
                color: #4a5568;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Audit Logs</div>
        <div class="page-subtitle">Track all system activities and user actions</div>
    """, unsafe_allow_html=True)
    
    # Initialize audit data in session state
    if 'audit_logs' not in st.session_state:
        st.session_state.audit_logs = []
    
    # ============================================================
    # FUNCTION TO ADD LOG ENTRY (Global)
    # ============================================================
    def add_audit_log(user, action, details, ip="192.168.0.1"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.audit_logs.insert(0, {
            "User": user,
            "Action": action,
            "Details": details,
            "IP": ip,
            "Timestamp": timestamp
        })
        # Keep only last 500 logs
        if len(st.session_state.audit_logs) > 500:
            st.session_state.audit_logs = st.session_state.audit_logs[:500]
    
    # Make function available globally
    st.session_state.add_audit_log = add_audit_log
    
    # ============================================================
    # GENERATE LOGS FROM DATABASE ON PAGE LOAD
    # ============================================================
    def generate_logs_from_db():
        db = SessionLocal()
        try:
            current_user = st.session_state.get('current_user', 'system')
            user_role = st.session_state.get('user_role', 'User')
            
            # Only add login log if not already added in this session
            if not any(log.get("Action") == "Login" and log.get("User") == current_user for log in st.session_state.audit_logs):
                add_audit_log(current_user, "Login", f"Logged in as {user_role}")
            
            # Get all counts from database
            emp_count = db.query(Employee).count()
            att_count = db.query(Attendance).count()
            leave_count = db.query(Leave).count()
            payroll_count = db.query(Payroll).count()
            promo_count = db.query(Promotion).count()
            admin_promo_count = db.query(AdminPromotion).count()
            notif_count = db.query(Notification).count()
            users_count = db.query(User).count()
            
            # Add view logs with counts
            add_audit_log(current_user, "View Dashboard", f"Total Records: Employees={emp_count}, HR={admin_promo_count}, Users={users_count}")
            
        except Exception as e:
            print(f"Error generating logs: {e}")
        finally:
            db.close()
    
    # Generate logs if empty
    if len(st.session_state.audit_logs) == 0:
        generate_logs_from_db()
    
    # ============================================================
    # FILTERS
    # ============================================================
    st.markdown("""
        <div class="section-card">
            <div class="section-title">
                Filter Logs
                <span class="badge">Search</span>
            </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        users = sorted(set([log.get("User", "") for log in st.session_state.audit_logs]))
        filter_user = st.selectbox("Filter by User", ["All Users"] + users)
    with col2:
        actions = sorted(set([log.get("Action", "") for log in st.session_state.audit_logs]))
        filter_action = st.selectbox("Filter by Action", ["All Actions"] + actions)
    with col3:
        date_filter = st.selectbox("Time Period", ["All Time", "Today", "Last 7 Days", "Last 30 Days"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # APPLY FILTERS
    # ============================================================
    filtered_logs = st.session_state.audit_logs.copy()
    
    if filter_user != "All Users":
        filtered_logs = [l for l in filtered_logs if l.get("User") == filter_user]
    if filter_action != "All Actions":
        filtered_logs = [l for l in filtered_logs if l.get("Action") == filter_action]
    
    if date_filter == "Today":
        today = datetime.now().strftime("%Y-%m-%d")
        filtered_logs = [l for l in filtered_logs if l.get("Timestamp", "").startswith(today)]
    elif date_filter == "Last 7 Days":
        from datetime import timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        filtered_logs = [l for l in filtered_logs if l.get("Timestamp", "") >= seven_days_ago]
    elif date_filter == "Last 30 Days":
        from datetime import timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        filtered_logs = [l for l in filtered_logs if l.get("Timestamp", "") >= thirty_days_ago]
    
    # ============================================================
    # DISPLAY LOGS
    # ============================================================
    st.markdown("""
        <div class="section-card">
            <div class="section-title">
                Activity Logs
                <span class="badge">{}</span>
            </div>
    """.format(len(filtered_logs)), unsafe_allow_html=True)
    
    if filtered_logs:
        df = pd.DataFrame(filtered_logs)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown(f"""
            <div style="color:#a0aec0;font-size:13px;margin-top:10px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);">
                Total Logs: <strong style="color:#ffffff;">{len(filtered_logs)}</strong>
            </div>
        """, unsafe_allow_html=True)
        
        # Clear logs button
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("Clear All", use_container_width=True):
                st.session_state.audit_logs = []
                st.success("All audit logs cleared!")
                st.rerun()
    else:
        st.markdown("""
            <div class="empty-state">
                <div style="font-size:48px;display:block;margin-bottom:10px;">📋</div>
                <div style="font-size:18px;color:#a0aec0;">No logs found</div>
                <div style="font-size:13px;">Try adjusting your filters</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)