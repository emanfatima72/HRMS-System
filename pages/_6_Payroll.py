import streamlit as st
import pandas as pd
from datetime import datetime
from backend.database import SessionLocal
from backend.models.employee import Employee
from backend.models.payroll import Payroll
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
            
            .status-paid {
                background: rgba(72,187,120,0.2);
                color: #48bb78;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                display: inline-block;
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
            
            .form-group {
                margin-bottom: 12px;
            }
            .form-group label {
                color: #a0aec0;
                font-size: 13px;
                display: block;
                margin-bottom: 4px;
                font-weight: 500;
            }
            .form-group input, .form-group select {
                width: 100%;
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.05);
                color: #ffffff;
                font-size: 13px;
            }
            .form-group input:focus, .form-group select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
            }
            .form-group select option {
                background: #1a1a2e;
                color: #ffffff;
            }
            
            .emp-detail-box {
                background: rgba(255,255,255,0.04);
                border-radius: 8px;
                padding: 12px;
                border: 1px solid rgba(255,255,255,0.06);
            }
            .emp-detail-box .label {
                color: #a0aec0;
                font-size: 12px;
            }
            .emp-detail-box .name {
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
            }
            .emp-detail-box .dept {
                color: #a0aec0;
                font-size: 13px;
            }
            .emp-detail-box .salary {
                color: #48bb78;
                font-size: 14px;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Payroll Management</div>
        <div class="page-subtitle">Manage employee salaries, bonuses, and deductions</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    def get_active_employees():
        return db.query(Employee).filter(
            Employee.status == "Active",
            Employee.department != "HR"
        ).all()
    
    def get_payroll_by_month(month):
        return db.query(Payroll).filter(Payroll.month == month).all()
    
    def save_payroll(employee_id, month, basic_salary, bonus, deductions, net_salary):
        payroll = Payroll(
            employee_id=employee_id,
            month=month,
            basic_salary=basic_salary,
            bonus=bonus,
            deductions=deductions,
            net_salary=net_salary,
            status="Pending"
        )
        db.add(payroll)
        db.commit()
        db.refresh(payroll)
        
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        add_audit_log(
            get_current_user(),
            "Generate Payroll",
            f"Generated payroll for {emp.name if emp else 'N/A'}: {month} - PKR {net_salary:,.0f}"
        )
        return payroll
    
    def update_payroll_status(payroll_id, status):
        payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
        if payroll:
            payroll.status = status
            db.commit()
            db.refresh(payroll)
            return True
        return False
    
    def delete_payroll(payroll_id):
        payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
        if payroll:
            db.delete(payroll)
            db.commit()
            return True
        return False
    
    active_employees = get_active_employees()
    current_month = datetime.now().strftime("%Y-%m")
    existing_payroll = get_payroll_by_month(current_month)
    existing_employee_ids = [p.employee_id for p in existing_payroll]
    
    total_employees = len(active_employees)
    total_payroll = sum(p.net_salary for p in existing_payroll) if existing_payroll else 0
    paid_count = sum(1 for p in existing_payroll if p.status == "Paid")
    pending_count = sum(1 for p in existing_payroll if p.status == "Pending")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_employees}</div>
                <div class="metric-label">Total Employees</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">PKR {total_payroll:,.0f}</div>
                <div class="metric-label">Total Payroll</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{paid_count}</div>
                <div class="metric-label">Paid</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{pending_count}</div>
                <div class="metric-label">Pending</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Generate Payroll", "Payroll History"])
    
    with tab1:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Generate Payroll
                    <span class="badge">New</span>
                </div>
        """, unsafe_allow_html=True)
        
        if active_employees:
            st.info(f"Generating payroll for {len(active_employees)} active employees for {current_month}")
            
            employee_data = []
            for emp in active_employees:
                existing = db.query(Payroll).filter(
                    Payroll.employee_id == emp.id,
                    Payroll.month == current_month
                ).first()
                
                try:
                    salary_val = int(emp.salary) if emp.salary else 0
                except (ValueError, TypeError):
                    salary_val = 0
                
                if existing:
                    status = "Paid" if existing.status == "Paid" else "Pending"
                    employee_data.append({
                        "ID": emp.id,
                        "Name": emp.name,
                        "Email": emp.email,
                        "Department": emp.department or "N/A",
                        "Salary": salary_val,
                        "Status": status,
                        "Payroll ID": existing.id
                    })
                else:
                    employee_data.append({
                        "ID": emp.id,
                        "Name": emp.name,
                        "Email": emp.email,
                        "Department": emp.department or "N/A",
                        "Salary": salary_val,
                        "Status": "Not Generated",
                        "Payroll ID": None
                    })
            
            df = pd.DataFrame(employee_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            with st.form("generate_payroll_form"):
                st.markdown("#### Generate Payroll for Selected Employee")
                
                col1, col2 = st.columns(2)
                with col1:
                    available_emps = [emp for emp in active_employees if emp.id not in existing_employee_ids]
                    if available_emps:
                        emp_options = {f"{emp.name} - {emp.department or 'N/A'}": emp.id for emp in available_emps}
                        selected_emp = st.selectbox("Select Employee", list(emp_options.keys()))
                        emp_id = emp_options[selected_emp]
                        selected_emp_obj = next((e for e in available_emps if e.id == emp_id), None)
                    else:
                        st.warning("All employees already have payroll for this month!")
                        selected_emp_obj = None
                
                if selected_emp_obj:
                    try:
                        salary_val = int(selected_emp_obj.salary) if selected_emp_obj.salary else 0
                    except (ValueError, TypeError):
                        salary_val = 0
                    
                    with col2:
                        st.markdown(f"""
                            <div class="emp-detail-box">
                                <div class="label">Employee Details</div>
                                <div class="name">{selected_emp_obj.name}</div>
                                <div class="dept">{selected_emp_obj.department or 'N/A'} - {selected_emp_obj.employee_type or 'N/A'}</div>
                                <div class="salary">PKR {salary_val:,.0f}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        basic_salary = st.number_input("Basic Salary", min_value=0, value=salary_val, step=1000)
                    with col2:
                        bonus = st.number_input("Bonus", min_value=0, value=0, step=500)
                    with col3:
                        deductions = st.number_input("Deductions", min_value=0, value=0, step=500)
                    
                    net_salary = basic_salary + bonus - deductions
                    st.info(f"Net Salary: PKR {net_salary:,.0f}")
                    
                    if st.form_submit_button("Generate Payroll", use_container_width=True):
                        if net_salary >= 0:
                            save_payroll(
                                employee_id=emp_id,
                                month=current_month,
                                basic_salary=basic_salary,
                                bonus=bonus,
                                deductions=deductions,
                                net_salary=net_salary
                            )
                            st.success(f"Payroll generated for {selected_emp_obj.name}!")
                            st.rerun()
                        else:
                            st.error("Net salary cannot be negative!")
        else:
            st.info("No active employees found. Add employees first.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Payroll History
                    <span class="badge">All Records</span>
                </div>
        """, unsafe_allow_html=True)
        
        all_payroll = db.query(Payroll).order_by(Payroll.month.desc()).all()
        
        if all_payroll:
            payroll_data = []
            for p in all_payroll:
                emp = db.query(Employee).filter(Employee.id == p.employee_id).first()
                if emp and emp.department != "HR":
                    payroll_data.append({
                        "Month": p.month,
                        "Employee": emp.name if emp else "Unknown",
                        "Department": emp.department if emp else "N/A",
                        "Basic Salary": p.basic_salary,
                        "Bonus": p.bonus,
                        "Deductions": p.deductions,
                        "Net Salary": p.net_salary,
                        "Status": p.status,
                        "ID": p.id
                    })
            
            if payroll_data:
                df = pd.DataFrame(payroll_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                st.markdown("#### Update Payroll Status")
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    payroll_options = {f"{p['Employee']} - {p['Month']} (PKR {p['Net Salary']:,.0f})": p['ID'] for p in payroll_data}
                    selected_payroll = st.selectbox("Select Payroll Record", list(payroll_options.keys()))
                    payroll_id = payroll_options[selected_payroll]
                
                with col2:
                    new_status = st.selectbox("Status", ["Pending", "Paid"])
                
                with col3:
                    if st.button("Update Status", use_container_width=True):
                        if update_payroll_status(payroll_id, new_status):
                            st.success(f"Status updated to {new_status}!")
                            st.rerun()
                        else:
                            st.error("Failed to update status!")
                
                st.markdown("---")
                
                st.markdown("#### Delete Payroll Record")
                col1, col2 = st.columns([4, 1])
                with col1:
                    del_options = {f"{p['Employee']} - {p['Month']}": p['ID'] for p in payroll_data}
                    del_selected = st.selectbox("Select Payroll to Delete", list(del_options.keys()), key="del_payroll")
                    del_id = del_options[del_selected]
                
                with col2:
                    if st.button("Delete", use_container_width=True):
                        if delete_payroll(del_id):
                            st.success("Payroll record deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete!")
            else:
                st.info("No payroll records found for employees.")
        else:
            st.info("No payroll records found. Generate payroll from the Generate Payroll tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    db.close()