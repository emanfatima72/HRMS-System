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
            .status-paid { background: rgba(72,187,120,0.2); color: #48bb78; }
            .status-pending { background: rgba(237,137,54,0.2); color: #ed8936; }
            .status-processing { background: rgba(102,126,234,0.2); color: #667eea; }
            
            .payslip-box {
                background: white;
                border: 2px solid #1a1a2e;
                border-radius: 12px;
                padding: 30px;
                margin: 10px 0;
                max-width: 700px;
                margin-left: auto;
                margin-right: auto;
                color: #1a1a2e !important;
            }
            .payslip-box * { color: #1a1a2e !important; }
            .payslip-box .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #667eea;
                padding-bottom: 15px;
                margin-bottom: 15px;
            }
            .payslip-box .title { 
                color: #1a1a2e !important; 
                font-size: 24px; 
                font-weight: 800; 
                letter-spacing: 2px;
            }
            .payslip-box .company {
                color: #667eea !important;
                font-size: 14px;
                font-weight: 600;
            }
            .payslip-box .row { 
                display: flex; 
                justify-content: space-between; 
                padding: 8px 0; 
                border-bottom: 1px solid #e2e8f0;
            }
            .payslip-box .row:last-child { border-bottom: none; }
            .payslip-box .label { color: #4a5568 !important; font-size: 14px; }
            .payslip-box .value { color: #1a1a2e !important; font-weight: 600; font-size: 14px; }
            .payslip-box .total-row {
                background: #f7fafc;
                padding: 12px 15px;
                border-radius: 8px;
                margin-top: 10px;
            }
            .payslip-box .total-row .label { font-size: 16px; font-weight: 700; color: #1a1a2e !important; }
            .payslip-box .total-row .value { font-size: 18px; font-weight: 800; color: #48bb78 !important; }
            .payslip-box .footer {
                text-align: center;
                color: #a0aec0 !important;
                font-size: 11px;
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid #e2e8f0;
            }
            .payslip-box .section-title {
                color: #1a1a2e !important;
                font-size: 14px;
                font-weight: 700;
                margin: 10px 0;
                padding-bottom: 5px;
                border-bottom: 2px solid #667eea;
            }
            .payslip-box .info-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-bottom: 15px;
            }
            .payslip-box .info-grid .info-item {
                padding: 5px 0;
            }
            .payslip-box .info-grid .info-label {
                color: #4a5568 !important;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .payslip-box .info-grid .info-value {
                color: #1a1a2e !important;
                font-size: 16px;
                font-weight: 700;
            }
            .payslip-box .info-grid .info-value-sm {
                color: #1a1a2e !important;
                font-size: 14px;
            }
            .payslip-status {
                display: inline-block;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
            }
            .payslip-status.paid { background: rgba(72,187,120,0.2); color: #48bb78 !important; }
            .payslip-status.pending { background: rgba(237,137,54,0.2); color: #ed8936 !important; }
            .payslip-status.processing { background: rgba(102,126,234,0.2); color: #667eea !important; }
            
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
        <div class="page-title">HR Salary Management</div>
        <div class="page-subtitle">Manage HR staff salaries, bonuses, and deductions</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    if 'selected_payslip_id' not in st.session_state:
        st.session_state.selected_payslip_id = None
    
    def get_hr_employees():
        return db.query(Employee).filter(
            Employee.department == "HR",
            Employee.status == "Active"
        ).all()
    
    def get_all_payroll_records():
        return db.query(Payroll).join(Employee, Payroll.employee_id == Employee.id).filter(
            Employee.department == "HR"
        ).order_by(Payroll.created_at.desc()).all()
    
    def create_payroll_record(employee_id, basic_salary, bonus, deductions, net_salary, month, status):
        payroll = Payroll(
            employee_id=employee_id,
            basic_salary=basic_salary,
            bonus=bonus,
            deductions=deductions,
            net_salary=net_salary,
            month=month,
            status=status,
            created_at=datetime.now()
        )
        db.add(payroll)
        db.commit()
        db.refresh(payroll)
        
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        add_audit_log(
            get_current_user(),
            "Add Salary Record",
            f"Added salary record for {emp.name if emp else 'N/A'}: {month} - PKR {net_salary:,.0f}"
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
    
    def delete_payroll_record(payroll_id):
        payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
        if payroll:
            db.delete(payroll)
            db.commit()
            return True
        return False
    
    def get_payroll_by_id(payroll_id):
        return db.query(Payroll).filter(Payroll.id == payroll_id).first()
    
    hr_employees = get_hr_employees()
    payroll_records = get_all_payroll_records()
    
    total_payroll = sum(p.net_salary for p in payroll_records) if payroll_records else 0
    total_hr = len(hr_employees)
    paid_count = sum(1 for p in payroll_records if p.status == "Paid") if payroll_records else 0
    pending_count = len(payroll_records) - paid_count if payroll_records else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-box"><div class="number">{total_hr}</div><div class="label">Total HR</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-box"><div class="number">PKR {total_payroll:,.0f}</div><div class="label">Total Payroll</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-box"><div class="number" style="color:#48bb78;">{paid_count}</div><div class="label">Paid</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-box"><div class="number" style="color:#ed8936;">{pending_count}</div><div class="label">Pending</div></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Salary Records", "Add Salary", "Payslip"])
    
    with tab1:
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    Salary Records
                    <span class="badge">{len(payroll_records)} Records</span>
                </div>
        """, unsafe_allow_html=True)
        
        if payroll_records:
            data = []
            for p in payroll_records:
                emp = db.query(Employee).filter(Employee.id == p.employee_id).first()
                data.append({
                    "ID": p.id,
                    "Employee": emp.name if emp else "N/A",
                    "Basic Salary": f"PKR {p.basic_salary:,.0f}",
                    "Bonus": f"PKR {p.bonus:,.0f}",
                    "Deductions": f"PKR {p.deductions:,.0f}",
                    "Net Salary": f"PKR {p.net_salary:,.0f}",
                    "Month": p.month,
                    "Status": p.status,
                    "Date": p.created_at.strftime("%Y-%m-%d") if p.created_at else "N/A"
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("### Actions")
            st.caption("Update status or delete records")
            
            for idx, p in enumerate(payroll_records):
                emp = db.query(Employee).filter(Employee.id == p.employee_id).first()
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{emp.name if emp else 'N/A'}** - {p.month} - PKR {p.net_salary:,.0f}")
                with col2:
                    if p.status != "Paid":
                        if st.button("Mark Paid", key=f"pay_{p.id}"):
                            if update_payroll_status(p.id, "Paid"):
                                st.success("Status updated to Paid!")
                                st.rerun()
                with col3:
                    if st.button("Delete", key=f"del_{p.id}"):
                        if delete_payroll_record(p.id):
                            st.success("Record deleted!")
                            st.rerun()
                st.markdown("---")
        else:
            st.info("No salary records found. Add salary from 'Add Salary' tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Add Salary Record
                    <span class="badge">New Entry</span>
                </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_salary_form"):
            col1, col2 = st.columns(2)
            with col1:
                if hr_employees:
                    emp_options = {f"{emp.name} - {emp.designation or 'N/A'} (PKR {emp.salary or 0:,.0f})": emp.id for emp in hr_employees}
                    selected_emp = st.selectbox("Select HR Employee *", list(emp_options.keys()))
                    emp_id = emp_options[selected_emp]
                    selected_emp_obj = next((e for e in hr_employees if e.id == emp_id), None)
                    
                    if selected_emp_obj:
                        st.text_input("Designation", value=selected_emp_obj.designation or "N/A", disabled=True)
                        current_salary = selected_emp_obj.salary or 0
                        st.number_input("Basic Salary (PKR) *", value=current_salary, disabled=True, key="basic_salary_display")
                else:
                    st.warning("No HR employees found. Please add HR first.")
                    emp_id = None
                    selected_emp_obj = None
            
            with col2:
                month = st.selectbox("Month *", ["January", "February", "March", "April", "May", "June", 
                                               "July", "August", "September", "October", "November", "December"])
                year = st.selectbox("Year *", [2024, 2025, 2026, 2027, 2028], index=2)
                month_year = f"{month} {year}"
            
            basic_salary = 0
            if selected_emp_obj:
                basic_salary = selected_emp_obj.salary or 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                bonus = st.number_input("Bonus", min_value=0, value=0, step=1000)
            with col2:
                deductions = st.number_input("Deductions", min_value=0, value=0, step=1000)
            with col3:
                status = st.selectbox("Status", ["Pending", "Processing", "Paid"])
            
            net_salary = basic_salary + bonus - deductions
            
            st.info(f"Net Salary: PKR {net_salary:,.0f}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Salary", use_container_width=True):
                    if emp_id and basic_salary > 0:
                        create_payroll_record(emp_id, basic_salary, bonus, deductions, net_salary, month_year, status)
                        st.success(f"Salary record added for {selected_emp_obj.name if selected_emp_obj else 'HR'}!")
                        st.rerun()
                    else:
                        st.error("Please select an employee with valid salary!")
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Generate Payslip
                    <span class="badge">Download</span>
                </div>
        """, unsafe_allow_html=True)
        
        if payroll_records:
            payslip_options = {}
            for p in payroll_records:
                emp = db.query(Employee).filter(Employee.id == p.employee_id).first()
                payslip_options[f"{emp.name if emp else 'N/A'} - {p.month} (PKR {p.net_salary:,.0f})"] = p.id
            
            selected_payslip = st.selectbox("Select Record for Payslip", list(payslip_options.keys()))
            payslip_id = payslip_options[selected_payslip]
            
            if st.button("Generate Payslip", use_container_width=True):
                payroll = db.query(Payroll).filter(Payroll.id == payslip_id).first()
                if payroll:
                    emp = db.query(Employee).filter(Employee.id == payroll.employee_id).first()
                    
                    st.markdown(f"""
                        <div style="background:rgba(72,187,120,0.1);border:1px solid rgba(72,187,120,0.3);border-radius:12px;padding:20px;text-align:center;margin:20px 0;">
                            <div style="font-size:48px;display:block;margin-bottom:10px;">✅</div>
                            <div style="color:#48bb78;font-size:20px;font-weight:700;">Payslip Generated Successfully!</div>
                            <div style="color:#a0aec0;font-size:14px;margin-top:5px;">Payslip for {emp.name if emp else 'N/A'} - {payroll.month} is ready to download</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    payslip_text = f"""
============================================================
                        PAYSLIP
                    HRMS Enterprise Suite
============================================================
Date: {datetime.now().strftime('%d %B, %Y')}
Month: {payroll.month}
------------------------------------------------------------
Employee Details
------------------------------------------------------------
Name        : {emp.name if emp else 'N/A'}
Designation : {emp.designation if emp else 'N/A'}
Department  : {emp.department if emp else 'N/A'}
Email       : {emp.email if emp else 'N/A'}
------------------------------------------------------------
Salary Details
------------------------------------------------------------
Basic Salary   : PKR {payroll.basic_salary:,.0f}
Bonus          : PKR {payroll.bonus:,.0f}
Deductions     : PKR {payroll.deductions:,.0f}
------------------------------------------------------------
NET SALARY     : PKR {payroll.net_salary:,.0f}
------------------------------------------------------------
Status         : {payroll.status}
Generated On   : {datetime.now().strftime('%d %B, %Y %I:%M %p')}
============================================================
This is a system-generated payslip. For queries, contact HR department.
============================================================
"""
                    
                    st.download_button(
                        label="Download Payslip",
                        data=payslip_text,
                        file_name=f"payslip_{emp.name if emp else 'employee'}_{payroll.month.replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    st.info("Click the download button above to save the payslip.")
        else:
            st.info("No payroll records found to generate payslip.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    db.close()

if __name__ == "__main__":
    show()