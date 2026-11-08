from sqlalchemy.orm import Session
from backend.models.leave import Leave
from datetime import date
from typing import List, Optional

def get_leave(db: Session, leave_id: int):
    return db.query(Leave).filter(Leave.id == leave_id).first()

def get_leaves_by_employee(db: Session, employee_id: int, status: str = None):
    query = db.query(Leave).filter(Leave.employee_id == employee_id)
    if status:
        query = query.filter(Leave.status == status)
    return query.order_by(Leave.applied_on.desc()).all()

def get_pending_leaves(db: Session):
    return db.query(Leave).filter(Leave.status == "Pending").all()

def create_leave(db: Session, leave_data: dict):
    db_leave = Leave(**leave_data)
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

def update_leave_status(db: Session, leave_id: int, status: str, approved_by: int = None):
    db_leave = get_leave(db, leave_id)
    if db_leave:
        db_leave.status = status
        if approved_by:
            db_leave.approved_by = approved_by
        db.commit()
        db.refresh(db_leave)
    return db_leave

def delete_leave(db: Session, leave_id: int):
    db_leave = get_leave(db, leave_id)
    if db_leave:
        db.delete(db_leave)
        db.commit()
    return db_leave