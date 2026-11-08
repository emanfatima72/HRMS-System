import streamlit as st
import pandas as pd
from datetime import datetime
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.employee import Employee
from backend.models.admin_promotion import AdminPromotion
from backend.models.promotion import Promotion
from backend.models.attendance import Attendance
from backend.models.leave import Leave
from backend.models.payroll import Payroll
from utils.audit_logger import add_audit_log, get_current_user

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
            .section-title .badge {
                font-size: 12px; font-weight: 400; color: #a0aec0;
                background: rgba(255,255,255,0.06); padding: 4px 14px; border-radius: 20px;
            }
            
            .stDataFrame {
                background: rgba(255,255,255,0.05) !important;
                backdrop-filter: blur(10px) !important;
                border-radius: 16px !important;
                border: 1px solid rgba(255,255,255,0.08) !important;
                padding: 10px !important;
            }
            .stDataFrame th { color: #a0aec0 !important; font-weight: 500 !important; padding: 12px 8px !important; border-bottom: 1px solid rgba(255,255,255,0.1) !important; }
            .stDataFrame td { color: #cbd5e0 !important; padding: 12px 8px !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; }
            .stDataFrame tbody tr td:first-child { color: #ffffff !important; font-weight: 500 !important; }
            
            .stat-box { background: rgba(255,255,255,0.04); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.06); }
            .stat-box .number { font-size: 28px; font-weight: 700; color: #ffffff; }
            .stat-box .label { color: #a0aec0; font-size: 12px; }
            
            .status-badge {
                padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 500; display: inline-block;
            }
            .status-active { background: #48bb78; color: white; }
            .status-inactive { background: #fc8181; color: white; }
            
            .profile-card {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                padding: 12px 16px;
                border: 1px solid rgba(255,255,255,0.06);
                margin: 4px 0;
            }
            .profile-card .label { color: #a0aec0; font-size: 12px; }
            .profile-card .value { color: #ffffff; font-size: 14px; font-weight: 500; }
            
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
            
            .out-modal {
                background: rgba(237,137,54,0.08);
                border: 1px solid rgba(237,137,54,0.2);
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0;
            }
            .out-modal .title { color: #ed8936; font-size: 18px; font-weight: 700; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Current & Old HR</div>
        <div class="page-subtitle">Manage current and former HR staff</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    def get_current_hr_employees():
        return db.query(Employee).filter(
            Employee.department == "HR",
            Employee.status == "Active"
        ).all()
    
    def get_old_hr_employees():
        return db.query(Employee).filter(
            Employee.department == "HR",
            Employee.status.in_(["Inactive", "Exited", "Rejected"])
        ).all()
    
    def delete_hr_employee(employee_id):
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            emp_name = employee.name
            emp_email = employee.email
            try:
                db.query(AdminPromotion).filter(AdminPromotion.employee_id == employee_id).delete()
                db.query(Promotion).filter(Promotion.employee_id == employee_id).delete()
                db.query(Attendance).filter(Attendance.employee_id == employee_id).delete()
                db.query(Leave).filter(Leave.employee_id == employee_id).delete()
                db.query(Payroll).filter(Payroll.employee_id == employee_id).delete()
                
                db.delete(employee)
                db.commit()
                
                add_audit_log(
                    get_current_user(),
                    "Delete HR Employee",
                    f"Deleted HR employee: {emp_name} ({emp_email})"
                )
                return True
            except Exception as e:
                db.rollback()
                print(f"Error deleting employee: {str(e)}")
                return False
        return False
    
    def move_to_old_hr(employee_id, exit_type, exit_reason, exit_date):
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            employee.status = "Inactive"
            employee.exit_type = exit_type
            employee.exit_reason = exit_reason
            employee.exit_date = exit_date
            db.commit()
            db.refresh(employee)
            
            add_audit_log(
                get_current_user(),
                "Move HR to Old",
                f"Moved HR {employee.name} to Old - {exit_type}: {exit_reason or 'No reason'}"
            )
            return True
        return False
    
    def update_hr_employee(employee_id, data):
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            employee.name = data.get('name', employee.name)
            employee.first_name = data.get('first_name', employee.first_name)
            employee.last_name = data.get('last_name', employee.last_name)
            employee.email = data.get('email', employee.email)
            employee.phone = data.get('phone', employee.phone)
            employee.designation = data.get('designation', employee.designation)
            employee.department = data.get('department', employee.department)
            employee.city = data.get('city', employee.city)
            employee.education = data.get('education', employee.education)
            employee.skills = data.get('skills', employee.skills)
            employee.status = data.get('status', employee.status)
            db.commit()
            db.refresh(employee)
            return True
        return False
    
    if 'edit_hr' not in st.session_state:
        st.session_state.edit_hr = None
    
    if 'view_hr' not in st.session_state:
        st.session_state.view_hr = None
    
    if 'out_hr' not in st.session_state:
        st.session_state.out_hr = None
    
    tab1, tab2 = st.tabs(["Current HR", "Old HR"])
    
    with tab1:
        current_hr = get_current_hr_employees()
        
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    Current HR Staff
                    <span class="badge">{len(current_hr)} Active</span>
                </div>
        """, unsafe_allow_html=True)
        
        total_current = len(current_hr)
        active_count = sum(1 for h in current_hr if h.status == "Active")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="stat-box"><div class="number">{total_current}</div><div class="label">Total Current HR</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="stat-box"><div class="number" style="color:#48bb78;">{active_count}</div><div class="label">Active</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="stat-box"><div class="number" style="color:#ed8936;">{total_current - active_count}</div><div class="label">Inactive</div></div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        if current_hr:
            data = []
            for emp in current_hr:
                data.append({
                    "ID": emp.id,
                    "Name": emp.name,
                    "Email": emp.email,
                    "Designation": emp.designation or "N/A",
                    "Department": emp.department or "N/A",
                    "Status": "Active" if emp.status == "Active" else emp.status
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("### HR Actions")
            st.caption("View, Edit, OUT (to Old HR), or Delete")
            
            for idx, emp in enumerate(current_hr):
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 3])
                with col1:
                    st.markdown(f"**{emp.name}**")
                with col2:
                    if st.button("View", key=f"hr_view_{emp.id}", use_container_width=True):
                        st.session_state.view_hr = emp.id
                        st.rerun()
                with col3:
                    if st.button("Edit", key=f"hr_edit_{emp.id}", use_container_width=True):
                        st.session_state.edit_hr = emp.id
                        st.rerun()
                with col4:
                    if st.button("OUT", key=f"hr_out_{emp.id}", use_container_width=True):
                        st.session_state.out_hr = emp.id
                        st.rerun()
                with col5:
                    if st.button("Delete", key=f"hr_delete_{emp.id}", use_container_width=True):
                        if delete_hr_employee(emp.id):
                            st.success(f"HR {emp.name} deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete HR! Please try again.")
            
            if st.session_state.view_hr is not None:
                emp = db.query(Employee).filter(Employee.id == st.session_state.view_hr).first()
                if emp:
                    st.markdown("---")
                    st.markdown(f"### Profile: {emp.name}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            <div class="profile-card"><div class="label">ID</div><div class="value">{emp.id}</div></div>
                            <div class="profile-card"><div class="label">Full Name</div><div class="value">{emp.name}</div></div>
                            <div class="profile-card"><div class="label">Email</div><div class="value">{emp.email}</div></div>
                            <div class="profile-card"><div class="label">Phone</div><div class="value">{emp.phone or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">Designation</div><div class="value">{emp.designation or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">Department</div><div class="value">{emp.department or 'N/A'}</div></div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                            <div class="profile-card"><div class="label">Status</div><div class="value"><span class="status-badge status-active">{emp.status}</span></div></div>
                            <div class="profile-card"><div class="label">Joining Date</div><div class="value">{emp.joining_date.strftime('%Y-%m-%d') if emp.joining_date else 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">City</div><div class="value">{emp.city or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">LinkedIn</div><div class="value">{emp.linkedin or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">GitHub</div><div class="value">{emp.github or 'N/A'}</div></div>
                        """, unsafe_allow_html=True)
                    
                    if emp.education:
                        st.markdown("### Education")
                        edu_labels = {"matric": "Matric", "inter": "Inter", "bachelor": "Bachelor", "master": "Master", "phd": "PhD"}
                        edu_data = emp.education
                        for key, label in edu_labels.items():
                            value = edu_data.get(key, '') if isinstance(edu_data, dict) else ''
                            if value and value.strip():
                                st.markdown(f"- **{label}:** {value}")
                    
                    if emp.skills:
                        st.markdown("### Skills")
                        skills_html = ""
                        for skill in emp.skills:
                            if skill and skill.strip():
                                skills_html += f'<span class="skill-tag">{skill}</span>'
                        if skills_html:
                            st.markdown(skills_html, unsafe_allow_html=True)
                    
                    if st.button("Close Profile", use_container_width=True, key="close_hr_view"):
                        st.session_state.view_hr = None
                        st.rerun()
            
            if st.session_state.edit_hr is not None:
                emp = db.query(Employee).filter(Employee.id == st.session_state.edit_hr).first()
                if emp:
                    st.markdown("---")
                    st.markdown(f"### Edit Profile: {emp.name}")
                    
                    with st.form("edit_hr_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            first_name = st.text_input("First Name", value=emp.first_name or '')
                            last_name = st.text_input("Last Name", value=emp.last_name or '')
                            email = st.text_input("Email", value=emp.email)
                            phone = st.text_input("Phone", value=emp.phone or '')
                        with col2:
                            designation = st.text_input("Designation", value=emp.designation or '')
                            department = st.selectbox("Department", ["HR", "Recruitment", "Payroll", "Training"], 
                                                    index=["HR", "Recruitment", "Payroll", "Training"].index(emp.department) if emp.department in ["HR", "Recruitment", "Payroll", "Training"] else 0)
                            status = st.selectbox("Status", ["Active", "Inactive"], index=0 if emp.status == "Active" else 1)
                            city = st.text_input("City", value=emp.city or '')
                        
                        st.markdown("#### Education")
                        edu_labels = {"matric": "Matric", "inter": "Inter", "bachelor": "Bachelor", "master": "Master", "phd": "PhD"}
                        edu_data = emp.education if isinstance(emp.education, dict) else {}
                        for key, label in edu_labels.items():
                            value = edu_data.get(key, '')
                            st.text_input(label, value=value, key=f"edit_hr_edu_{key}")
                        
                        st.markdown("#### Skills")
                        skills_list = emp.skills if isinstance(emp.skills, list) else []
                        skills_str = ", ".join(skills_list) if skills_list else ""
                        skills_input = st.text_area("Skills (comma separated)", value=skills_str, height=80)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Save Changes", use_container_width=True):
                                edu_dict = {}
                                for key in edu_labels.keys():
                                    edu_dict[key] = st.session_state.get(f"edit_hr_edu_{key}", '')
                                skills_final = [s.strip() for s in skills_input.split(',') if s.strip()]
                                
                                update_data = {
                                    "name": f"{first_name} {last_name}".strip(),
                                    "first_name": first_name,
                                    "last_name": last_name,
                                    "email": email,
                                    "phone": phone,
                                    "designation": designation,
                                    "department": department,
                                    "status": status,
                                    "city": city,
                                    "education": edu_dict,
                                    "skills": skills_final
                                }
                                
                                if update_hr_employee(emp.id, update_data):
                                    st.success("HR profile updated successfully!")
                                    st.session_state.edit_hr = None
                                    st.rerun()
                                else:
                                    st.error("Failed to update HR!")
                        
                        with col2:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state.edit_hr = None
                                st.rerun()
            
            if st.session_state.out_hr is not None:
                emp = db.query(Employee).filter(Employee.id == st.session_state.out_hr).first()
                if emp:
                    st.markdown("---")
                    st.markdown(f"""
                        <div class="out-modal">
                            <div class="title">Move to Old HR</div>
                            <div style="color:#a0aec0;font-size:14px;margin-top:4px;">
                                Moving <strong style="color:#ffffff;">{emp.name}</strong> to Old HR
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form("out_hr_form"):
                        exit_type = st.selectbox("Exit Type", ["Resign", "Terminated", "Retired", "Runaway"])
                        exit_reason = st.text_area("Reason (optional)", placeholder="e.g., Resigned voluntarily")
                        exit_date = st.date_input("Exit Date", datetime.now())
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Confirm OUT", use_container_width=True):
                                if move_to_old_hr(emp.id, exit_type, exit_reason, exit_date):
                                    st.success(f"HR {emp.name} moved to Old HR with type: {exit_type}!")
                                    st.session_state.out_hr = None
                                    st.rerun()
                                else:
                                    st.error("Failed to move HR to Old!")
                        
                        with col2:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state.out_hr = None
                                st.rerun()
        else:
            st.info("No current HR staff found. Add HR from New HR Management page.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        old_hr = get_old_hr_employees()
        
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    Old HR Staff
                    <span class="badge">{len(old_hr)} Ex-HR</span>
                </div>
        """, unsafe_allow_html=True)
        
        total_old = len(old_hr)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="stat-box"><div class="number">{total_old}</div><div class="label">Total Old HR</div></div>""", unsafe_allow_html=True)
        with col2:
            resign_count = sum(1 for h in old_hr if h.exit_type == 'Resign')
            st.markdown(f"""<div class="stat-box"><div class="number" style="color:#48bb78;">{resign_count}</div><div class="label">Resign</div></div>""", unsafe_allow_html=True)
        with col3:
            term_count = sum(1 for h in old_hr if h.exit_type == 'Terminated')
            st.markdown(f"""<div class="stat-box"><div class="number" style="color:#fc8181;">{term_count}</div><div class="label">Terminated</div></div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        if old_hr:
            data = []
            for emp in old_hr:
                data.append({
                    "Name": emp.name,
                    "Designation": emp.designation or "N/A",
                    "Department": emp.department or "N/A",
                    "Email": emp.email,
                    "Phone": emp.phone or '-',
                    "Exit Type": emp.exit_type or "N/A",
                    "Exit Date": emp.exit_date.strftime("%Y-%m-%d") if emp.exit_date else "N/A",
                    "Reason": emp.exit_reason or "N/A",
                    "Status": emp.status
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("#### Delete Old HR Record")
            col1, col2 = st.columns([4, 1])
            with col1:
                del_options = {f"{emp.name} - {emp.exit_type} ({emp.exit_date.strftime('%Y-%m-%d') if emp.exit_date else 'N/A'})": emp.id for emp in old_hr}
                del_selected = st.selectbox("Select Record to Delete", list(del_options.keys()), key="del_old_hr")
                del_id = del_options[del_selected]
            with col2:
                if st.button("Delete", use_container_width=True):
                    if delete_hr_employee(del_id):
                        st.success("Old HR record deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete! Please try again.")
        else:
            st.info("No old HR records found.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    db.close()