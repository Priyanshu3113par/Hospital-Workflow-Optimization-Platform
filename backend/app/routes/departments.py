"""Department routes — CRUD + staffing status."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Department, Employee, Assignment, Shift

router = APIRouter(prefix="/departments", tags=["Departments"])


class DepartmentCreate(BaseModel):
    name: str
    code: str = "WARD"
    rooms_capacity: int = 15
    beds_total: int = 25
    current_occupancy: int = 18
    min_staff_per_shift: int = 3
    patients_per_doctor: float = 8.0
    patients_per_nurse: float  = 4.0


class DepartmentUpdate(BaseModel):
    name: Optional[str]            = None
    code: Optional[str]            = None
    rooms_capacity: Optional[int]  = None
    beds_total: Optional[int]      = None
    current_occupancy: Optional[int] = None
    min_staff_per_shift: Optional[int]   = None
    patients_per_doctor: Optional[float] = None
    patients_per_nurse:  Optional[float] = None
    is_active: Optional[bool] = None


def _serialize(d: Department) -> dict:
    return {
        "id": d.id, "name": d.name,
        "code": getattr(d, "code", "WARD"),
        "rooms_capacity": getattr(d, "rooms_capacity", 15),
        "beds_total": getattr(d, "beds_total", 25),
        "current_occupancy": getattr(d, "current_occupancy", 18),
        "min_staff_per_shift": d.min_staff_per_shift,
        "patients_per_doctor": d.patients_per_doctor,
        "patients_per_nurse":  d.patients_per_nurse,
        "is_active": d.is_active,
        "employee_count": len([e for e in d.employees if e.is_active]),
    }


@router.get("/")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).filter(Department.is_active == True).all()
    return {"total": len(depts), "data": [_serialize(d) for d in depts]}


@router.get("/{dept_id}")
def get_department(dept_id: int, db: Session = Depends(get_db)):
    d = db.query(Department).filter(Department.id == dept_id).first()
    if not d:
        raise HTTPException(404, "Department not found")
    return _serialize(d)


@router.post("/", status_code=201)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db)):
    dept = Department(**body.model_dump(), created_at=datetime.utcnow().isoformat())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return _serialize(dept)


@router.put("/{dept_id}")
def update_department(dept_id: int, body: DepartmentUpdate, db: Session = Depends(get_db)):
    d = db.query(Department).filter(Department.id == dept_id).first()
    if not d:
        raise HTTPException(404, "Department not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(d, k, v)
    db.commit()
    db.refresh(d)
    return _serialize(d)


@router.delete("/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    d = db.query(Department).filter(Department.id == dept_id).first()
    if not d:
        raise HTTPException(404, "Department not found")
    d.is_active = False
    db.commit()
    return {"message": f"Department {dept_id} deactivated"}


@router.get("/{dept_id}/staffing-status")
def staffing_status(dept_id: int, db: Session = Depends(get_db)):
    d = db.query(Department).filter(Department.id == dept_id).first()
    if not d:
        raise HTTPException(404, "Department not found")
    active_staff = db.query(Employee).filter(
        Employee.department_id == dept_id,
        Employee.is_active == True,
    ).count()
    return {
        "department_id":    dept_id,
        "department_name":  d.name,
        "min_staff_needed": d.min_staff_per_shift * 3,  # 3 shifts/day
        "active_staff":     active_staff,
        "is_understaffed":  active_staff < d.min_staff_per_shift * 3,
    }
