from sqlalchemy.orm import Session
from backend.models.attendance import Attendance
from datetime import date
from typing import List, Optional

def get_attendance(db: Session, attendance_id: int):
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()

def get_attendance_by_employee(db: Session, employee_id: int, start_date: date = None, end_date: date = None):
    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    return query.order_by(Attendance.date.desc()).all()

def get_attendance_by_date(db: Session, attendance_date: date):
    return db.query(Attendance).filter(Attendance.date == attendance_date).all()

def create_attendance(db: Session, attendance_data: dict):
    db_attendance = Attendance(**attendance_data)
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def update_attendance(db: Session, attendance_id: int, attendance_data: dict):
    db_attendance = get_attendance(db, attendance_id)
    if db_attendance:
        for key, value in attendance_data.items():
            setattr(db_attendance, key, value)
        db.commit()
        db.refresh(db_attendance)
    return db_attendance

def delete_attendance(db: Session, attendance_id: int):
    db_attendance = get_attendance(db, attendance_id)
    if db_attendance:
        db.delete(db_attendance)
        db.commit()
    return db_attendance

def get_attendance_summary(db: Session, employee_id: int, month: int, year: int):
    # Returns: present, absent, leave count
    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)
    # Add month/year filter logic
    return query.all()