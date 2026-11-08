from backend.database import SessionLocal
from backend.models import User, Employee, Attendance, Leave, Payroll, Notification
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import bcrypt

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from backend.database import Base, engine
    Base.metadata.create_all(bind=engine)


# ============================================================
# AUTHENTICATION
# ============================================================

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db, user_data: dict):
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ============================================================
# DASHBOARD STATS
# ============================================================

def get_dashboard_stats():
    """Get all dashboard statistics from database"""
    db = SessionLocal()
    
    try:
        # Total Employees
        total_employees = db.query(Employee).count()
        
        # New Hires (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        new_hires = db.query(Employee).filter(Employee.joining_date >= thirty_days_ago).count()
        
        # Active Employees
        active_employees = db.query(Employee).filter(Employee.status == "Active").count()
        
        # Today's Attendance
        today = datetime.now().date()
        attendance_today = db.query(Attendance).filter(Attendance.date == today).all()
        present_today = sum(1 for a in attendance_today if a.status == "Present")
        absent_today = sum(1 for a in attendance_today if a.status == "Absent")
        
        # Pending Leaves
        pending_leaves = db.query(Leave).filter(Leave.status == "Pending").count()
        
        return {
            "total_employees": total_employees,
            "new_hires": new_hires,
            "active_employees": active_employees,
            "present_today": present_today,
            "absent_today": absent_today,
            "pending_leaves": pending_leaves,
            "attendance_total": len(attendance_today)
        }
    finally:
        db.close()

def get_pending_approvals():
    """Get all pending approvals"""
    db = SessionLocal()
    try:
        return db.query(Leave).filter(Leave.status == "Pending").all()
    finally:
        db.close()


# ============================================================
# EMPLOYEE CRUD
# ============================================================

def get_employee(db, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_employee_by_email(db, email: str):
    return db.query(Employee).filter(Employee.email == email).first()

def get_all_employees(db):
    return db.query(Employee).all()

def get_active_employees(db):
    return db.query(Employee).filter(Employee.status == "Active").all()

def get_old_employees(db):
    return db.query(Employee).filter(Employee.status != "Active").all()

def get_employees_by_department(db, department: str):
    return db.query(Employee).filter(Employee.department == department).all()

def get_employees_by_status(db, status: str):
    return db.query(Employee).filter(Employee.status == status).all()

def create_employee(db, employee_data: dict):
    db_employee = Employee(**employee_data)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db, employee_id: int, employee_data: dict):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        for key, value in employee_data.items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee

def delete_employee(db, employee_id: int):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
    return db_employee

def search_employees(db, search_term: str):
    return db.query(Employee).filter(
        or_(
            Employee.name.contains(search_term),
            Employee.email.contains(search_term),
            Employee.department.contains(search_term)
        )
    ).all()


# ============================================================
# ATTENDANCE CRUD
# ============================================================

def get_attendance(db, attendance_id: int):
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()

def get_attendance_by_employee(db, employee_id: int, start_date=None, end_date=None):
    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    return query.order_by(Attendance.date.desc()).all()

def get_attendance_by_date(db, attendance_date: date):
    return db.query(Attendance).filter(Attendance.date == attendance_date).all()

def get_today_attendance(db):
    today = datetime.now().date()
    return db.query(Attendance).filter(Attendance.date == today).all()

def create_attendance(db, attendance_data: dict):
    db_attendance = Attendance(**attendance_data)
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def update_attendance(db, attendance_id: int, attendance_data: dict):
    db_attendance = get_attendance(db, attendance_id)
    if db_attendance:
        for key, value in attendance_data.items():
            setattr(db_attendance, key, value)
        db.commit()
        db.refresh(db_attendance)
    return db_attendance

def delete_attendance(db, attendance_id: int):
    db_attendance = get_attendance(db, attendance_id)
    if db_attendance:
        db.delete(db_attendance)
        db.commit()
    return db_attendance


# ============================================================
# LEAVE CRUD
# ============================================================

def get_leave(db, leave_id: int):
    return db.query(Leave).filter(Leave.id == leave_id).first()

def get_leaves_by_employee(db, employee_id: int, status=None):
    query = db.query(Leave).filter(Leave.employee_id == employee_id)
    if status:
        query = query.filter(Leave.status == status)
    return query.order_by(Leave.applied_on.desc()).all()

def get_pending_leaves(db):
    return db.query(Leave).filter(Leave.status == "Pending").all()

def get_approved_leaves(db):
    return db.query(Leave).filter(Leave.status == "Approved").all()

def get_rejected_leaves(db):
    return db.query(Leave).filter(Leave.status == "Rejected").all()

def create_leave(db, leave_data: dict):
    db_leave = Leave(**leave_data)
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

def update_leave_status(db, leave_id: int, status: str, approved_by: int = None):
    db_leave = get_leave(db, leave_id)
    if db_leave:
        db_leave.status = status
        if approved_by:
            db_leave.approved_by = approved_by
            db_leave.approved_on = datetime.now()
        db.commit()
        db.refresh(db_leave)
    return db_leave

def delete_leave(db, leave_id: int):
    db_leave = get_leave(db, leave_id)
    if db_leave:
        db.delete(db_leave)
        db.commit()
    return db_leave


# ============================================================
# PAYROLL CRUD
# ============================================================

def get_payroll(db, payroll_id: int):
    return db.query(Payroll).filter(Payroll.id == payroll_id).first()

def get_payroll_by_employee(db, employee_id: int, month: str = None):
    query = db.query(Payroll).filter(Payroll.employee_id == employee_id)
    if month:
        query = query.filter(Payroll.month == month)
    return query.order_by(Payroll.month.desc()).all()

def get_payroll_by_month(db, month: str):
    return db.query(Payroll).filter(Payroll.month == month).all()

def create_payroll(db, payroll_data: dict):
    db_payroll = Payroll(**payroll_data)
    db.add(db_payroll)
    db.commit()
    db.refresh(db_payroll)
    return db_payroll

def update_payroll_status(db, payroll_id: int, status: str):
    db_payroll = get_payroll(db, payroll_id)
    if db_payroll:
        db_payroll.status = status
        db.commit()
        db.refresh(db_payroll)
    return db_payroll

def delete_payroll(db, payroll_id: int):
    db_payroll = get_payroll(db, payroll_id)
    if db_payroll:
        db.delete(db_payroll)
        db.commit()
    return db_payroll

def get_payroll_summary(db, month: str):
    payrolls = get_payroll_by_month(db, month)
    total = sum(p.net_salary for p in payrolls)
    paid = sum(p.net_salary for p in payrolls if p.status == "Paid")
    pending = sum(p.net_salary for p in payrolls if p.status == "Pending")
    return {"total": total, "paid": paid, "pending": pending}


# ============================================================
# NOTIFICATION CRUD
# ============================================================

def get_notification(db, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_all_notifications(db):
    return db.query(Notification).order_by(Notification.created_at.desc()).all()

def get_notifications_by_employee(db, employee_id: int):
    return db.query(Notification).filter(
        or_(
            Notification.employee_id == employee_id,
            Notification.send_to == "All Employees"
        )
    ).order_by(Notification.created_at.desc()).all()

def get_unread_notifications(db, employee_id: int = None):
    query = db.query(Notification).filter(Notification.is_read == False)
    if employee_id:
        query = query.filter(
            or_(
                Notification.employee_id == employee_id,
                Notification.send_to == "All Employees"
            )
        )
    return query.order_by(Notification.created_at.desc()).all()

def create_notification(db, notification_data: dict):
    db_notification = Notification(**notification_data)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def mark_notification_read(db, notification_id: int):
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db_notification.is_read = True
        db.commit()
        db.refresh(db_notification)
    return db_notification

def mark_all_notifications_read(db, employee_id: int = None):
    query = db.query(Notification).filter(Notification.is_read == False)
    if employee_id:
        query = query.filter(
            or_(
                Notification.employee_id == employee_id,
                Notification.send_to == "All Employees"
            )
        )
    query.update({"is_read": True})
    db.commit()

def delete_notification(db, notification_id: int):
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db.delete(db_notification)
        db.commit()
    return db_notification


# ============================================================
# HR STAFF CRUD (Users with role HR)
# ============================================================

def get_hr_staff(db):
    return db.query(User).filter(User.role == "HR").all()

def get_hr_staff_by_id(db, user_id: int):
    return db.query(User).filter(User.id == user_id, User.role == "HR").first()

def create_hr_staff(db, user_data: dict):
    user_data["role"] = "HR"
    return create_user(db, user_data)

def update_hr_staff(db, user_id: int, user_data: dict):
    db_user = get_hr_staff_by_id(db, user_id)
    if db_user:
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_hr_staff(db, user_id: int):
    db_user = get_hr_staff_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


# ============================================================
# SEED DATA
# ============================================================

def seed_default_users():
    """Create default users if they don't exist"""
    db = SessionLocal()
    try:
        users = [
            {"username": "hr", "email": "hr@hrms.com", "password": "hr@portal1166", "full_name": "HR Manager", "role": "HR"},
            {"username": "admin", "email": "admin@hrms.com", "password": "admin@portal1166", "full_name": "System Admin", "role": "Admin"}
        ]
        
        for user_data in users:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"]
                )
                db.add(user)
                print(f"✅ User {user_data['username']} created!")
        db.commit()
    finally:
        db.close()

def seed_sample_employees():
    """Create sample employees if none exist"""
    db = SessionLocal()
    try:
        if db.query(Employee).count() == 0:
            employees = [
                {"name": "Zara Malik", "email": "zara@email.com", "phone": "0300-1111111", 
                 "designation": "Marketing Manager", "department": "Marketing", "employee_type": "Permanent",
                 "joining_date": datetime(2025, 10, 1).date(), "status": "Active"},
                {"name": "Hassan Raza", "email": "hassan@email.com", "phone": "0300-2222222",
                 "designation": "IT Manager", "department": "IT", "employee_type": "Temporary",
                 "joining_date": datetime(2026, 6, 10).date(), "status": "Active"},
                {"name": "Fatima Noor", "email": "fatima@email.com", "phone": "0300-3333333",
                 "designation": "HR Executive", "department": "HR", "employee_type": "Permanent",
                 "joining_date": datetime(2025, 9, 15).date(), "status": "Active"},
                {"name": "Ahmed Khan", "email": "ahmed@email.com", "phone": "0300-4444444",
                 "designation": "Sr. Manager", "department": "Operations", "employee_type": "Permanent",
                 "joining_date": datetime(2024, 1, 15).date(), "status": "Inactive",
                 "exit_type": "Resign", "exit_date": datetime(2026, 1, 15).date()},
                {"name": "Sara Ali", "email": "sara@email.com", "phone": "0300-5555555",
                 "designation": "Team Lead", "department": "IT", "employee_type": "Permanent",
                 "joining_date": datetime(2023, 11, 20).date(), "status": "Inactive",
                 "exit_type": "Terminated", "exit_date": datetime(2025, 11, 20).date()}
            ]
            for emp_data in employees:
                emp = Employee(**emp_data)
                db.add(emp)
            db.commit()
            print("✅ Sample employees seeded!")
    finally:
        db.close()