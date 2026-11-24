"""Scheduling routes — generate and retrieve shift rosters."""

import random
from datetime import datetime, timedelta, date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Shift, Assignment, Employee, Department, Forecast, Alert

router = APIRouter(prefix="/schedule", tags=["Scheduling"])


class GenerateRequest(BaseModel):
    week_start_date: str           # ISO date YYYY-MM-DD (Monday)
    department_ids:  list[int] = []  # empty = all departments


def _greedy_assign(shifts, employees, db):
    """Simple greedy scheduler — assigns least-loaded eligible employee to each shift."""
    assignments = []
    emp_hours: dict[int, int] = {e.id: 0 for e in employees}
    emp_days:  dict[int, set] = {e.id: set() for e in employees}

    for sh in sorted(shifts, key=lambda s: (s.shift_date, s.shift_type)):
        eligible = [
            e for e in employees
            if e.department_id == sh.department_id
            and e.is_active
            and sh.shift_date not in emp_days[e.id]
            and emp_hours[e.id] + 8 <= e.max_hours_week
        ]
        eligible.sort(key=lambda e: emp_hours[e.id])  # least loaded first

        assigned = 0
        for emp in eligible[:sh.required_staff]:
            is_ot = emp_hours[emp.id] + 8 > 40
            assignments.append(Assignment(
                shift_id       = sh.id,
                employee_id    = emp.id,
                is_overtime    = is_ot,
                workload_score = round(emp_hours[emp.id] / max(emp.max_hours_week, 1), 3),
                assigned_at    = datetime.utcnow().isoformat(),
            ))
            emp_hours[emp.id] += 8
            emp_days[emp.id].add(sh.shift_date)
            assigned += 1

        # Raise shortage alert if understaffed
        if assigned < sh.required_staff:
            db.add(Alert(
                alert_type    = "SHORTAGE",
                severity      = "CRITICAL" if sh.required_staff - assigned > 1 else "WARNING",
                department_id = sh.department_id,
                message       = (f"Shift shortage on {sh.shift_date} ({sh.shift_type}): "
                                 f"needed {sh.required_staff}, assigned {assigned}."),
                created_at    = datetime.utcnow().isoformat(),
            ))

    return assignments


@router.post("/generate")
def generate_schedule(body: GenerateRequest, db: Session = Depends(get_db)):
    start = datetime.strptime(body.week_start_date, "%Y-%m-%d").date()
    end   = start + timedelta(days=6)

    dept_q = db.query(Department).filter(Department.is_active == True)
    if body.department_ids:
        dept_q = dept_q.filter(Department.id.in_(body.department_ids))
    departments = dept_q.all()
    if not departments:
        raise HTTPException(400, "No departments found")

    employees = db.query(Employee).filter(Employee.is_active == True).all()

    # Create shift records for the week
    shift_types  = ["MORNING", "AFTERNOON", "NIGHT"]
    created_shifts = []
    now = datetime.utcnow().isoformat()

    for dept in departments:
        for day_offset in range(7):
            d = start + timedelta(days=day_offset)
            # Get forecast if available
            for stype in shift_types:
                fc = db.query(Forecast).filter(
                    Forecast.department_id == dept.id,
                    Forecast.forecast_date == str(d),
                    Forecast.shift_type    == stype,
                ).first()

                if fc:
                    req_staff = fc.required_doctors + fc.required_nurses
                else:
                    req_staff = dept.min_staff_per_shift

                # Check if shift already exists
                existing = db.query(Shift).filter(
                    Shift.department_id == dept.id,
                    Shift.shift_date    == str(d),
                    Shift.shift_type    == stype,
                ).first()

                if existing:
                    created_shifts.append(existing)
                else:
                    sh = Shift(
                        shift_date     = str(d),
                        department_id  = dept.id,
                        shift_type     = stype,
                        required_staff = req_staff,
                        min_qualified  = max(1, req_staff // 3),
                        created_at     = now,
                    )
                    db.add(sh)
                    db.flush()
                    created_shifts.append(sh)

    # Clear old assignments for this week's shifts
    for sh in created_shifts:
        db.query(Assignment).filter(Assignment.shift_id == sh.id).delete()

    # Greedy assignment
    assignments = _greedy_assign(created_shifts, employees, db)
    db.add_all(assignments)
    db.commit()

    return {
        "week":        f"{start} → {end}",
        "shifts":      len(created_shifts),
        "assignments": len(assignments),
        "departments": len(departments),
        "message":     "Schedule generated successfully",
    }


@router.get("/{week_start_date}")
def get_schedule(week_start_date: str, db: Session = Depends(get_db)):
    start = datetime.strptime(week_start_date, "%Y-%m-%d").date()
    end   = start + timedelta(days=6)

    shifts = db.query(Shift).filter(
        Shift.shift_date >= str(start),
        Shift.shift_date <= str(end),
    ).all()

    result = []
    for sh in shifts:
        assigned = db.query(Assignment).filter(Assignment.shift_id == sh.id).all()
        result.append({
            "shift_id":      sh.id,
            "date":          sh.shift_date,
            "shift_type":    sh.shift_type,
            "department_id": sh.department_id,
            "department":    sh.department.name if sh.department else None,
            "required":      sh.required_staff,
            "assigned":      len(assigned),
            "coverage_pct":  round(len(assigned) / sh.required_staff * 100, 1) if sh.required_staff else 0,
            "employees": [{
                "id":   a.employee_id,
                "name": a.employee.name  if a.employee else None,
                "role": a.employee.role  if a.employee else None,
                "is_overtime": a.is_overtime,
            } for a in assigned],
        })

    return {"week": f"{start} → {end}", "shifts": result}


@router.put("/assignments/{assignment_id}")
def update_assignment(assignment_id: int, employee_id: int, db: Session = Depends(get_db)):
    a = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not a:
        raise HTTPException(404, "Assignment not found")
    a.employee_id = employee_id
    db.commit()
    return {"message": "Assignment updated"}


@router.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    a = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not a:
        raise HTTPException(404, "Assignment not found")
    db.delete(a)
    db.commit()
    return {"message": "Assignment removed"}
