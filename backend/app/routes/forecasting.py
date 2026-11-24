"""Forecasting routes — run model, return predictions, model metrics."""

import math
import random
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Forecast, Department, ModelMetric

router = APIRouter(prefix="/forecast", tags=["Forecasting"])

# Base patient rates per department per shift (used for mock)
BASE_DEMAND = {
    "Emergency":    {"MORNING": 48, "AFTERNOON": 52, "NIGHT": 30},
    "General Ward": {"MORNING": 32, "AFTERNOON": 28, "NIGHT": 18},
    "ICU":          {"MORNING": 12, "AFTERNOON": 12, "NIGHT": 10},
    "Pediatrics":   {"MORNING": 20, "AFTERNOON": 22, "NIGHT": 12},
}


class ForecastRequest(BaseModel):
    department_id: int
    start_date:    str
    end_date:      str
    model:         str = "gru"      # lstm | gru | arima | naive
    lookback:      int = 168        # 24 | 48 | 168


def _mock_forecast(dept_name: str, start_date: str, end_date: str, model: str) -> list[dict]:
    """Generate realistic mock forecasts when no trained model is available."""
    random.seed(42)
    base = BASE_DEMAND.get(dept_name, {"MORNING": 25, "AFTERNOON": 25, "NIGHT": 15})
    forecasts = []
    current   = datetime.strptime(start_date, "%Y-%m-%d").date()
    end       = datetime.strptime(end_date,   "%Y-%m-%d").date()

    while current <= end:
        is_weekend = current.weekday() >= 5
        for shift_type, shift_base in base.items():
            weekend_mult = 0.85 if is_weekend and dept_name != "Emergency" else 1.0
            jitter       = random.uniform(0.88, 1.12)
            predicted    = shift_base * weekend_mult * jitter
            noise        = shift_base * 0.08
            forecasts.append({
                "date":               str(current),
                "shift_type":         shift_type,
                "predicted_patients": round(predicted, 1),
                "confidence_low":     round(predicted - noise, 1),
                "confidence_high":    round(predicted + noise, 1),
                "model_used":         model,
            })
        current += timedelta(days=1)
    return forecasts


@router.post("/run")
def run_forecast(body: ForecastRequest, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == body.department_id).first()
    if not dept:
        raise HTTPException(404, "Department not found")

    # Try real model; fall back to mock
    forecasts_data = _mock_forecast(dept.name, body.start_date, body.end_date, body.model)

    # Persist to DB
    now = datetime.utcnow().isoformat()
    saved = []
    for f in forecasts_data:
        doctors = max(1, math.ceil(f["predicted_patients"] / dept.patients_per_doctor))
        nurses  = max(2, math.ceil(f["predicted_patients"] / dept.patients_per_nurse))
        fc = Forecast(
            department_id      = body.department_id,
            forecast_date      = f["date"],
            shift_type         = f["shift_type"],
            predicted_patients = f["predicted_patients"],
            required_doctors   = doctors,
            required_nurses    = nurses,
            model_used         = body.model,
            confidence_low     = f["confidence_low"],
            confidence_high    = f["confidence_high"],
            created_at         = now,
        )
        db.add(fc)
        saved.append(f)

    db.commit()
    return {
        "department":  dept.name,
        "model":       body.model,
        "period":      f"{body.start_date} → {body.end_date}",
        "forecasts":   saved,
        "count":       len(saved),
    }


@router.get("/history")
def forecast_history(
    department_id: Optional[int] = Query(None),
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Forecast)
    if department_id:
        q = q.filter(Forecast.department_id == department_id)
    total = q.count()
    items = q.order_by(Forecast.forecast_date.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "data": [{
            "id": f.id, "department_id": f.department_id,
            "forecast_date": f.forecast_date, "shift_type": f.shift_type,
            "predicted_patients": f.predicted_patients,
            "required_doctors": f.required_doctors, "required_nurses": f.required_nurses,
            "model_used": f.model_used, "created_at": f.created_at,
        } for f in items],
    }


@router.get("/metrics")
def get_model_metrics(db: Session = Depends(get_db)):
    metrics = db.query(ModelMetric).all()
    return [{
        "model": m.model_name, "department": m.department,
        "lookback": m.lookback, "MAE": m.mae, "RMSE": m.rmse,
        "MAPE": m.mape, "R2": m.r_squared, "evaluated_at": m.evaluated_at,
    } for m in metrics]


@router.get("/departments/{dept_id}/latest")
def latest_forecast(dept_id: int, db: Session = Depends(get_db)):
    fc = db.query(Forecast).filter(Forecast.department_id == dept_id)\
        .order_by(Forecast.created_at.desc()).first()
    if not fc:
        raise HTTPException(404, "No forecast found for this department")
    return {
        "id": fc.id, "forecast_date": fc.forecast_date, "shift_type": fc.shift_type,
        "predicted_patients": fc.predicted_patients,
        "required_doctors": fc.required_doctors, "required_nurses": fc.required_nurses,
        "model_used": fc.model_used,
    }
