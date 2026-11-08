import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
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
            .metric-value {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
            }
            .metric-label {
                color: #a0aec0;
                font-size: 13px;
            }
            
            .status-present {
                background: rgba(72,187,120,0.2);
                color: #48bb78;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                display: inline-block;
            }
            .status-absent {
                background: rgba(252,129,129,0.2);
                color: #fc8181;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                display: inline-block;
            }
            .status-leave {
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
            
            .upload-box {
                border: 2px dashed rgba(255,255,255,0.15);
                border-radius: 12px;
                padding: 25px;
                text-align: center;
                color: #a0aec0;
                transition: all 0.3s ease;
                margin: 10px 0;
            }
            .upload-box:hover {
                border-color: rgba(102, 126, 234, 0.4);
                background: rgba(255,255,255,0.02);
            }
            .upload-box .icon {
                font-size: 40px;
                display: block;
                margin-bottom: 10px;
            }
            
            .date-badge {
                background: rgba(102,126,234,0.2);
                color: #9f7aea;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                display: inline-block;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Attendance Management</div>
        <div class="page-subtitle">Track daily attendance, leaves, and working hours</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    def get_active_employees():
        """Get active employees excluding HR department"""
        return db.query(Employee).filter(
            Employee.status == "Active",
            Employee.department != "HR"
        ).all()
    
    def get_attendance_by_date(attendance_date):
        return db.query(Attendance).filter(Attendance.date == attendance_date).all()
    
    def get_attendance_by_date_and_employee(attendance_date, employee_id):
        return db.query(Attendance).filter(
            Attendance.date == attendance_date,
            Attendance.employee_id == employee_id
        ).first()
    
    def save_attendance(employee_id, date, status, check_in=None, check_out=None, hours_worked=None):
        existing = db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.date == date
        ).first()
        
        # Get employee name for audit log
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if existing:
            existing.status = status
            existing.check_in = check_in
            existing.check_out = check_out
            existing.hours_worked = hours_worked
            db.commit()
            db.refresh(existing)
            
            # 🔥 ADD AUDIT LOG - Update Attendance
            add_audit_log(
                get_current_user(),
                "Update Attendance",
                f"Updated attendance for {emp.name if emp else 'N/A'} - {status} on {date}"
            )
            return existing
        else:
            attendance = Attendance(
                employee_id=employee_id,
                date=date,
                status=status,
                check_in=check_in,
                check_out=check_out,
                hours_worked=hours_worked
            )
            db.add(attendance)
            db.commit()
            db.refresh(attendance)
            
            # 🔥 ADD AUDIT LOG - Mark Attendance
            add_audit_log(
                get_current_user(),
                "Mark Attendance",
                f"Marked {status} for {emp.name if emp else 'N/A'} on {date}"
            )
            return attendance
    
    def delete_attendance(attendance_id):
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if attendance:
            db.delete(attendance)
            db.commit()
            return True
        return False
    
    def get_attendance_with_employees():
        """Get attendance with employees excluding HR"""
        results = db.query(Attendance, Employee).join(Employee, Attendance.employee_id == Employee.id).filter(
            Employee.department != "HR"
        ).all()
        return results
    
    tab1, tab2, tab3 = st.tabs(["Mark Attendance", "Upload Excel", "Attendance Records"])
    
    with tab1:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Mark Attendance
                    <span class="badge">Manual Entry</span>
                </div>
        """, unsafe_allow_html=True)
        
        active_employees = get_active_employees()
        
        if active_employees:
            with st.form("mark_attendance_form"):
                col1, col2 = st.columns(2)
                with col1:
                    emp_options = {f"{emp.name} - {emp.department or 'N/A'}": emp.id for emp in active_employees}
                    selected_emp = st.selectbox("Select Employee", list(emp_options.keys()))
                    emp_id = emp_options[selected_emp]
                
                with col2:
                    attendance_date = st.date_input("Date", datetime.now())
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    status = st.selectbox("Status", ["Present", "Absent", "Leave"])
                with col2:
                    check_in = st.text_input("Check In (HH:MM)", placeholder="09:00")
                with col3:
                    check_out = st.text_input("Check Out (HH:MM)", placeholder="18:00")
                
                hours_worked = None
                if check_in and check_out:
                    try:
                        h1, m1 = map(int, check_in.split(':'))
                        h2, m2 = map(int, check_out.split(':'))
                        total_minutes = (h2 * 60 + m2) - (h1 * 60 + m1)
                        hours_worked = round(total_minutes / 60, 2)
                    except:
                        pass
                
                if hours_worked:
                    st.info(f"Hours Worked: {hours_worked} hours")
                
                if st.form_submit_button("Save Attendance", use_container_width=True):
                    save_attendance(emp_id, attendance_date, status, check_in, check_out, hours_worked)
                    st.success(f"Attendance saved for {selected_emp} on {attendance_date}!")
                    st.rerun()
        else:
            st.info("No active employees found. Add employees first.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Upload Excel
                    <span class="badge">Bulk Upload</span>
                </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="background:rgba(102,126,234,0.08);border-radius:10px;padding:12px 16px;border:1px solid rgba(102,126,234,0.15);margin-bottom:15px;">
                <div style="color:#a0aec0;font-size:13px;font-weight:500;">Select Date for Upload</div>
                <div style="color:#cbd5e0;font-size:13px;margin-top:4px;">
                    All records in the Excel will be saved with this date
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        upload_date = st.date_input("Attendance Date", datetime.now(), key="upload_date")
        date_str = upload_date.strftime("%Y-%m-%d")
        st.markdown(f'<span class="date-badge">Date: {date_str}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
            <div class="upload-box">
                <span class="icon">Excel</span>
                Upload Excel file with attendance data<br>
                <span style="font-size:12px;color:#4a5568;">.xlsx, .xls files supported</span>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"], key="attendance_excel", label_visibility="collapsed")
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"File uploaded successfully! {len(df)} rows found.")
                
                st.markdown("### Preview Data")
                st.dataframe(df.head(10), use_container_width=True)
                
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:12px;border:1px solid rgba(255,255,255,0.06);margin:10px 0;">
                        <div style="color:#a0aec0;font-size:13px;font-weight:600;">Expected Columns:</div>
                        <div style="color:#cbd5e0;font-size:13px;margin-top:4px;">
                            • <b>Employee Name</b> - Employee full name<br>
                            • <b>Status</b> - Present / Absent / Leave<br>
                            • <b>Check In</b> - HH:MM (optional)<br>
                            • <b>Check Out</b> - HH:MM (optional)
                        </div>
                        <div style="color:#48bb78;font-size:12px;margin-top:6px;">
                            Date will be set to: <b>{date_str}</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button("Import Data", use_container_width=True):
                        active_emps = get_active_employees()
                        emp_lookup = {}
                        for emp in active_emps:
                            emp_lookup[emp.name.lower()] = emp.id
                            if emp.emp_id:
                                emp_lookup[emp.emp_id.lower()] = emp.id
                        
                        success_count = 0
                        error_count = 0
                        errors = []
                        
                        for idx, row in df.iterrows():
                            try:
                                emp_id = None
                                
                                if 'Employee Name' in df.columns:
                                    emp_name = str(row['Employee Name']).strip().lower()
                                    if emp_name in emp_lookup:
                                        emp_id = emp_lookup[emp_name]
                                elif 'Employee ID' in df.columns:
                                    emp_id_val = str(row['Employee ID']).strip().lower()
                                    if emp_id_val in emp_lookup:
                                        emp_id = emp_lookup[emp_id_val]
                                else:
                                    for col in df.columns:
                                        if 'name' in col.lower() or 'employee' in col.lower():
                                            emp_name = str(row[col]).strip().lower()
                                            if emp_name in emp_lookup:
                                                emp_id = emp_lookup[emp_name]
                                                break
                                
                                if not emp_id:
                                    errors.append(f"Row {idx+1}: Employee not found")
                                    error_count += 1
                                    continue
                                
                                status = "Present"
                                if 'Status' in df.columns:
                                    status_val = str(row['Status']).strip().lower()
                                    if status_val == 'absent':
                                        status = "Absent"
                                    elif status_val == 'leave':
                                        status = "Leave"
                                    else:
                                        status = "Present"
                                
                                check_in = None
                                check_out = None
                                if 'Check In' in df.columns:
                                    check_in = str(row['Check In']) if pd.notna(row['Check In']) else None
                                if 'Check Out' in df.columns:
                                    check_out = str(row['Check Out']) if pd.notna(row['Check Out']) else None
                                
                                existing = get_attendance_by_date_and_employee(upload_date, emp_id)
                                
                                if existing:
                                    existing.status = status
                                    existing.check_in = check_in
                                    existing.check_out = check_out
                                    db.commit()
                                else:
                                    attendance = Attendance(
                                        employee_id=emp_id,
                                        date=upload_date,
                                        status=status,
                                        check_in=check_in,
                                        check_out=check_out,
                                        hours_worked=None
                                    )
                                    db.add(attendance)
                                    db.commit()
                                
                                success_count += 1
                                
                            except Exception as e:
                                errors.append(f"Row {idx+1}: {str(e)}")
                                error_count += 1
                        
                        if success_count > 0:
                            st.success(f"{success_count} records imported successfully for {date_str}!")
                        if error_count > 0:
                            st.error(f"{error_count} records failed:")
                            for err in errors[:10]:
                                st.write(f"- {err}")
                            if len(errors) > 10:
                                st.write(f"... and {len(errors) - 10} more errors")
                        
                        st.rerun()
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Attendance Records
                    <span class="badge">Search & Filter</span>
                </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:15px;border:1px solid rgba(255,255,255,0.06);margin-bottom:15px;">
                <div style="color:#a0aec0;font-size:13px;font-weight:500;margin-bottom:10px;">Search / Filter Records</div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_date = st.date_input("Date", datetime.now(), key="search_date")
        with col2:
            status_filter = st.selectbox("Status", ["All", "Present", "Absent", "Leave"], key="status_filter")
        with col3:
            active_emps = get_active_employees()
            emp_filter_options = ["All"] + [emp.name for emp in active_emps]
            emp_filter = st.selectbox("Employee", emp_filter_options, key="emp_filter")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        all_attendance = get_attendance_with_employees()
        
        filtered = all_attendance
        if search_date:
            filtered = [a for a in filtered if a[0].date == search_date]
        if status_filter != "All":
            filtered = [a for a in filtered if a[0].status == status_filter]
        if emp_filter != "All":
            filtered = [a for a in filtered if a[1].name == emp_filter]
        
        if filtered:
            data = []
            for att, emp in filtered:
                data.append({
                    "Date": att.date.strftime("%Y-%m-%d"),
                    "Employee": emp.name if emp else "Unknown",
                    "Department": emp.department if emp else "N/A",
                    "Status": att.status,
                    "Check In": att.check_in or "-",
                    "Check Out": att.check_out or "-",
                    "Hours": att.hours_worked or 0,
                    "ID": att.id
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            total = len(filtered)
            present = sum(1 for a, _ in filtered if a.status == "Present")
            absent = sum(1 for a, _ in filtered if a.status == "Absent")
            leave = sum(1 for a, _ in filtered if a.status == "Leave")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", total)
            with col2:
                st.metric("Present", present)
            with col3:
                st.metric("Absent", absent)
            with col4:
                st.metric("Leave", leave)
            
            st.markdown("---")
            
            st.markdown("#### Delete Record")
            col1, col2 = st.columns([4, 1])
            with col1:
                del_options = {f"{d['Employee']} - {d['Date']} ({d['Status']})": d['ID'] for d in data}
                del_selected = st.selectbox("Select Record to Delete", list(del_options.keys()), key="del_attendance")
                del_id = del_options[del_selected]
            
            with col2:
                if st.button("Delete", use_container_width=True):
                    if delete_attendance(del_id):
                        st.success("Attendance record deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete!")
        else:
            st.info("No attendance records found for the selected filters.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    db.close()