"""Monitoring routes — overtime, rest violations, burnout risk, alerts."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from collections import defaultdict

from app.database import get_db
from app.models import Assignment, Employee, Shift, Alert

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

SHIFT_HOURS = 8


def _employee_hours(db: Session, week_start: Optional[str] = None) -> dict[int, float]:
    """Compute weekly hours per employee from assignments."""
    q = db.query(Assignment, Shift).join(Shift, Assignment.shift_id == Shift.id)
    if week_start:
        q = q.filter(Shift.shift_date >= week_start)
    rows = q.all()
    hours: dict[int, float] = defaultdict(float)
    for a, _ in rows:
        hours[a.employee_id] += SHIFT_HOURS
    return hours


@router.get("/overtime")
def get_overtime(threshold: int = 48, db: Session = Depends(get_db)):
    hours = _employee_hours(db)
    result = []
    for emp_id, hrs in hours.items():
        if hrs > threshold:
            emp = db.query(Employee).filter(Employee.id == emp_id).first()
            result.append({
                "employee_id":   emp_id,
                "employee_name": emp.name if emp else f"Emp#{emp_id}",
                "role":          emp.role if emp else "UNKNOWN",
                "department":    emp.department.name if emp and emp.department else None,
                "weekly_hours":  hrs,
                "excess_hours":  hrs - threshold,
                "threshold":     threshold,
            })
    return sorted(result, key=lambda x: x["excess_hours"], reverse=True)


@router.get("/rest-violations")
def get_rest_violations(min_rest_hours: int = 11, db: Session = Depends(get_db)):
    """Find employee/shift pairs with insufficient rest gap."""
    SHIFT_START = {"MORNING": 6, "AFTERNOON": 14, "NIGHT": 22}

    # Group shifts by employee
    rows = db.query(Assignment, Shift).join(Shift, Assignment.shift_id == Shift.id).all()
    emp_shifts: dict[int, list] = defaultdict(list)
    for a, sh in rows:
        emp_shifts[a.employee_id].append(sh)

    violations = []
    for emp_id, shifts in emp_shifts.items():
        shifts_sorted = sorted(shifts, key=lambda s: (s.shift_date, SHIFT_START.get(s.shift_type, 0)))
        for i in range(len(shifts_sorted) - 1):
            s1 = shifts_sorted[i]
            s2 = shifts_sorted[i + 1]
            from datetime import datetime as dt
            d1 = dt.strptime(s1.shift_date, "%Y-%m-%d")
            d2 = dt.strptime(s2.shift_date, "%Y-%m-%d")
            h1 = d1.toordinal() * 24 + SHIFT_START.get(s1.shift_type, 0) + SHIFT_HOURS
            h2 = d2.toordinal() * 24 + SHIFT_START.get(s2.shift_type, 0)
            gap = h2 - h1
            if gap < min_rest_hours:
                emp = db.query(Employee).filter(Employee.id == emp_id).first()
                violations.append({
                    "employee_id":   emp_id,
                    "employee_name": emp.name if emp else f"Emp#{emp_id}",
                    "shift_1":       {"date": s1.shift_date, "type": s1.shift_type},
                    "shift_2":       {"date": s2.shift_date, "type": s2.shift_type},
                    "rest_hours":    gap,
                    "required_hours": min_rest_hours,
                })
    return violations


@router.get("/burnout-risk")
def get_burnout_risk(db: Session = Depends(get_db)):
    hours  = _employee_hours(db)
    # Night shifts per employee
    rows = db.query(Assignment, Shift).join(Shift, Assignment.shift_id == Shift.id).all()
    nights: dict[int, int] = defaultdict(int)
    days:   dict[int, set] = defaultdict(set)
    for a, sh in rows:
        if sh.shift_type == "NIGHT":
            nights[a.employee_id] += 1
        days[a.employee_id].add(sh.shift_date)

    employees = db.query(Employee).filter(Employee.is_active == True).all()
    result = []
    for emp in employees:
        hrs    = hours.get(emp.id, 0.0)
        nshifts = nights.get(emp.id, 0)
        consec  = len(days.get(emp.id, set()))

        hrs_score   = min(40.0, (hrs / 48) * 40)
        night_score = min(20.0, nshifts * 5)
        day_score   = min(25.0, consec * 4)
        total       = hrs_score + night_score + day_score

        level = "LOW" if total < 33 else "MEDIUM" if total < 55 else "HIGH" if total < 75 else "CRITICAL"
        result.append({
            "employee_id":   emp.id,
            "employee_name": emp.name,
            "role":          emp.role,
            "department":    emp.department.name if emp.department else None,
            "burnout_score": round(total, 1),
            "risk_level":    level,
            "weekly_hours":  hrs,
            "night_shifts":  nshifts,
            "days_worked":   consec,
        })

    return sorted(result, key=lambda x: x["burnout_score"], reverse=True)


@router.get("/alerts")
def get_alerts(
    alert_type: Optional[str] = None,
    severity:   Optional[str] = None,
    is_resolved: Optional[bool] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Alert)
    if alert_type:
        q = q.filter(Alert.alert_type == alert_type.upper())
    if severity:
        q = q.filter(Alert.severity == severity.upper())
    if is_resolved is not None:
        q = q.filter(Alert.is_resolved == is_resolved)
    total = q.count()
    items = q.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "data": [{
            "id": a.id, "type": a.alert_type, "severity": a.severity,
            "employee_id": a.employee_id, "department_id": a.department_id,
            "message": a.message, "is_resolved": a.is_resolved,
            "created_at": a.created_at,
        } for a in items],
    }


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(404, "Alert not found")
    a.is_resolved = True
    a.resolved_at = datetime.utcnow().isoformat()
    db.commit()
    return {"message": f"Alert {alert_id} resolved"}
