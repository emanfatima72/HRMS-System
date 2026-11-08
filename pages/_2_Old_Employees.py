import streamlit as st
import pandas as pd
from datetime import datetime
from backend.database import SessionLocal
from backend.models.employee import Employee
from backend.models.attendance import Attendance
from backend.models.leave import Leave
from backend.models.payroll import Payroll
from backend.models.admin_promotion import AdminPromotion
from backend.models.promotion import Promotion
from backend.models.notification import Notification
from utils.audit_logger import add_audit_log, get_current_user

def show():
    add_audit_log(
        get_current_user(),
        "View Old Employees",
        "HR viewed old employees list"
    )
    
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
            
            .status-badge {
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                display: inline-block;
            }
            .status-resign { background: #48bb78; color: white; }
            .status-terminated { background: #fc8181; color: white; }
            .status-runaway { background: #ed8936; color: white; }
            
            .legend-item {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #a0aec0;
                font-size: 13px;
                padding: 6px 0;
            }
            .legend-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                flex-shrink: 0;
            }
            .legend-dot.resign { background: #48bb78; }
            .legend-dot.terminated { background: #fc8181; }
            .legend-dot.runaway { background: #ed8936; }
            
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
                background: rgba(252,129,129,0.15);
                border: 1px solid rgba(252,129,129,0.2);
                border-radius: 6px;
                padding: 4px 14px;
                color: #fc8181;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            .action-btn:hover {
                background: rgba(252,129,129,0.3);
                border-color: rgba(252,129,129,0.5);
                transform: scale(1.02);
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Old Employees</div>
        <div class="page-subtitle">Former employees with exit status tracking</div>
    """, unsafe_allow_html=True)
    
    if 'old_search_query' not in st.session_state:
        st.session_state.old_search_query = ""
    
    db = SessionLocal()
    
    def get_old_employees():
        return db.query(Employee).filter(
            Employee.status == "Inactive"
        ).all()
    
    def delete_employee_from_db(email):
        emp = db.query(Employee).filter(Employee.email == email).first()
        if not emp:
            return False
        
        try:
            emp_id = emp.id
            emp_name = emp.name
            
            db.query(Notification).filter(Notification.send_to == emp.name).delete()
            db.query(AdminPromotion).filter(AdminPromotion.employee_id == emp_id).delete()
            db.query(Promotion).filter(Promotion.employee_id == emp_id).delete()
            db.query(Attendance).filter(Attendance.employee_id == emp_id).delete()
            db.query(Leave).filter(Leave.employee_id == emp_id).delete()
            db.query(Payroll).filter(Payroll.employee_id == emp_id).delete()
            
            db.delete(emp)
            db.commit()
            
            add_audit_log(
                get_current_user(),
                "Delete Old Employee",
                f"Deleted old employee: {emp_name} ({email})"
            )
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error deleting employee: {str(e)}")
            return False
    
    old_employees = get_old_employees()
    
    old_data = []
    for emp in old_employees:
        old_data.append({
            "Name": emp.name,
            "Exit Type": emp.exit_type or "N/A",
            "Last Designation": emp.designation or "N/A",
            "Exit Date": emp.exit_date.strftime("%Y-%m-%d") if emp.exit_date else "N/A",
            "Reason": emp.exit_reason or "N/A",
            "Email": emp.email,
            "Emp ID": emp.emp_id or f"EMP-{emp.id:06d}"
        })
    
    search_query = st.text_input(
        "Search",
        placeholder="Search by name, email, ID, or exit type...",
        key="old_search_query",
        label_visibility="collapsed"
    )
    
    filtered_data = old_data
    if search_query:
        search_lower = search_query.lower()
        filtered_data = [
            e for e in old_data 
            if search_lower in e.get('Name', '').lower() or 
               search_lower in e.get('Email', '').lower() or 
               search_lower in e.get('Emp ID', '').lower() or
               search_lower in e.get('Exit Type', '').lower()
        ]
    
    if filtered_data:
        st.markdown(f"""
            <div style="color:#a0aec0;font-size:13px;margin-bottom:12px;">
                Showing <strong style="color:#ffffff;">{len(filtered_data)}</strong> of <strong style="color:#ffffff;">{len(old_data)}</strong> employees
            </div>
        """, unsafe_allow_html=True)
        
        display_data = []
        for emp in filtered_data:
            display_data.append({
                "Name": emp.get('Name', 'N/A'),
                "Exit Type": emp.get('Exit Type', 'N/A'),
                "Last Designation": emp.get('Last Designation', 'N/A'),
                "Exit Date": emp.get('Exit Date', 'N/A'),
                "Email": emp.get('Email', 'N/A'),
                "Emp ID": emp.get('Emp ID', 'N/A')
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### Delete Employee")
        st.caption("Permanently delete employee record from the system")
        
        for idx, emp in enumerate(filtered_data):
            col1, col2, col3 = st.columns([4, 1, 4])
            
            with col1:
                st.markdown(f"**{emp.get('Name', 'N/A')}**")
            
            with col2:
                if st.button("Delete", key=f"old_delete_{idx}_{emp.get('Emp ID', '')}", use_container_width=True):
                    if delete_employee_from_db(emp.get('Email')):
                        st.success(f"Employee {emp.get('Name')} deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete employee! Please try again.")
        
        st.markdown("""
            <div style="margin-top: 20px; display: flex; gap: 30px; flex-wrap: wrap; padding: 10px 0;">
                <div class="legend-item"><span class="legend-dot resign"></span> Proper Resign - Eligible for Rehire</div>
                <div class="legend-item"><span class="legend-dot terminated"></span> Terminated - Not Eligible</div>
                <div class="legend-item"><span class="legend-dot runaway"></span> Runaway - No Notice Given</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="color:#a0aec0;font-size:13px;margin-top:10px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);">
                Total Old Employees: <strong style="color:#ffffff;">{len(old_data)}</strong>
            </div>
        """, unsafe_allow_html=True)
        
        if old_data:
            st.markdown("---")
            if st.button("Clear All Records", use_container_width=True):
                for emp in old_data:
                    delete_employee_from_db(emp.get('Email'))
                st.success("All old employee records cleared successfully!")
                st.rerun()
    
    else:
        st.info("No old employees found. Employees moved from Current will appear here.")
    
    db.close()