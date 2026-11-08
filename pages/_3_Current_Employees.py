import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
from backend.database import SessionLocal
from backend.models.employee import Employee
from backend.models.attendance import Attendance
from utils.audit_logger import add_audit_log, get_current_user

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
                padding: 15px 18px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.06);
                transition: all 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-4px);
                background: rgba(255,255,255,0.10);
                border-color: rgba(102, 126, 234, 0.3);
            }
            .metric-value { font-size: 28px; font-weight: 700; color: #ffffff; }
            .metric-label { color: #a0aec0; font-size: 13px; }
            
            .profile-card {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                padding: 12px 16px;
                border: 1px solid rgba(255,255,255,0.06);
                margin: 4px 0;
            }
            .profile-card .label {
                color: #a0aec0;
                font-size: 12px;
            }
            .profile-card .value {
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
            }
            
            .skill-tag {
                display: inline-block;
                background: rgba(102, 126, 234, 0.2);
                color: #cbd5e0;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                margin: 3px 5px 3px 0;
                border: 1px solid rgba(102, 126, 234, 0.15);
            }
            
            .badge-permanent {
                background: rgba(72,187,120,0.2);
                color: #48bb78;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                display: inline-block;
            }
            .badge-temporary {
                background: rgba(237,137,54,0.2);
                color: #ed8936;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                display: inline-block;
            }
            .badge-contract {
                background: rgba(102,126,234,0.2);
                color: #9f7aea;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                display: inline-block;
            }
            
            .stDataFrame {
                background: rgba(255,255,255,0.05) !important;
                backdrop-filter: blur(10px) !important;
                border-radius: 16px !important;
                border: 1px solid rgba(255,255,255,0.08) !important;
                padding: 10px !important;
            }
            .stDataFrame table {
                width: 100% !important;
            }
            .stDataFrame th {
                color: #a0aec0 !important;
                font-weight: 500 !important;
                padding: 12px 8px !important;
                border-bottom: 1px solid rgba(255,255,255,0.1) !important;
            }
            .stDataFrame td {
                color: #cbd5e0 !important;
                padding: 12px 8px !important;
                border-bottom: 1px solid rgba(255,255,255,0.05) !important;
            }
            .stDataFrame tbody tr:hover {
                background: rgba(255,255,255,0.03) !important;
            }
            .stDataFrame tbody tr td:first-child {
                color: #ffffff !important;
                font-weight: 500 !important;
            }
            
            .action-btn {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px;
                padding: 4px 10px;
                color: #a0aec0;
                font-size: 11px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 3px;
            }
            .action-btn:hover {
                background: rgba(102,126,234,0.15);
                border-color: rgba(102,126,234,0.3);
                color: #ffffff;
            }
            .action-btn.view:hover {
                background: rgba(102,126,234,0.2);
                border-color: rgba(102,126,234,0.4);
                color: #667eea;
            }
            .action-btn.edit:hover {
                background: rgba(72,187,120,0.2);
                border-color: rgba(72,187,120,0.4);
                color: #48bb78;
            }
            .action-btn.delete:hover {
                background: rgba(252,129,129,0.2);
                border-color: rgba(252,129,129,0.4);
                color: #fc8181;
            }
            .action-btn.out:hover {
                background: rgba(237,137,54,0.2);
                border-color: rgba(237,137,54,0.4);
                color: #ed8936;
            }
            
            .form-row {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin: 10px 0;
            }
            .form-row .form-group {
                flex: 1;
                min-width: 180px;
            }
            .form-row .form-group label {
                color: #a0aec0;
                font-size: 13px;
                display: block;
                margin-bottom: 4px;
                font-weight: 500;
            }
            .form-row .form-group input, 
            .form-row .form-group select {
                width: 100%;
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.05);
                color: #ffffff;
                font-size: 13px;
            }
            .form-row .form-group input:focus,
            .form-row .form-group select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
            }
            .form-row .form-group select option {
                background: #1a1a2e;
                color: #ffffff;
            }
            
            .out-modal {
                background: rgba(237,137,54,0.08);
                border: 1px solid rgba(237,137,54,0.2);
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0;
            }
            .out-modal .title {
                color: #ed8936;
                font-size: 18px;
                font-weight: 700;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Current Employees</div>
        <div class="page-subtitle">Active employees with profile access (Excluding HR)</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    def get_non_hr_employees():
        return db.query(Employee).filter(
            Employee.status == "Active",
            Employee.department != "HR"
        ).all()
    
    def get_employee_by_email(email):
        return db.query(Employee).filter(Employee.email == email).first()
    
    def update_employee_in_db(email, update_data):
        emp = db.query(Employee).filter(Employee.email == email).first()
        if emp:
            for key, value in update_data.items():
                setattr(emp, key, value)
            db.commit()
            db.refresh(emp)
            return True
        return False
    
    def move_employee_to_old(email, exit_type, exit_reason=""):
        emp = db.query(Employee).filter(Employee.email == email).first()
        if emp:
            emp.status = "Inactive"
            emp.exit_type = exit_type
            emp.exit_date = datetime.now().date()
            emp.exit_reason = exit_reason
            db.commit()
            db.refresh(emp)
            
            add_audit_log(
                get_current_user(),
                "Move Employee to Old",
                f"Moved employee {emp.name} to Old - {exit_type}"
            )
            return True
        return False
    
    def delete_employee_from_db(email):
        emp = db.query(Employee).filter(Employee.email == email).first()
        if emp:
            db.query(Attendance).filter(Attendance.employee_id == emp.id).delete()
            db.delete(emp)
            db.commit()
            return True
        return False
    
    def load_full_profile_from_db(email):
        emp = db.query(Employee).filter(Employee.email == email).first()
        if emp:
            return {
                "first_name": emp.first_name or "",
                "last_name": emp.last_name or "",
                "phone": emp.phone or "",
                "address": emp.address or "",
                "city": emp.city or "",
                "linkedin": emp.linkedin or "",
                "github": emp.github or "",
                "dob": emp.dob or "",
                "department": emp.department or "",
                "employee_type": emp.employee_type or "",
                "salary": emp.salary or 0,
                "joining_date": emp.joining_date.strftime("%Y-%m-%d") if emp.joining_date else "",
                "active_days": emp.active_days or 0,
                "extra_work": emp.extra_work or 0,
                "education": emp.education or {},
                "skills": emp.skills or [],
                "cv_path": emp.cv_path or "",
                "photo1": emp.photo1 or "",
                "photo2": emp.photo2 or "",
                "criminal_letter": emp.criminal_letter or "",
                "additional_docs": emp.additional_docs or []
            }
        return {}
    
    employees = get_non_hr_employees()
    
    current_data = []
    for emp in employees:
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
    
    if 'current_employees_data' not in st.session_state:
        st.session_state.current_employees_data = current_data
    
    if 'edit_employee' not in st.session_state:
        st.session_state.edit_employee = None
    
    if 'view_employee' not in st.session_state:
        st.session_state.view_employee = None
    
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    if 'old_employees_data' not in st.session_state:
        st.session_state.old_employees_data = []
    
    if 'employee_profiles' not in st.session_state:
        st.session_state.employee_profiles = {}
    
    total = len(current_data)
    permanent = sum(1 for e in current_data if e.get('Type') == "Permanent")
    temporary = sum(1 for e in current_data if e.get('Type') == "Temporary")
    contract = sum(1 for e in current_data if e.get('Type') == "Contract")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total}</div>
                <div class="metric-label">Total Employees</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{permanent}</div>
                <div class="metric-label">Permanent</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{temporary}</div>
                <div class="metric-label">Temporary</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{contract}</div>
                <div class="metric-label">Contract</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    search_query = st.text_input(
        "Search",
        placeholder="Search by name, email, ID, or department...",
        key="search_query",
        label_visibility="collapsed"
    )
    
    filtered_data = current_data
    if search_query:
        search_lower = search_query.lower()
        filtered_data = [
            e for e in current_data 
            if search_lower in e.get('Name', '').lower() or 
               search_lower in e.get('Email', '').lower() or 
               search_lower in e.get('emp_id', '').lower() or
               search_lower in e.get('Department', '').lower()
        ]
    
    if filtered_data:
        st.markdown(f"""
            <div style="color:#a0aec0;font-size:13px;margin-bottom:12px;">
                Showing <strong style="color:#ffffff;">{len(filtered_data)}</strong> of <strong style="color:#ffffff;">{total}</strong> employees
            </div>
        """, unsafe_allow_html=True)
        
        display_data = []
        for emp in filtered_data:
            display_data.append({
                "Employee ID": emp.get('emp_id', 'N/A'),
                "Name": emp.get('Name', 'N/A'),
                "Type": emp.get('Type', 'N/A'),
                "Department": emp.get('Department', 'N/A'),
                "Salary": f"PKR {int(emp.get('Salary', 0)):,}" if emp.get('Salary', 0) else "N/A",
                "Email": emp.get('Email', 'N/A')
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### Employee Actions")
        st.caption("View, Edit, Move OUT (to Old Employees), or Delete")
        
        for idx, emp in enumerate(filtered_data):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 3])
            
            with col1:
                st.markdown(f"**{emp.get('Name', 'N/A')}**")
            
            with col2:
                if st.button("View", key=f"view_{idx}_{emp.get('emp_id', '')}", use_container_width=True):
                    orig_idx = current_data.index(emp) if emp in current_data else idx
                    st.session_state.view_employee = orig_idx
                    st.rerun()
            
            with col3:
                if st.button("Edit", key=f"edit_{idx}_{emp.get('emp_id', '')}", use_container_width=True):
                    orig_idx = current_data.index(emp) if emp in current_data else idx
                    st.session_state.edit_employee = orig_idx
                    st.rerun()
            
            with col4:
                if st.button("OUT", key=f"out_{idx}_{emp.get('emp_id', '')}", use_container_width=True):
                    st.session_state.out_employee = idx
                    st.rerun()
            
            with col5:
                if st.button("Delete", key=f"delete_{idx}_{emp.get('emp_id', '')}", use_container_width=True):
                    if delete_employee_from_db(emp.get('Email')):
                        st.session_state.current_employees_data = [e for e in current_data if e.get('Email') != emp.get('Email')]
                        if emp.get('Email') in st.session_state.employee_profiles:
                            del st.session_state.employee_profiles[emp.get('Email')]
                        st.success(f"Employee {emp.get('Name')} deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete employee!")
        
        if st.session_state.get('out_employee') is not None:
            idx = st.session_state.out_employee
            if idx < len(current_data):
                emp = current_data[idx]
                
                st.markdown("---")
                st.markdown(f"""
                    <div class="out-modal">
                        <div class="title">Move to Old Employees</div>
                        <div style="color:#a0aec0;font-size:14px;margin-top:4px;">
                            Moving <strong style="color:#ffffff;">{emp.get('Name', 'N/A')}</strong> to Old Employees
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.form("out_employee_form"):
                    st.markdown("#### Select Exit Type")
                    exit_type = st.selectbox("Exit Type", ["Proper Resign", "Terminated", "Runaway"])
                    exit_reason = st.text_area("Reason (optional)", placeholder="e.g., Resigned voluntarily, Performance issues, etc.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Confirm OUT", use_container_width=True):
                            if move_employee_to_old(emp.get('Email'), exit_type, exit_reason):
                                st.session_state.current_employees_data = [e for e in current_data if e.get('Email') != emp.get('Email')]
                                if emp.get('Email') in st.session_state.employee_profiles:
                                    del st.session_state.employee_profiles[emp.get('Email')]
                                st.success(f"Employee {emp.get('Name')} moved to Old Employees with type: {exit_type}!")
                                st.session_state.out_employee = None
                                st.rerun()
                            else:
                                st.error("Failed to move employee!")
                    
                    with col2:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.session_state.out_employee = None
                            st.rerun()
        
        if st.session_state.view_employee is not None:
            idx = st.session_state.view_employee
            if idx < len(current_data):
                emp = current_data[idx]
                
                st.markdown("---")
                st.markdown(f"### Profile: {emp['Name']}")
                
                full_profile = load_full_profile_from_db(emp.get('Email'))
                if not full_profile:
                    full_profile = st.session_state.employee_profiles.get(emp.get('Email'), {})
                
                def get_download_link(file_name, file_display):
                    try:
                        file_path = os.path.join("uploads", file_name)
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                data = f.read()
                            b64 = base64.b64encode(data).decode()
                            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}" style="color:#667eea;text-decoration:underline;">{file_display}</a>'
                            return href
                        else:
                            return f'<span style="color:#4a5568;">{file_display} (file not found)</span>'
                    except:
                        return f'<span style="color:#4a5568;">{file_display}</span>'
                
                salary_val = full_profile.get('salary', 0)
                if salary_val is None:
                    salary_val = 0
                salary_str = f"PKR {int(salary_val):,}" if salary_val else "PKR 0"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        <div class="profile-card"><div class="label">Employee ID</div><div class="value">{emp.get('emp_id', 'N/A')}</div></div>
                        <div class="profile-card"><div class="label">Full Name</div><div class="value">{full_profile.get('first_name', '')} {full_profile.get('last_name', '')}</div></div>
                        <div class="profile-card"><div class="label">Email</div><div class="value">{emp.get('Email', 'N/A')}</div></div>
                        <div class="profile-card"><div class="label">Phone</div><div class="value">{full_profile.get('phone', 'N/A')}</div></div>
                        <div class="profile-card"><div class="label">Address</div><div class="value">{full_profile.get('address', 'N/A')}</div></div>
                        <div class="profile-card"><div class="label">City</div><div class="value">{full_profile.get('city', 'N/A')}</div></div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class="profile-card"><div class="label">Department</div><div class="value">{full_profile.get('department', 'N/A')}</div></div>
                        <div class="profile-card"><div class="label">Employee Type</div><div class="value">{full_profile.get('employee_type', 'N/A')}</div></div>
                        <div class="profile-card"><div class="label">Salary</div><div class="value">{salary_str}</div></div>
                        <div class="profile-card"><div class="label">Joining Date</div><div class="value">{full_profile.get('joining_date', 'N/A')}</div></div>
                        <div class="profile-card"><div class="label">Active Days</div><div class="value">{full_profile.get('active_days', 0)}</div></div>
                        <div class="profile-card"><div class="label">Extra Work (Hrs)</div><div class="value">{full_profile.get('extra_work', 0)}</div></div>
                    """, unsafe_allow_html=True)
                
                if full_profile.get('education'):
                    st.markdown("### Education")
                    edu_labels = {"matric": "Matric", "inter": "Inter", "bachelor": "Bachelor", "master": "Master", "phd": "PhD"}
                    for key, label in edu_labels.items():
                        value = full_profile['education'].get(key, '')
                        if value:
                            st.markdown(f"- **{label}:** {value}")
                
                if full_profile.get('skills'):
                    st.markdown("### Skills")
                    skills_html = ""
                    for skill in full_profile['skills']:
                        if skill and skill.strip():
                            skills_html += f'<span class="skill-tag">{skill}</span>'
                    if skills_html:
                        st.markdown(skills_html, unsafe_allow_html=True)
                
                if st.button("Close Profile", use_container_width=True, key="close_view_profile"):
                    st.session_state.view_employee = None
                    st.rerun()
        
        if st.session_state.edit_employee is not None:
            idx = st.session_state.edit_employee
            if idx < len(current_data):
                emp = current_data[idx]
                
                full_profile = load_full_profile_from_db(emp.get('Email'))
                if not full_profile:
                    full_profile = st.session_state.employee_profiles.get(emp.get('Email'), {})
                
                st.markdown("---")
                st.markdown(f"### Edit Profile: {emp['Name']}")
                
                with st.form("edit_employee_form"):
                    st.markdown("#### Personal Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name", value=full_profile.get('first_name', ''))
                        last_name = st.text_input("Last Name", value=full_profile.get('last_name', ''))
                        email = st.text_input("Email", value=emp.get('Email', ''))
                        phone = st.text_input("Phone", value=full_profile.get('phone', ''))
                    with col2:
                        city = st.text_input("City", value=full_profile.get('city', ''))
                        linkedin = st.text_input("LinkedIn", value=full_profile.get('linkedin', ''))
                        github = st.text_input("GitHub", value=full_profile.get('github', ''))
                    
                    st.markdown("#### Employment Details")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        department = st.selectbox("Department", ["IT", "Marketing", "Finance", "Operations"], 
                                                index=["IT", "Marketing", "Finance", "Operations"].index(full_profile.get('department', 'IT')) if full_profile.get('department', 'IT') in ["IT", "Marketing", "Finance", "Operations"] else 0)
                    with col2:
                        emp_type_list = ["Permanent", "Temporary", "Contract"]
                        current_type = full_profile.get('employee_type', 'Permanent')
                        if current_type not in emp_type_list:
                            current_type = "Permanent"
                        employee_type = st.selectbox("Employee Type", emp_type_list, index=emp_type_list.index(current_type))
                    with col3:
                        salary = st.number_input("Salary (PKR)", min_value=0, value=int(full_profile.get('salary', 0) or 0), step=1000)
                    
                    st.markdown("#### Education")
                    edu_data = full_profile.get('education', {})
                    edu_fields = [
                        {"key": "matric", "label": "Matriculation / O-Levels"},
                        {"key": "inter", "label": "Intermediate / A-Levels"},
                        {"key": "bachelor", "label": "Bachelor's Degree"},
                        {"key": "master", "label": "Master's Degree"},
                        {"key": "phd", "label": "PhD / Doctorate"}
                    ]
                    for edu_field in edu_fields:
                        key = edu_field["key"]
                        value = edu_data.get(key, '')
                        st.text_input(edu_field["label"], value=value, key=f"edit_edu_{key}")
                    
                    st.markdown("#### Skills")
                    skills_list = full_profile.get('skills', [])
                    skills_str = ", ".join(skills_list) if skills_list else ""
                    skills_input = st.text_area("Skills (comma separated)", value=skills_str, height=80)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save Changes", use_container_width=True):
                            edu_dict = {}
                            for edu_field in edu_fields:
                                key = edu_field["key"]
                                edu_dict[key] = st.session_state.get(f"edit_edu_{key}", '')
                            
                            skills_final = [s.strip() for s in skills_input.split(',') if s.strip()]
                            
                            update_data = {
                                "first_name": first_name,
                                "last_name": last_name,
                                "name": f"{first_name} {last_name}".strip() if first_name or last_name else emp.get('Name', ''),
                                "email": email,
                                "phone": phone,
                                "city": city,
                                "linkedin": linkedin,
                                "github": github,
                                "education": edu_dict,
                                "skills": skills_final,
                                "department": department,
                                "employee_type": employee_type,
                                "salary": salary
                            }
                            
                            if update_employee_in_db(emp.get('Email'), update_data):
                                st.session_state.employee_profiles[email] = update_data
                                emp['Name'] = update_data['name']
                                emp['Email'] = email
                                emp['Type'] = employee_type
                                emp['Department'] = department
                                emp['Salary'] = salary
                                
                                st.success(f"Employee {emp['Name']} updated successfully!")
                                st.session_state.edit_employee = None
                                st.rerun()
                            else:
                                st.error("Failed to update employee!")
                    
                    with col2:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.session_state.edit_employee = None
                            st.rerun()
        
        st.markdown(f"""
            <div style="color:#a0aec0;font-size:13px;margin-top:10px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);">
                Total Current Employees: <strong style="color:#ffffff;">{total}</strong>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No current employees found.")
    
    db.close()