import streamlit as st
from datetime import datetime
from backend.database import SessionLocal
from backend.models.employee import Employee
from utils.audit_logger import add_audit_log, get_current_user

def show():
    # Add log for viewing dashboard
    add_audit_log(
        get_current_user(),
        "View Dashboard",
        "HR viewed dashboard overview"
    )
    
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            }
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 2rem;
            }
            
            .dash-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                padding: 10px 0;
            }
            .dash-title {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
            }
            .dash-title span {
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .dash-subtitle {
                color: #a0aec0;
                font-size: 14px;
            }
            .dash-date {
                color: #a0aec0;
                font-size: 13px;
                background: rgba(255,255,255,0.05);
                padding: 8px 16px;
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.08);
            }
            
            .stat-card {
                background: rgba(255,255,255,0.06);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 20px 22px;
                transition: all 0.3s ease;
            }
            .stat-card:hover {
                transform: translateY(-4px);
                background: rgba(255,255,255,0.10);
                border-color: rgba(102, 126, 234, 0.3);
                box-shadow: 0 8px 30px rgba(0,0,0,0.3);
            }
            .stat-number {
                font-size: 32px;
                font-weight: 700;
                color: #ffffff;
            }
            .stat-label {
                color: #a0aec0;
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
            .stat-icon {
                float: right;
                font-size: 22px;
                opacity: 0.6;
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
            }
            .section-title span {
                color: #a0aec0;
                font-size: 13px;
                font-weight: 400;
                float: right;
            }
            
            .pending-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid rgba(255,255,255,0.06);
            }
            .pending-item:last-child {
                border-bottom: none;
            }
            .pending-name {
                color: #ffffff;
                font-weight: 500;
                font-size: 14px;
            }
            .pending-detail {
                color: #a0aec0;
                font-size: 13px;
            }
            .pending-badge {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 3px 14px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
            }
            
            .attendance-row {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }
            .attendance-item {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #a0aec0;
                font-size: 14px;
            }
            .attendance-item .num {
                font-weight: 700;
                color: #ffffff;
                font-size: 18px;
            }
            .attendance-item .dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                display: inline-block;
            }
            .dot.present { background: #48bb78; }
            .dot.absent { background: #fc8181; }
            .dot.total { background: #667eea; }
            
            .info-box {
                background: rgba(102, 126, 234, 0.1);
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 12px;
                padding: 18px 22px;
                margin-top: 20px;
            }
            .info-box h4 {
                color: #a0aec0;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .info-box ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            .info-box ul li {
                color: #cbd5e0;
                font-size: 13px;
                padding: 4px 0;
            }
            .info-box ul li::before {
                content: "> ";
                color: #48bb78;
            }
            
            .footer-stats {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 0 5px 0;
                border-top: 1px solid rgba(255,255,255,0.06);
                margin-top: 10px;
            }
            .footer-stat-item {
                color: #a0aec0;
                font-size: 13px;
            }
            .footer-stat-item strong {
                color: #ffffff;
            }
            
            @media (max-width: 768px) {
                .dash-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 10px;
                }
                .stat-card {
                    padding: 15px;
                }
                .stat-number {
                    font-size: 24px;
                }
                .footer-stats {
                    flex-direction: column;
                    gap: 8px;
                    align-items: flex-start;
                }
            }
        </style>
    """, unsafe_allow_html=True)
    
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    st.markdown(f"""
        <div class="dash-header">
            <div>
                <div class="dash-title">HR Overview</div>
                <div class="dash-subtitle">Welcome back! Here's what's happening with your workforce today.</div>
            </div>
            <div class="dash-date">Date: {today}</div>
        </div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    active_employees = db.query(Employee).filter(
        Employee.status == "Active",
        Employee.department != "HR"
    ).all()
    total_active = len(active_employees)
    
    permanent = sum(1 for e in active_employees if e.employee_type == "Permanent")
    temporary = sum(1 for e in active_employees if e.employee_type == "Temporary")
    contract = sum(1 for e in active_employees if e.employee_type == "Contract")
    
    pending_employees = db.query(Employee).filter(Employee.status == "Pending").all()
    total_pending = len(pending_employees)
    
    db.close()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <span class="stat-icon">TE</span>
                <div class="stat-label">TOTAL EMPLOYEES</div>
                <div class="stat-number">{total_active}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <span class="stat-icon">NH</span>
                <div class="stat-label">NEW HIRES</div>
                <div class="stat-number">{total_pending}</div>
                <div style="color:#48bb78;font-size:12px;">Pending Review</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <span class="stat-icon">PL</span>
                <div class="stat-label">PENDING LEAVES</div>
                <div class="stat-number">0</div>
                <div style="color:#a0aec0;font-size:12px;">Pending Requests</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <span class="stat-icon">AE</span>
                <div class="stat-label">ACTIVE EMPLOYEES</div>
                <div class="stat-number">{total_active}</div>
                <div style="color:#48bb78;font-size:12px;">Active Workforce</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1.2])
    
    with col_left:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">Today's Attendance <span>0% Rate Today</span></div>
                <div class="attendance-row">
                    <div class="attendance-item">
                        <span class="dot present"></span>
                        Present: <span class="num">0</span>
                    </div>
                    <div class="attendance-item">
                        <span class="dot absent"></span>
                        Absent: <span class="num">0</span>
                    </div>
                    <div class="attendance-item">
                        <span class="dot total"></span>
                        Total: <span class="num">0</span>
                    </div>
                </div>
                <div style="margin-top:10px;color:#a0aec0;font-size:13px;">
                    Active Workforce +0% from last month
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="info-box">
                <h4>System Working</h4>
                <ul>
                    <li><b>OLD Employees:</b> Exit tracking (Resign, Terminated, Runaway)</li>
                    <li><b>CURRENT Employees:</b> Performance, Salary, Promotion tracking</li>
                    <li><b>NEW Employee:</b> AI-powered CV parsing</li>
                    <li><b>Notifications:</b> Weather, Time, Office alerts</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">Pending Approvals <span>0 items</span></div>
        """, unsafe_allow_html=True)
        
        if total_pending > 0:
            for emp in pending_employees[:3]:
                st.markdown(f"""
                    <div class="pending-item">
                        <div>
                            <div class="pending-name">{emp.name}</div>
                            <div class="pending-detail">New Employee - Pending Review</div>
                        </div>
                        <span class="pending-badge">Review</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="color:#4a5568;font-size:14px;padding:15px 0;text-align:center;">
                    No pending approvals
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
                <div class="footer-stats">
                    <span class="footer-stat-item">Pending: <strong>{total_pending}</strong> Approvals</span>
                </div>
            </div>
        """, unsafe_allow_html=True)