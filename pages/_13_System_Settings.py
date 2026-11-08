import streamlit as st
from datetime import datetime
from backend.database import SessionLocal
from backend.models.employee import Employee

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
            .setting-row {
                display: flex; justify-content: space-between; align-items: center;
                padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            .setting-row:last-child { border-bottom: none; }
            .setting-label { color: #cbd5e0; font-size: 14px; font-weight: 500; }
            .setting-value { color: #a0aec0; font-size: 14px; }
            .setting-toggle {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 4px 16px;
                color: #ffffff;
                font-size: 12px;
                cursor: pointer;
            }
            .setting-toggle.on { background: rgba(72, 187, 120, 0.3); border-color: #48bb78; color: #48bb78; }
            .setting-toggle.off { background: rgba(252, 129, 129, 0.3); border-color: #fc8181; color: #fc8181; }
            .setting-input {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 6px 12px;
                color: #ffffff;
                font-size: 13px;
                width: 200px;
            }
            .setting-input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
            }
            .setting-select {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 6px 12px;
                color: #ffffff;
                font-size: 13px;
                width: 200px;
            }
            .setting-select:focus {
                outline: none;
                border-color: #667eea;
            }
            .setting-select option {
                background: #1a1a2e;
                color: #ffffff;
            }
            .edit-btn {
                background: rgba(102,126,234,0.2);
                border: 1px solid rgba(102,126,234,0.3);
                border-radius: 6px;
                padding: 4px 14px;
                color: #667eea;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .edit-btn:hover {
                background: rgba(102,126,234,0.4);
                border-color: rgba(102,126,234,0.6);
            }
            .save-btn {
                background: rgba(72,187,120,0.2);
                border: 1px solid rgba(72,187,120,0.3);
                border-radius: 6px;
                padding: 4px 14px;
                color: #48bb78;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .save-btn:hover {
                background: rgba(72,187,120,0.4);
                border-color: rgba(72,187,120,0.6);
            }
            .cancel-btn {
                background: rgba(252,129,129,0.2);
                border: 1px solid rgba(252,129,129,0.3);
                border-radius: 6px;
                padding: 4px 14px;
                color: #fc8181;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .cancel-btn:hover {
                background: rgba(252,129,129,0.4);
                border-color: rgba(252,129,129,0.6);
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">System Settings</div>
        <div class="page-subtitle">Configure system preferences and policies</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    # Get employee count for company settings
    total_employees = db.query(Employee).filter(Employee.department != "HR").count()
    db.close()
    
    # Initialize settings in session state
    if 'system_settings' not in st.session_state:
        st.session_state.system_settings = {
            "company_name": "HRMS Enterprise Suite",
            "industry": "Human Resource Management",
            "founded": "2024",
            "headquarters": "Lahore, Pakistan",
            "total_employees": str(total_employees),
            "annual_leaves": "20",
            "sick_leaves": "10",
            "casual_leaves": "5",
            "emergency_leaves": "3",
            "monthly_leave_limit": "5",
            "working_hours_start": "09:00",
            "working_hours_end": "18:00",
            "lunch_start": "13:00",
            "lunch_end": "14:00",
            "work_days": "Monday to Friday",
            "weekend": "Saturday & Sunday",
            "grace_period": "10"
        }
    
    # ============================================================
    # COMPANY SETTINGS
    # ============================================================
    st.markdown("""
        <div class="section-card">
            <div class="section-title">
                Company Settings
                <span class="badge">General</span>
            </div>
    """, unsafe_allow_html=True)
    
    company_settings = [
        {"key": "company_name", "label": "Company Name"},
        {"key": "industry", "label": "Industry"},
        {"key": "founded", "label": "Founded"},
        {"key": "headquarters", "label": "Headquarters"},
        {"key": "total_employees", "label": "Total Employees"}
    ]
    
    for s in company_settings:
        value = st.session_state.system_settings.get(s["key"], "")
        st.markdown(f"""
            <div class="setting-row">
                <span class="setting-label">{s['label']}</span>
                <span class="setting-value">{value}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # LEAVE POLICY - Editable
    # ============================================================
    st.markdown("""
        <div class="section-card">
            <div class="section-title">
                Leave Policy
                <span class="badge">HR Settings</span>
            </div>
    """, unsafe_allow_html=True)
    
    leave_settings = [
        {"key": "annual_leaves", "label": "Annual Leaves (days/year)"},
        {"key": "sick_leaves", "label": "Sick Leaves (days/year)"},
        {"key": "casual_leaves", "label": "Casual Leaves (days/year)"},
        {"key": "emergency_leaves", "label": "Emergency Leaves (days/year)"},
        {"key": "monthly_leave_limit", "label": "Monthly Leave Limit (days)"}
    ]
    
    # Show leave settings with edit option
    for s in leave_settings:
        key = s["key"]
        value = st.session_state.system_settings.get(key, "")
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f'<span class="setting-label">{s["label"]}</span>', unsafe_allow_html=True)
        with col2:
            edit_key = f"edit_{key}"
            if st.session_state.get(edit_key, False):
                new_val = st.text_input("", value=value, key=f"input_{key}", label_visibility="collapsed")
                st.session_state[f"temp_{key}"] = new_val
            else:
                st.markdown(f'<span class="setting-value">{value}</span>', unsafe_allow_html=True)
        with col3:
            edit_key = f"edit_{key}"
            if st.session_state.get(edit_key, False):
                col3_1, col3_2 = st.columns(2)
                with col3_1:
                    if st.button("Save", key=f"save_{key}", use_container_width=True):
                        temp_val = st.session_state.get(f"temp_{key}", value)
                        if temp_val:
                            st.session_state.system_settings[key] = temp_val
                            st.session_state[edit_key] = False
                            st.rerun()
                with col3_2:
                    if st.button("Cancel", key=f"cancel_{key}", use_container_width=True):
                        st.session_state[edit_key] = False
                        st.rerun()
            else:
                if st.button("Edit", key=f"edit_btn_{key}", use_container_width=True):
                    st.session_state[edit_key] = True
                    st.rerun()
        
        st.markdown('<div style="border-bottom:1px solid rgba(255,255,255,0.05);margin:4px 0;"></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # ATTENDANCE POLICY - Editable
    # ============================================================
    st.markdown("""
        <div class="section-card">
            <div class="section-title">
                Attendance Policy
                <span class="badge">HR Settings</span>
            </div>
    """, unsafe_allow_html=True)
    
    attendance_settings = [
        {"key": "working_hours_start", "label": "Working Hours Start"},
        {"key": "working_hours_end", "label": "Working Hours End"},
        {"key": "lunch_start", "label": "Lunch Start"},
        {"key": "lunch_end", "label": "Lunch End"},
        {"key": "work_days", "label": "Work Days"},
        {"key": "weekend", "label": "Weekend"},
        {"key": "grace_period", "label": "Grace Period (minutes)"}
    ]
    
    for s in attendance_settings:
        key = s["key"]
        value = st.session_state.system_settings.get(key, "")
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f'<span class="setting-label">{s["label"]}</span>', unsafe_allow_html=True)
        with col2:
            edit_key = f"edit_att_{key}"
            if st.session_state.get(edit_key, False):
                if key in ["work_days", "weekend"]:
                    new_val = st.text_input("", value=value, key=f"input_{key}", label_visibility="collapsed")
                else:
                    new_val = st.text_input("", value=value, key=f"input_{key}", label_visibility="collapsed")
                st.session_state[f"temp_{key}"] = new_val
            else:
                st.markdown(f'<span class="setting-value">{value}</span>', unsafe_allow_html=True)
        with col3:
            edit_key = f"edit_att_{key}"
            if st.session_state.get(edit_key, False):
                col3_1, col3_2 = st.columns(2)
                with col3_1:
                    if st.button("Save", key=f"save_att_{key}", use_container_width=True):
                        temp_val = st.session_state.get(f"temp_{key}", value)
                        if temp_val:
                            st.session_state.system_settings[key] = temp_val
                            st.session_state[edit_key] = False
                            st.rerun()
                with col3_2:
                    if st.button("Cancel", key=f"cancel_att_{key}", use_container_width=True):
                        st.session_state[edit_key] = False
                        st.rerun()
            else:
                if st.button("Edit", key=f"edit_att_btn_{key}", use_container_width=True):
                    st.session_state[edit_key] = True
                    st.rerun()
        
        st.markdown('<div style="border-bottom:1px solid rgba(255,255,255,0.05);margin:4px 0;"></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
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
    
    status_data = [
        {"label": "Database Status", "value": "Connected", "status": "on"},
        {"label": "API Status", "value": "Active", "status": "on"},
        {"label": "System Version", "value": "v2.0.0", "status": ""}
    ]
    
    for s in status_data:
        if s.get("status") == "on":
            display_value = f"{s['value']}"
        else:
            display_value = s["value"]
        st.markdown(f"""
            <div class="setting-row">
                <span class="setting-label">{s['label']}</span>
                <span class="setting-value">{display_value}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # RESET SETTINGS
    # ============================================================
    st.markdown("""
        <div class="section-card">
            <div class="section-title">
                Danger Zone
                <span class="badge">Reset</span>
            </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            <div style="color:#fc8181;font-size:13px;">
                Reset all settings to default values. This action cannot be undone.
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Reset to Default", use_container_width=True):
            st.session_state.system_settings = {
                "company_name": "HRMS Enterprise Suite",
                "industry": "Human Resource Management",
                "founded": "2024",
                "headquarters": "Lahore, Pakistan",
                "total_employees": "50+",
                "annual_leaves": "20",
                "sick_leaves": "10",
                "casual_leaves": "5",
                "emergency_leaves": "3",
                "monthly_leave_limit": "5",
                "working_hours_start": "09:00",
                "working_hours_end": "18:00",
                "lunch_start": "13:00",
                "lunch_end": "14:00",
                "work_days": "Monday to Friday",
                "weekend": "Saturday & Sunday",
                "grace_period": "10"
            }
            st.success("Settings reset to default values!")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)