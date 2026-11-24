"""Employee routes — full CRUD + availability management."""

import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.models import Employee, Availability, Department

router = APIRouter(prefix="/employees", tags=["Employees"])


# ── Schemas ───────────────────────────────────────────────────────────────────
class EmployeeCreate(BaseModel):
    name: str
    email: Optional[str] = None
    role: str = Field(..., pattern="^(DOCTOR|NURSE|TECHNICIAN|ADMIN)$")
    department_id: int
    max_hours_week: int = 40
    qualifications: list[str] = []


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[int] = None
    max_hours_week: Optional[int] = None
    qualifications: Optional[list[str]] = None
    is_active: Optional[bool] = None


class AvailabilitySet(BaseModel):
    dates: list[str]           # ISO date strings YYYY-MM-DD
    morning_avail: bool   = True
    afternoon_avail: bool = True
    night_avail: bool     = True


def _serialize(emp: Employee) -> dict:
    return {
        "id":             emp.id,
        "name":           emp.name,
        "email":          emp.email,
        "role":           emp.role,
        "department_id":  emp.department_id,
        "department_name": emp.department.name if emp.department else None,
        "max_hours_week": emp.max_hours_week,
        "qualifications": json.loads(emp.qualifications or "[]"),
        "is_active":      emp.is_active,
        "created_at":     emp.created_at,
    }


# ── GET /employees ─────────────────────────────────────────────────────────────
@router.get("/")
def list_employees(
    department_id: Optional[int]  = Query(None),
    role:          Optional[str]  = Query(None),
    is_active:     Optional[bool] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(Employee)
    if department_id is not None:
        q = q.filter(Employee.department_id == department_id)
    if role:
        q = q.filter(Employee.role == role.upper())
    if is_active is not None:
        q = q.filter(Employee.is_active == is_active)
    employees = q.offset(skip).limit(limit).all()
    return {"total": q.count(), "data": [_serialize(e) for e in employees]}


# ── GET /employees/{id} ────────────────────────────────────────────────────────
@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _serialize(emp)


# ── POST /employees ────────────────────────────────────────────────────────────
@router.post("/", status_code=201)
def create_employee(body: EmployeeCreate, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == body.department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    emp = Employee(
        name           = body.name,
        email          = body.email,
        role           = body.role,
        department_id  = body.department_id,
        max_hours_week = body.max_hours_week,
        qualifications = json.dumps(body.qualifications),
        created_at     = datetime.utcnow().isoformat(),
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return _serialize(emp)


# ── PUT /employees/{id} ────────────────────────────────────────────────────────
@router.put("/{employee_id}")
def update_employee(employee_id: int, body: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in body.model_dump(exclude_none=True).items():
        if field == "qualifications":
            value = json.dumps(value)
        setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return _serialize(emp)


# ── DELETE /employees/{id} (soft delete) ──────────────────────────────────────
@router.delete("/{employee_id}")
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_active = False
    db.commit()
    return {"message": f"Employee {employee_id} deactivated"}


# ── POST /employees/{id}/availability ─────────────────────────────────────────
@router.post("/{employee_id}/availability")
def set_availability(employee_id: int, body: AvailabilitySet, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for d in body.dates:
        existing = db.query(Availability).filter(
            Availability.employee_id == employee_id,
            Availability.avail_date  == d,
        ).first()
        if existing:
            existing.morning_avail   = body.morning_avail
            existing.afternoon_avail = body.afternoon_avail
            existing.night_avail     = body.night_avail
        else:
            db.add(Availability(
                employee_id     = employee_id,
                avail_date      = d,
                morning_avail   = body.morning_avail,
                afternoon_avail = body.afternoon_avail,
                night_avail     = body.night_avail,
            ))
    db.commit()
    return {"message": f"Availability set for {len(body.dates)} dates"}


# ── GET /employees/{id}/availability ──────────────────────────────────────────
@router.get("/{employee_id}/availability")
def get_availability(employee_id: int, db: Session = Depends(get_db)):
    avail = db.query(Availability).filter(Availability.employee_id == employee_id).all()
    return [{"date": a.avail_date, "morning": a.morning_avail, "afternoon": a.afternoon_avail, "night": a.night_avail} for a in avail]
