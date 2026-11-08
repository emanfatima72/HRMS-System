from sqlalchemy.orm import Session
from backend.models.employee import Employee
from typing import List, Optional

def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_employee_by_email(db: Session, email: str):
    return db.query(Employee).filter(Employee.email == email).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Employee).offset(skip).limit(limit).all()

def get_employees_by_status(db: Session, status: str):
    return db.query(Employee).filter(Employee.status == status).all()

def get_employees_by_department(db: Session, department: str):
    return db.query(Employee).filter(Employee.department == department).all()

def create_employee(db: Session, employee_data: dict):
    db_employee = Employee(**employee_data)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int, employee_data: dict):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        for key, value in employee_data.items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
    return db_employee

def search_employees(db: Session, search_term: str):
    return db.query(Employee).filter(
        Employee.name.contains(search_term) | 
        Employee.email.contains(search_term) |
        Employee.department.contains(search_term)
    ).all()