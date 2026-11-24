"""Reports routes — weekly summaries and CSV exports."""

import csv
import io
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Assignment, Shift, Alert, ModelMetric, Department

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary")
def weekly_summary(db: Session = Depends(get_db)):
    total_shifts = db.query(Shift).count()
    total_assignments = db.query(Assignment).count()
    active_alerts = db.query(Alert).filter(Alert.is_resolved == False).count()

    # Coverage
    shifts = db.query(Shift).all()
    fully_covered = sum(1 for s in shifts if
        db.query(Assignment).filter(Assignment.shift_id == s.id).count() >= s.required_staff)
    coverage_pct = round(fully_covered / total_shifts * 100, 1) if total_shifts else 0

    # Overtime count
    from collections import defaultdict
    rows = db.query(Assignment).all()
    emp_hours: dict[int, int] = defaultdict(int)
    for a in rows:
        emp_hours[a.employee_id] += 8
    overtime_count = sum(1 for h in emp_hours.values() if h > 48)

    return {
        "total_shifts":       total_shifts,
        "total_assignments":  total_assignments,
        "coverage_pct":       coverage_pct,
        "fully_covered":      fully_covered,
        "understaffed":       total_shifts - fully_covered,
        "active_alerts":      active_alerts,
        "overtime_employees": overtime_count,
        "generated_at":       datetime.utcnow().isoformat(),
    }


@router.get("/schedule-export")
def export_schedule(db: Session = Depends(get_db)):
    """Download current schedule as CSV."""
    shifts = db.query(Shift).order_by(Shift.shift_date, Shift.shift_type).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Department", "Shift", "Required", "Assigned", "Coverage%", "Employees"])

    for sh in shifts:
        assigned = db.query(Assignment).filter(Assignment.shift_id == sh.id).all()
        emp_names = "; ".join(a.employee.name for a in assigned if a.employee)
        coverage  = round(len(assigned) / sh.required_staff * 100, 1) if sh.required_staff else 0
        writer.writerow([
            sh.shift_date,
            sh.department.name if sh.department else sh.department_id,
            sh.shift_type,
            sh.required_staff,
            len(assigned),
            f"{coverage}%",
            emp_names,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=schedule_export.csv"},
    )


@router.get("/model-comparison")
def export_model_comparison(db: Session = Depends(get_db)):
    """Download model metrics comparison as CSV."""
    metrics = db.query(ModelMetric).order_by(ModelMetric.department, ModelMetric.mae).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Model", "Department", "Lookback(h)", "MAE", "RMSE", "MAPE%", "R²"])
    for m in metrics:
        writer.writerow([m.model_name, m.department, m.lookback, m.mae, m.rmse, m.mape, m.r_squared])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=model_comparison.csv"},
    )
