import streamlit as st
import pandas as pd
import json
from datetime import datetime
from backend.database import SessionLocal
from backend.models.employee import Employee
from backend.models.promotion import Promotion
from backend.models.admin_promotion import AdminPromotion
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
            .metric-value {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
            }
            .metric-label {
                color: #a0aec0;
                font-size: 13px;
            }
            
            .status-pending {
                background: rgba(237,137,54,0.2);
                color: #ed8936;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                display: inline-block;
            }
            .status-approved {
                background: rgba(72,187,120,0.2);
                color: #48bb78;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                display: inline-block;
            }
            .status-rejected {
                background: rgba(252,129,129,0.2);
                color: #fc8181;
                padding: 4px 14px;
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
            
            .promotion-card {
                background: rgba(102,126,234,0.05);
                border: 1px solid rgba(102,126,234,0.12);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
            }
            .promotion-card .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .promotion-card .emp-name {
                color: #ffffff;
                font-weight: 600;
                font-size: 16px;
            }
            .promotion-card .emp-dept {
                color: #a0aec0;
                font-size: 13px;
            }
            .promotion-card .details {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
                margin-top: 8px;
            }
            .promotion-card .details .item {
                color: #cbd5e0;
                font-size: 13px;
            }
            .promotion-card .details .item .label {
                color: #a0aec0;
            }
            .promotion-card .details .item .value {
                color: #48bb78;
                font-weight: 600;
            }
            .admin-badge {
                background: rgba(102,126,234,0.2);
                color: #667eea;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 500;
                margin-left: 8px;
            }
            .employee-badge {
                background: rgba(72,187,120,0.2);
                color: #48bb78;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 500;
                margin-left: 8px;
            }
            .divider {
                border: none;
                height: 2px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                margin: 30px 0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Employee & HR Promotions</div>
        <div class="page-subtitle">Manage employee promotions - Separate systems for Employees and HR</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    def get_all_active_employees():
        return db.query(Employee).filter(Employee.status == "Active").all()
    
    def get_current_hr_employees():
        return db.query(Employee).filter(Employee.status == "Active", Employee.department == "HR").all()
    
    def get_emp_promotions():
        return db.query(Promotion).join(Employee, Promotion.employee_id == Employee.id).order_by(Promotion.created_at.desc()).all()
    
    def get_emp_pending():
        return db.query(Promotion).join(Employee, Promotion.employee_id == Employee.id).filter(Promotion.status == "Pending").all()
    
    def save_emp_promotion(employee_id, current_designation, new_designation, current_salary, new_salary, reason, recommendation_by):
        promo = Promotion(
            employee_id=employee_id,
            current_designation=current_designation,
            new_designation=new_designation,
            current_salary=current_salary,
            new_salary=new_salary,
            reason=reason,
            recommendation_by=recommendation_by,
            status="Pending"
        )
        db.add(promo)
        db.commit()
        db.refresh(promo)
        return promo
    
    def update_emp_status(promo_id, status):
        promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
        if promo:
            promo.status = status
            if status == "Approved":
                emp = db.query(Employee).filter(Employee.id == promo.employee_id).first()
                if emp:
                    emp.designation = promo.new_designation
                    emp.salary = promo.new_salary
            promo.approved_on = datetime.now()
            db.commit()
            db.refresh(promo)
            return True
        return False
    
    def delete_emp_promotion(promo_id):
        promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
        if promo:
            db.delete(promo)
            db.commit()
            return True
        return False
    
    def get_admin_promotions():
        return db.query(AdminPromotion).join(Employee, AdminPromotion.employee_id == Employee.id).order_by(AdminPromotion.created_at.desc()).all()
    
    def get_admin_pending():
        return db.query(AdminPromotion).join(Employee, AdminPromotion.employee_id == Employee.id).filter(AdminPromotion.status == "Pending").all()
    
    def save_admin_promotion(employee_id, current_designation, new_designation, current_salary, new_salary, reason, recommendation_by):
        promo = AdminPromotion(
            employee_id=employee_id,
            current_designation=current_designation,
            new_designation=new_designation,
            current_salary=current_salary,
            new_salary=new_salary,
            reason=reason,
            recommendation_by=recommendation_by,
            status="Pending"
        )
        db.add(promo)
        db.commit()
        db.refresh(promo)
        
        # Add audit log
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        add_audit_log(
            get_current_user(),
            "HR Promotion Request",
            f"Promotion request for {emp.name if emp else 'N/A'}: {current_designation} -> {new_designation} (PKR {new_salary:,.0f})"
        )
        return promo
    
    def update_admin_status(promo_id, status):
        promo = db.query(AdminPromotion).filter(AdminPromotion.id == promo_id).first()
        if promo:
            promo.status = status
            emp = db.query(Employee).filter(Employee.id == promo.employee_id).first()
            
            if status == "Approved":
                if emp:
                    emp.designation = promo.new_designation
                    emp.salary = promo.new_salary
                    promo.approved_by = "Admin"
                    
                    add_audit_log(
                        get_current_user(),
                        "Approve HR Promotion",
                        f"Approved promotion for {emp.name}: {promo.current_designation} -> {promo.new_designation} (PKR {promo.new_salary:,.0f})"
                    )
            else:
                add_audit_log(
                    get_current_user(),
                    "Reject HR Promotion",
                    f"Rejected promotion for {emp.name if emp else 'N/A'}"
                )
            
            promo.approved_on = datetime.now()
            db.commit()
            db.refresh(promo)
            return True
        return False
    
    def delete_admin_promotion(promo_id):
        promo = db.query(AdminPromotion).filter(AdminPromotion.id == promo_id).first()
        if promo:
            db.delete(promo)
            db.commit()
            return True
        return False
    
    all_employees = get_all_active_employees()
    hr_employees = get_current_hr_employees()
    emp_promotions = get_emp_promotions()
    emp_pending = get_emp_pending()
    admin_promotions = get_admin_promotions()
    admin_pending = get_admin_pending()
    
    col_emp, col_admin = st.columns(2)
    
    with col_emp:
        st.markdown("""
            <div style="
                background: rgba(72,187,120,0.05);
                border: 1px solid rgba(72,187,120,0.2);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
            ">
                <h3 style="color: #48bb78; margin: 0;">Employee Side <span class="employee-badge">All Employees</span></h3>
                <p style="color: #a0aec0; font-size: 13px; margin: 5px 0 0 0;">All active employees - Uses 'promotions' table</p>
            </div>
        """, unsafe_allow_html=True)
        
        emp_total = len(emp_promotions)
        emp_pending_count = len(emp_pending)
        emp_approved = sum(1 for p in emp_promotions if p.status == "Approved")
        emp_rejected = sum(1 for p in emp_promotions if p.status == "Rejected")
        
        emp_col1, emp_col2, emp_col3, emp_col4 = st.columns(4)
        with emp_col1:
            st.metric("Total", emp_total)
        with emp_col2:
            st.metric("Pending", emp_pending_count)
        with emp_col3:
            st.metric("Approved", emp_approved)
        with emp_col4:
            st.metric("Rejected", emp_rejected)
        
        st.markdown("---")
        
        emp_tab1, emp_tab2, emp_tab3 = st.tabs(["Recommend", "Pending", "History"])
        
        with emp_tab1:
            with st.form("emp_promotion_form"):
                st.markdown("##### Employee Promotion Request")
                
                if all_employees:
                    emp_options = {f"{emp.name} - {emp.designation or 'N/A'}": emp.id for emp in all_employees}
                    selected_emp = st.selectbox("Select Employee", list(emp_options.keys()), key="emp_emp")
                    emp_id = emp_options[selected_emp]
                    selected_emp_obj = next((e for e in all_employees if e.id == emp_id), None)
                    
                    rec_by = st.selectbox("Recommended By", ["HR Manager", "Department Head", "Team Lead", "CEO"], key="emp_rec")
                    
                    if selected_emp_obj:
                        st.text_input("Current Designation", value=selected_emp_obj.designation or "N/A", disabled=True, key="emp_curr_desig")
                        st.number_input("Current Salary (PKR)", value=selected_emp_obj.salary or 0, disabled=True, key="emp_curr_sal")
                        
                        with st.expander("View Education Details"):
                            education = selected_emp_obj.education
                            if education:
                                try:
                                    if isinstance(education, str):
                                        education = json.loads(education)
                                    if isinstance(education, dict):
                                        for key, value in education.items():
                                            if value and value != "Missing" and value != "N/A" and value != "":
                                                if isinstance(value, dict):
                                                    st.write(f"**{key}:**")
                                                    for sub_key, sub_value in value.items():
                                                        if sub_value and sub_value != "Missing" and sub_value != "N/A" and sub_value != "":
                                                            st.write(f"  - {sub_key}: {sub_value}")
                                                else:
                                                    st.write(f"**{key}:** {value}")
                                    else:
                                        st.write(str(education))
                                except:
                                    st.write(str(education))
                            else:
                                st.write("No education data available")
                    
                    st.markdown("---")
                    new_desig = st.text_input("New Designation *", placeholder="e.g., Senior Software Engineer", key="emp_new_desig")
                    new_sal = st.number_input("New Salary (PKR) *", min_value=0, value=50000, step=1000, key="emp_new_sal")
                    reason = st.text_area("Reason *", placeholder="Explain why...", height=60, key="emp_reason")
                    
                    if st.form_submit_button("Submit Employee Promotion", use_container_width=True):
                        if new_desig and new_sal and reason and selected_emp_obj and new_sal > (selected_emp_obj.salary or 0):
                            save_emp_promotion(emp_id, selected_emp_obj.designation or "N/A", new_desig, selected_emp_obj.salary or 0, new_sal, reason, rec_by)
                            st.success(f"Employee Promotion submitted for {selected_emp_obj.name}!")
                            st.rerun()
                        else:
                            st.error("Please fill all fields and ensure salary is higher!")
                else:
                    st.info("No active employees found.")
        
        with emp_tab2:
            if emp_pending:
                for promo in emp_pending:
                    emp = promo.employee
                    st.markdown(f"""
                        <div class="promotion-card">
                            <div class="header">
                                <div>
                                    <div class="emp-name">{emp.name}</div>
                                    <div class="emp-dept">{emp.department or 'N/A'} - {emp.designation or 'N/A'}</div>
                                </div>
                                <span class="status-pending">Pending</span>
                            </div>
                            <div class="details">
                                <div class="item"><span class="label">Current:</span> {promo.current_designation}</div>
                                <div class="item"><span class="label">New:</span> <span style="color:#667eea;">{promo.new_designation}</span></div>
                                <div class="item"><span class="label">Salary:</span> PKR {promo.current_salary:,} -> PKR {promo.new_salary:,}</div>
                            </div>
                            <div style="color:#a0aec0;font-size:12px;margin-top:6px;">{promo.reason[:100]}...</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Approve", key=f"emp_approve_{promo.id}"):
                            if update_emp_status(promo.id, "Approved"):
                                st.success("Approved!")
                                st.rerun()
                    with col2:
                        if st.button("Reject", key=f"emp_reject_{promo.id}"):
                            if update_emp_status(promo.id, "Rejected"):
                                st.warning("Rejected!")
                                st.rerun()
                    st.markdown("---")
            else:
                st.info("No pending Employee promotions.")
        
        with emp_tab3:
            if emp_promotions:
                data = []
                for promo in emp_promotions:
                    data.append({
                        "Employee": promo.employee.name,
                        "From": promo.current_designation,
                        "To": promo.new_designation,
                        "Salary": f"PKR {promo.current_salary:,} -> PKR {promo.new_salary:,}",
                        "Status": promo.status,
                        "Date": promo.created_at.strftime("%Y-%m-%d")
                    })
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No Employee promotion history.")
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    with col_admin:
        st.markdown("""
            <div style="
                background: rgba(102,126,234,0.05);
                border: 1px solid rgba(102,126,234,0.2);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
            ">
                <h3 style="color: #667eea; margin: 0;">HR Side <span class="admin-badge">HR System</span></h3>
                <p style="color: #a0aec0; font-size: 13px; margin: 5px 0 0 0;">Current HR employees only - Uses 'admin_promotions' table</p>
            </div>
        """, unsafe_allow_html=True)
        
        admin_total = len(admin_promotions)
        admin_pending_count = len(admin_pending)
        admin_approved = sum(1 for p in admin_promotions if p.status == "Approved")
        admin_rejected = sum(1 for p in admin_promotions if p.status == "Rejected")
        
        admin_col1, admin_col2, admin_col3, admin_col4 = st.columns(4)
        with admin_col1:
            st.metric("Total", admin_total)
        with admin_col2:
            st.metric("Pending", admin_pending_count)
        with admin_col3:
            st.metric("Approved", admin_approved)
        with admin_col4:
            st.metric("Rejected", admin_rejected)
        
        st.markdown("---")
        
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["Recommend", "Pending", "History"])
        
        with admin_tab1:
            with st.form("admin_promotion_form"):
                st.markdown("##### HR Promotion Request")
                
                if hr_employees:
                    emp_options = {f"{emp.name} - {emp.designation or 'N/A'}": emp.id for emp in hr_employees}
                    selected_emp = st.selectbox("Select Employee", list(emp_options.keys()), key="admin_emp")
                    emp_id = emp_options[selected_emp]
                    selected_emp_obj = next((e for e in hr_employees if e.id == emp_id), None)
                    
                    rec_by = st.selectbox("Recommended By", ["Admin", "HR Manager", "Department Head", "Team Lead", "CEO"], key="admin_rec")
                    
                    if selected_emp_obj:
                        st.text_input("Current Designation", value=selected_emp_obj.designation or "N/A", disabled=True, key="admin_curr_desig")
                        st.number_input("Current Salary (PKR)", value=selected_emp_obj.salary or 0, disabled=True, key="admin_curr_sal")
                        
                        with st.expander("View Education Details"):
                            education = selected_emp_obj.education
                            if education:
                                try:
                                    if isinstance(education, str):
                                        education = json.loads(education)
                                    if isinstance(education, dict):
                                        for key, value in education.items():
                                            if value and value != "Missing" and value != "N/A" and value != "":
                                                if isinstance(value, dict):
                                                    st.write(f"**{key}:**")
                                                    for sub_key, sub_value in value.items():
                                                        if sub_value and sub_value != "Missing" and sub_value != "N/A" and sub_value != "":
                                                            st.write(f"  - {sub_key}: {sub_value}")
                                                else:
                                                    st.write(f"**{key}:** {value}")
                                    else:
                                        st.write(str(education))
                                except:
                                    st.write(str(education))
                            else:
                                st.write("No education data available")
                    
                    st.markdown("---")
                    new_desig = st.text_input("New Designation *", placeholder="e.g., Senior Software Engineer", key="admin_new_desig")
                    new_sal = st.number_input("New Salary (PKR) *", min_value=0, value=50000, step=1000, key="admin_new_sal")
                    reason = st.text_area("Reason *", placeholder="Explain why...", height=60, key="admin_reason")
                    
                    if st.form_submit_button("Submit HR Promotion", use_container_width=True):
                        if new_desig and new_sal and reason and selected_emp_obj and new_sal > (selected_emp_obj.salary or 0):
                            save_admin_promotion(emp_id, selected_emp_obj.designation or "N/A", new_desig, selected_emp_obj.salary or 0, new_sal, reason, rec_by)
                            st.success(f"HR Promotion submitted for {selected_emp_obj.name}!")
                            st.rerun()
                        else:
                            st.error("Please fill all fields and ensure salary is higher!")
                else:
                    st.info("No HR employees found. Add HR from 'New HR Management' page and approve from 'Review Applications'.")
        
        with admin_tab2:
            if admin_pending:
                for promo in admin_pending:
                    emp = promo.employee
                    st.markdown(f"""
                        <div class="promotion-card">
                            <div class="header">
                                <div>
                                    <div class="emp-name">{emp.name}</div>
                                    <div class="emp-dept">{emp.department or 'N/A'} - {emp.designation or 'N/A'}</div>
                                </div>
                                <span class="status-pending">Pending</span>
                            </div>
                            <div class="details">
                                <div class="item"><span class="label">Current:</span> {promo.current_designation}</div>
                                <div class="item"><span class="label">New:</span> <span style="color:#667eea;">{promo.new_designation}</span></div>
                                <div class="item"><span class="label">Salary:</span> PKR {promo.current_salary:,} -> PKR {promo.new_salary:,}</div>
                            </div>
                            <div style="color:#a0aec0;font-size:12px;margin-top:6px;">{promo.reason[:100]}...</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Approve", key=f"admin_approve_{promo.id}"):
                            if update_admin_status(promo.id, "Approved"):
                                st.success("Approved!")
                                st.rerun()
                    with col2:
                        if st.button("Reject", key=f"admin_reject_{promo.id}"):
                            if update_admin_status(promo.id, "Rejected"):
                                st.warning("Rejected!")
                                st.rerun()
                    st.markdown("---")
            else:
                st.info("No pending HR promotions.")
        
        with admin_tab3:
            if admin_promotions:
                data = []
                for promo in admin_promotions:
                    data.append({
                        "Employee": promo.employee.name,
                        "From": promo.current_designation,
                        "To": promo.new_designation,
                        "Salary": f"PKR {promo.current_salary:,} -> PKR {promo.new_salary:,}",
                        "Status": promo.status,
                        "Date": promo.created_at.strftime("%Y-%m-%d")
                    })
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No HR promotion history.")
    
    db.close()

if __name__ == "__main__":
    show()