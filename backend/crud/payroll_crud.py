from sqlalchemy.orm import Session
from backend.models.payroll import Payroll
from typing import List, Optional

def get_payroll(db: Session, payroll_id: int):
    return db.query(Payroll).filter(Payroll.id == payroll_id).first()

def get_payroll_by_employee(db: Session, employee_id: int, month: str = None):
    query = db.query(Payroll).filter(Payroll.employee_id == employee_id)
    if month:
        query = query.filter(Payroll.month == month)
    return query.order_by(Payroll.month.desc()).all()

def get_payroll_by_month(db: Session, month: str):
    return db.query(Payroll).filter(Payroll.month == month).all()

def create_payroll(db: Session, payroll_data: dict):
    db_payroll = Payroll(**payroll_data)
    db.add(db_payroll)
    db.commit()
    db.refresh(db_payroll)
    return db_payroll

def update_payroll_status(db: Session, payroll_id: int, status: str):
    db_payroll = get_payroll(db, payroll_id)
    if db_payroll:
        db_payroll.status = status
        db.commit()
        db.refresh(db_payroll)
    return db_payroll

def delete_payroll(db: Session, payroll_id: int):
    db_payroll = get_payroll(db, payroll_id)
    if db_payroll:
        db.delete(db_payroll)
        db.commit()
    return db_payroll

def get_payroll_summary(db: Session, month: str):
    payrolls = get_payroll_by_month(db, month)
    total = sum(p.net_salary for p in payrolls)
    paid = sum(p.net_salary for p in payrolls if p.status == "Paid")
    pending = sum(p.net_salary for p in payrolls if p.status == "Pending")
    return {"total": total, "paid": paid, "pending": pending}