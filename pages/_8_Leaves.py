import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend.database import SessionLocal
from backend.models.employee import Employee
from backend.models.leave import Leave
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
            .form-group input, .form-group select, .form-group textarea {
                width: 100%;
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.05);
                color: #ffffff;
                font-size: 13px;
            }
            .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
            }
            .form-group select option {
                background: #1a1a2e;
                color: #ffffff;
            }
            .form-group textarea {
                resize: vertical;
                min-height: 60px;
            }
            
            .balance-box {
                background: rgba(102,126,234,0.08);
                border: 1px solid rgba(102,126,234,0.15);
                border-radius: 10px;
                padding: 12px 16px;
                margin: 8px 0;
            }
            .balance-box .emp-name {
                color: #ffffff;
                font-weight: 500;
            }
            .balance-box .emp-balance {
                color: #48bb78;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Leave Management</div>
        <div class="page-subtitle">Manage employee leave requests and balances</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    def get_active_employees():
        return db.query(Employee).filter(
            Employee.status == "Active",
            Employee.department != "HR"
        ).all()
    
    def get_all_leaves():
        return db.query(Leave).order_by(Leave.applied_on.desc()).all()
    
    def get_pending_leaves():
        return db.query(Leave).filter(Leave.status == "Pending").all()
    
    def get_leaves_by_employee(employee_id):
        return db.query(Leave).filter(Leave.employee_id == employee_id).all()
    
    def get_leave_balance(employee_id):
        approved_leaves = db.query(Leave).filter(
            Leave.employee_id == employee_id,
            Leave.status == "Approved"
        ).all()
        total_taken = sum(l.days for l in approved_leaves)
        annual_quota = 20
        remaining = annual_quota - total_taken
        return {
            "annual_quota": annual_quota,
            "taken": total_taken,
            "remaining": remaining if remaining > 0 else 0
        }
    
    def save_leave(employee_id, leave_type, start_date, end_date, days, reason):
        leave = Leave(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=reason,
            status="Pending"
        )
        db.add(leave)
        db.commit()
        db.refresh(leave)
        return leave
    
    def update_leave_status(leave_id, status):
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if leave:
            leave.status = status
            emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
            if status == "Approved":
                leave.approved_on = datetime.now()
                add_audit_log(
                    get_current_user(),
                    "Approve Leave",
                    f"Approved {leave.leave_type} leave for {emp.name if emp else 'N/A'} ({leave.days} days)"
                )
            else:
                add_audit_log(
                    get_current_user(),
                    "Reject Leave",
                    f"Rejected {leave.leave_type} leave for {emp.name if emp else 'N/A'}"
                )
            db.commit()
            db.refresh(leave)
            return True
        return False
    
    def delete_leave(leave_id):
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if leave:
            db.delete(leave)
            db.commit()
            return True
        return False
    
    if 'leave_notifications' not in st.session_state:
        st.session_state.leave_notifications = []
    
    active_employees = get_active_employees()
    employee_names = [emp.name for emp in active_employees] if active_employees else []
    employee_options = {emp.name: emp.id for emp in active_employees} if active_employees else {}
    
    tab1, tab2, tab3, tab4 = st.tabs(["Apply Leave", "Pending Requests", "Leave History", "Leave Analytics"])
    
    with tab1:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Apply Leave
                    <span class="badge">New Request</span>
                </div>
        """, unsafe_allow_html=True)
        
        if active_employees:
            with st.expander("View Leave Balance", expanded=False):
                for emp in active_employees:
                    balance = get_leave_balance(emp.id)
                    st.markdown(f"""
                        <div class="balance-box">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div>
                                    <span class="emp-name">{emp.name}</span>
                                    <span style="color:#a0aec0;font-size:12px;"> {emp.department or 'N/A'}</span>
                                </div>
                                <div>
                                    <span class="emp-balance">{balance['remaining']}</span>
                                    <span style="color:#a0aec0;font-size:12px;">/ {balance['annual_quota']} days left</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            with st.form("apply_leave_form"):
                col1, col2 = st.columns(2)
                with col1:
                    employee = st.selectbox("Select Employee", employee_names)
                    emp_id = employee_options.get(employee) if employee else None
                
                with col2:
                    leave_type = st.selectbox("Leave Type", ["Annual", "Sick", "Casual", "Unpaid", "Other"])
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", datetime.now())
                with col2:
                    end_date = st.date_input("End Date", datetime.now() + timedelta(days=1))
                
                if start_date and end_date:
                    days = (end_date - start_date).days + 1
                    if days < 1:
                        days = 1
                    st.info(f"Total Days: {days} day{'s' if days > 1 else ''}")
                
                reason = st.text_area("Reason for Leave", placeholder="Please provide a reason for your leave request...", height=80)
                
                if emp_id:
                    balance = get_leave_balance(emp_id)
                    st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px;border:1px solid rgba(255,255,255,0.06);">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="color:#a0aec0;">Leave Balance for {employee}:</span>
                                <span style="color:#48bb78;font-weight:600;">{balance['remaining']} days remaining</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                if st.form_submit_button("Submit Leave Request", use_container_width=True):
                    if start_date and end_date and reason:
                        if start_date <= end_date:
                            if leave_type == "Annual":
                                balance = get_leave_balance(emp_id)
                                if days > balance['remaining']:
                                    st.error(f"Insufficient leave balance! You have {balance['remaining']} days remaining.")
                                else:
                                    save_leave(emp_id, leave_type, start_date, end_date, days, reason)
                                    st.success(f"Leave request submitted for {employee}!")
                                    st.rerun()
                            else:
                                save_leave(emp_id, leave_type, start_date, end_date, days, reason)
                                st.success(f"Leave request submitted for {employee}!")
                                st.rerun()
                        else:
                            st.error("End date must be after start date!")
                    else:
                        st.error("Please fill all required fields!")
        else:
            st.info("No active employees found. Add employees first.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        pending_leaves = db.query(Leave).filter(Leave.status == "Pending").all()
        
        filtered_pending = []
        for leave in pending_leaves:
            emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
            if emp and emp.department != "HR":
                filtered_pending.append(leave)
        
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    Pending Requests
                    <span class="badge">{len(filtered_pending)} Pending</span>
                </div>
        """, unsafe_allow_html=True)
        
        if filtered_pending:
            data = []
            for leave in filtered_pending:
                emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
                data.append({
                    "ID": leave.id,
                    "Employee": emp.name if emp else "Unknown",
                    "Department": emp.department if emp else "N/A",
                    "Type": leave.leave_type,
                    "Start Date": leave.start_date.strftime("%Y-%m-%d"),
                    "End Date": leave.end_date.strftime("%Y-%m-%d"),
                    "Days": leave.days,
                    "Reason": leave.reason or "-",
                    "Applied": leave.applied_on.strftime("%Y-%m-%d %H:%M")
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            st.markdown("#### Approve or Reject Leave Request")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                pending_options = {f"{d['Employee']} - {d['Type']} ({d['Start Date']} to {d['End Date']})": d['ID'] for d in data}
                selected_leave = st.selectbox("Select Leave Request", list(pending_options.keys()))
                leave_id = pending_options[selected_leave]
            
            with col2:
                if st.button("Approve", use_container_width=True):
                    if update_leave_status(leave_id, "Approved"):
                        st.success("Leave request approved!")
                        st.rerun()
                    else:
                        st.error("Failed to approve!")
            
            with col3:
                if st.button("Reject", use_container_width=True):
                    if update_leave_status(leave_id, "Rejected"):
                        st.success("Leave request rejected!")
                        st.rerun()
                    else:
                        st.error("Failed to reject!")
        else:
            st.info("No pending leave requests.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Leave History
                    <span class="badge">All Records</span>
                </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Approved", "Rejected"])
        with col2:
            emp_filter_options = ["All"] + employee_names
            emp_filter = st.selectbox("Filter by Employee", emp_filter_options)
        with col3:
            leave_type_filter = st.selectbox("Leave Type", ["All", "Annual", "Sick", "Casual", "Unpaid", "Other"])
        
        all_leaves = get_all_leaves()
        
        filtered = []
        for leave in all_leaves:
            emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
            if emp and emp.department != "HR":
                filtered.append(leave)
        
        if status_filter != "All":
            filtered = [l for l in filtered if l.status == status_filter]
        if emp_filter != "All":
            filtered = [l for l in filtered if db.query(Employee).filter(Employee.id == l.employee_id).first().name == emp_filter]
        if leave_type_filter != "All":
            filtered = [l for l in filtered if l.leave_type == leave_type_filter]
        
        if filtered:
            data = []
            for leave in filtered:
                emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
                data.append({
                    "Employee": emp.name if emp else "Unknown",
                    "Department": emp.department if emp else "N/A",
                    "Type": leave.leave_type,
                    "Start Date": leave.start_date.strftime("%Y-%m-%d"),
                    "End Date": leave.end_date.strftime("%Y-%m-%d"),
                    "Days": leave.days,
                    "Reason": leave.reason or "-",
                    "Status": leave.status,
                    "Applied": leave.applied_on.strftime("%Y-%m-%d %H:%M"),
                    "ID": leave.id
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            total = len(filtered)
            pending = sum(1 for l in filtered if l.status == "Pending")
            approved = sum(1 for l in filtered if l.status == "Approved")
            rejected = sum(1 for l in filtered if l.status == "Rejected")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", total)
            with col2:
                st.metric("Pending", pending)
            with col3:
                st.metric("Approved", approved)
            with col4:
                st.metric("Rejected", rejected)
            
            st.markdown("---")
            
            st.markdown("#### Delete Leave Record")
            col1, col2 = st.columns([4, 1])
            with col1:
                del_options = {f"{d['Employee']} - {d['Type']} ({d['Start Date']})": d['ID'] for d in data}
                del_selected = st.selectbox("Select Record to Delete", list(del_options.keys()), key="del_leave")
                del_id = del_options[del_selected]
            
            with col2:
                if st.button("Delete", use_container_width=True):
                    if delete_leave(del_id):
                        st.success("Leave record deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete!")
        else:
            st.info("No leave records found.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Leave Analytics
                    <span class="badge">Insights</span>
                </div>
        """, unsafe_allow_html=True)
        
        if active_employees:
            high_employees = []
            medium_employees = []
            low_employees = []
            
            for emp in active_employees:
                balance = get_leave_balance(emp.id)
                used = balance['taken']
                limit = balance['annual_quota']
                remaining = balance['remaining']
                
                if used >= 15:
                    high_employees.append({"name": emp.name, "used": used, "limit": limit, "remaining": remaining})
                elif used >= 8:
                    medium_employees.append({"name": emp.name, "used": used, "limit": limit, "remaining": remaining})
                else:
                    low_employees.append({"name": emp.name, "used": used, "limit": limit, "remaining": remaining})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div style="background:rgba(252,129,129,0.15);border:2px solid rgba(252,129,129,0.3);border-radius:16px;padding:20px;text-align:center;height:100%;">
                        <div style="color:#fc8181;font-size:18px;font-weight:700;margin-bottom:15px;">Most Leaves</div>
                        <div style="font-size:36px;font-weight:800;color:#fc8181;">{len(high_employees)}</div>
                        <div style="text-align:left;margin-top:10px;">
                """, unsafe_allow_html=True)
                
                if high_employees:
                    for emp in high_employees:
                        st.markdown(f"""
                            <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:13px;">
                                <span style="color:#cbd5e0;">{emp['name']}</span>
                                <span style="color:#fc8181;font-weight:600;">{emp['used']}/{emp['limit']}</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="color:#4a5568;text-align:center;padding:10px 0;">No employees</div>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div style="background:rgba(237,137,54,0.15);border:2px solid rgba(237,137,54,0.3);border-radius:16px;padding:20px;text-align:center;height:100%;">
                        <div style="color:#ed8936;font-size:18px;font-weight:700;margin-bottom:15px;">Medium</div>
                        <div style="font-size:36px;font-weight:800;color:#ed8936;">{len(medium_employees)}</div>
                        <div style="text-align:left;margin-top:10px;">
                """, unsafe_allow_html=True)
                
                if medium_employees:
                    for emp in medium_employees:
                        st.markdown(f"""
                            <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:13px;">
                                <span style="color:#cbd5e0;">{emp['name']}</span>
                                <span style="color:#ed8936;font-weight:600;">{emp['used']}/{emp['limit']}</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="color:#4a5568;text-align:center;padding:10px 0;">No employees</div>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div style="background:rgba(72,187,120,0.15);border:2px solid rgba(72,187,120,0.3);border-radius:16px;padding:20px;text-align:center;height:100%;">
                        <div style="color:#48bb78;font-size:18px;font-weight:700;margin-bottom:15px;">Least Leaves</div>
                        <div style="font-size:36px;font-weight:800;color:#48bb78;">{len(low_employees)}</div>
                        <div style="text-align:left;margin-top:10px;">
                """, unsafe_allow_html=True)
                
                if low_employees:
                    for emp in low_employees:
                        st.markdown(f"""
                            <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:13px;">
                                <span style="color:#cbd5e0;">{emp['name']}</span>
                                <span style="color:#48bb78;font-weight:600;">{emp['used']}/{emp['limit']}</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="color:#4a5568;text-align:center;padding:10px 0;">No employees</div>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            total_employees = len(active_employees)
            total_used = sum(get_leave_balance(emp.id)['taken'] for emp in active_employees)
            total_limit = sum(get_leave_balance(emp.id)['annual_quota'] for emp in active_employees)
            total_remaining = total_limit - total_used
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:15px;text-align:center;border:1px solid rgba(255,255,255,0.06);">
                        <div style="font-size:28px;font-weight:700;color:#ffffff;">{total_employees}</div>
                        <div style="color:#a0aec0;font-size:12px;">Total</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:15px;text-align:center;border:1px solid rgba(255,255,255,0.06);">
                        <div style="font-size:28px;font-weight:700;color:#ffffff;">{total_used}</div>
                        <div style="color:#a0aec0;font-size:12px;">Used</div>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:15px;text-align:center;border:1px solid rgba(255,255,255,0.06);">
                        <div style="font-size:28px;font-weight:700;color:#ffffff;">{total_remaining}</div>
                        <div style="color:#a0aec0;font-size:12px;">Remaining</div>
                    </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:15px;text-align:center;border:1px solid rgba(255,255,255,0.06);">
                        <div style="font-size:28px;font-weight:700;color:#fc8181;">{len(high_employees)}</div>
                        <div style="color:#a0aec0;font-size:12px;">Most</div>
                    </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:15px;text-align:center;border:1px solid rgba(255,255,255,0.06);">
                        <div style="font-size:28px;font-weight:700;color:#48bb78;">{len(low_employees)}</div>
                        <div style="color:#a0aec0;font-size:12px;">Least</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No leave data available. Add employees first.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    db.close()