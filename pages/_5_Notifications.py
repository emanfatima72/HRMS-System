import streamlit as st
from datetime import datetime
from backend.database import SessionLocal
from backend.models.employee import Employee
from backend.models.notification import Notification
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
            
            .notif-card {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                padding: 15px 18px;
                margin-bottom: 12px;
                border-left: 4px solid #a0aec0;
                transition: all 0.3s ease;
                position: relative;
            }
            .notif-card:hover {
                background: rgba(255,255,255,0.08);
            }
            .notif-card .notif-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 8px;
            }
            .notif-card .notif-category {
                font-size: 10px;
                padding: 2px 12px;
                border-radius: 20px;
                color: white;
                font-weight: 500;
            }
            .notif-card .notif-priority {
                font-size: 10px;
                font-weight: 600;
            }
            .notif-card .notif-message {
                color: #cbd5e0;
                font-size: 14px;
                margin-top: 8px;
                line-height: 1.5;
            }
            .notif-card .notif-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 10px;
                font-size: 11px;
                color: #4a5568;
            }
            
            .stat-box {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.06);
            }
            .stat-box .number {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
            }
            .stat-box .label {
                color: #a0aec0;
                font-size: 12px;
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
                padding: 10px 14px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.08);
                background: rgba(255,255,255,0.04);
                color: #ffffff;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
            }
            .form-group textarea {
                resize: vertical;
                min-height: 80px;
            }
            .form-group select option {
                background: #1a1a2e;
            }
            
            .empty-state {
                text-align: center;
                padding: 40px 20px;
                color: #4a5568;
            }
            .empty-state .icon {
                font-size: 48px;
                display: block;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">Notifications</div>
        <div class="page-subtitle">Manage and send notifications to employees</div>
    """, unsafe_allow_html=True)
    
    if 'notification_categories' not in st.session_state:
        st.session_state.notification_categories = ["Weather", "Leaves", "Event", "Emergency", "General"]
    
    db = SessionLocal()
    
    def get_all_notifications():
        return db.query(Notification).order_by(Notification.created_at.desc()).all()
    
    def get_active_employees():
        """Get active employees excluding HR department"""
        return db.query(Employee).filter(
            Employee.status == "Active",
            Employee.department != "HR"
        ).all()
    
    def delete_notification(notif_id):
        notif = db.query(Notification).filter(Notification.id == notif_id).first()
        if notif:
            db.delete(notif)
            db.commit()
            return True
        return False
    
    def save_notification(send_to, category, message, priority):
        notif = Notification(
            send_to=send_to,
            category=category,
            message=message,
            priority=priority,
            is_read=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        
        # 🔥 ADD AUDIT LOG
        add_audit_log(
            get_current_user(),
            "Send Notification",
            f"Sent {category} notification to {send_to}"
        )
        return notif
    
    notifications = get_all_notifications()
    
    total_notifs = len(notifications)
    unread_notifs = sum(1 for n in notifications if not n.is_read)
    active_employees = get_active_employees()
    employee_names = [emp.name for emp in active_employees] if active_employees else []
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="stat-box">
                <div class="number">{total_notifs}</div>
                <div class="label">Total Notifications</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="stat-box">
                <div class="number">{unread_notifs}</div>
                <div class="label">Unread</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        categories = set(n.category for n in notifications)
        st.markdown(f"""
            <div class="stat-box">
                <div class="number">{len(categories)}</div>
                <div class="label">Categories</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="stat-box">
                <div class="number">{len(st.session_state.notification_categories)}</div>
                <div class="label">Available Categories</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Send Notification", "All Notifications"])
    
    with tab1:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Send New Notification
                    <span class="badge">To Employees</span>
                </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            send_to = st.selectbox("Send To", ["All Employees", "Specific Employee"], key="send_to_select")
            category = st.selectbox("Category", st.session_state.notification_categories, key="category_select")
        with col2:
            priority = st.selectbox("Priority", ["Normal", "High", "Urgent"], key="priority_select")
        
        employee = "All Employees"
        if send_to == "Specific Employee":
            if employee_names:
                employee = st.selectbox("Select Employee", employee_names, key="specific_employee_select")
            else:
                st.warning("No active employees found.")
                employee = st.text_input("Employee Name", placeholder="Enter employee name", key="specific_employee_manual")
        else:
            employee = "All Employees"
        
        message = st.text_area("Message *", placeholder="Type your notification here...", height=120, key="message_area")
        
        if st.button("Send", use_container_width=True, key="send_notification_btn"):
            if message:
                save_notification(employee, category, message, priority)
                st.success(f"Notification sent to {employee}!")
                st.rerun()
            else:
                st.error("Please enter a message!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Filter Notifications
                    <span class="badge">Search & Filter</span>
                </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_category = st.selectbox("Category", ["All"] + st.session_state.notification_categories, key="filter_category")
        with col2:
            filter_priority = st.selectbox("Priority", ["All", "Normal", "High", "Urgent"], key="filter_priority")
        with col3:
            filter_send_to = st.selectbox("Sent To", ["All", "All Employees", "Specific Employee"], key="filter_send_to")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if notifications:
            filtered = notifications.copy()
            
            if filter_category != "All":
                filtered = [n for n in filtered if n.category == filter_category]
            if filter_priority != "All":
                filtered = [n for n in filtered if n.priority == filter_priority]
            if filter_send_to != "All":
                if filter_send_to == "All Employees":
                    filtered = [n for n in filtered if n.send_to == "All Employees"]
                else:
                    filtered = [n for n in filtered if n.send_to != "All Employees"]
            
            if filtered:
                for notif in filtered:
                    priority_color = "#a0aec0"
                    if notif.priority == "High":
                        priority_color = "#ed8936"
                    elif notif.priority == "Urgent":
                        priority_color = "#fc8181"
                    
                    category_colors = {
                        "Weather": "#4299e1",
                        "Leaves": "#48bb78",
                        "Event": "#9f7aea",
                        "Emergency": "#fc8181",
                        "General": "#a0aec0"
                    }
                    cat_color = category_colors.get(notif.category, "#a0aec0")
                    
                    date_str = notif.created_at.strftime('%Y-%m-%d')
                    time_str = notif.created_at.strftime('%H:%M')
                    
                    st.markdown(f"""
                        <div class="notif-card" style="border-left-color: {priority_color};">
                            <div class="notif-header">
                                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                                    <span class="notif-category" style="background:{cat_color};">{notif.category}</span>
                                    <span class="notif-priority" style="color:{priority_color};">{notif.priority}</span>
                                    <span style="color:#4a5568;font-size:11px;">To: {notif.send_to}</span>
                                </div>
                                <span style="color:#4a5568;font-size:11px;">{date_str}</span>
                            </div>
                            <div class="notif-message">
                                {notif.message}
                            </div>
                            <div class="notif-footer">
                                <span>Time: {time_str}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([5, 1, 5])
                    with col2:
                        if st.button("X", key=f"del_{notif.id}", help="Delete this notification"):
                            if delete_notification(notif.id):
                                st.success("Notification deleted!")
                                st.rerun()
                
                st.markdown(f"""
                    <div style="color:#a0aec0;font-size:13px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);">
                        Showing <strong style="color:#ffffff;">{len(filtered)}</strong> of <strong style="color:#ffffff;">{len(notifications)}</strong> notifications
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Clear All Notifications", use_container_width=True):
                    for n in notifications:
                        delete_notification(n.id)
                    st.success("All notifications cleared!")
                    st.rerun()
            else:
                st.markdown("""
                    <div class="empty-state">
                        <span class="icon">Search</span>
                        <div style="font-size:18px;color:#a0aec0;">No notifications match your filters</div>
                        <div style="font-size:13px;">Try adjusting your filter criteria</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="empty-state">
                    <span class="icon">Inbox</span>
                    <div style="font-size:18px;color:#a0aec0;">No notifications yet</div>
                    <div style="font-size:13px;">Send your first notification from the Send Notification tab</div>
                </div>
            """, unsafe_allow_html=True)
    
    db.close()