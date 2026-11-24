"""
FastAPI application entry point.
Registers all routers, sets up CORS, and seeds the database on startup.
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import create_tables, SessionLocal
from app.routes import employees, departments, forecasting, scheduling, monitoring, reports


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    _seed_if_empty()
    yield
    # Shutdown (nothing to clean up for SQLite)


def _seed_if_empty() -> None:
    """Insert default departments and employees if the DB is empty."""
    db = SessionLocal()
    try:
        from app.models import Department, Employee, Alert, ModelMetric
        if db.query(Department).count() > 0:
            return  # Already seeded

        now = datetime.utcnow().isoformat()

        # Departments
        depts = [
            Department(name="Emergency",    code="ED",  rooms_capacity=18, beds_total=32, current_occupancy=28, min_staff_per_shift=4, patients_per_doctor=8.0,  patients_per_nurse=4.0,  created_at=now),
            Department(name="General Ward", code="GMW", rooms_capacity=24, beds_total=48, current_occupancy=42, min_staff_per_shift=3, patients_per_doctor=10.0, patients_per_nurse=6.0,  created_at=now),
            Department(name="ICU",          code="ICU", rooms_capacity=12, beds_total=16, current_occupancy=14, min_staff_per_shift=3, patients_per_doctor=4.0,  patients_per_nurse=2.0,  created_at=now),
            Department(name="Pediatrics",   code="PED", rooms_capacity=16, beds_total=26, current_occupancy=19, min_staff_per_shift=3, patients_per_doctor=8.0,  patients_per_nurse=5.0,  created_at=now),
        ]
        db.add_all(depts)
        db.flush()

        dept_ids = {d.name: d.id for d in depts}

        # 30 Sample employees
        import json
        employees_data = [
            ("Dr. Sarah Chen",      "sarah.chen@hospital.com",      "DOCTOR",     "Emergency",    48, ["emergency_care","trauma"]),
            ("Dr. James Okonkwo",   "james.okonkwo@hospital.com",   "DOCTOR",     "Emergency",    40, ["emergency_care"]),
            ("Dr. Priya Sharma",    "priya.sharma@hospital.com",    "DOCTOR",     "ICU",          48, ["critical_care"]),
            ("Dr. Michael Torres",  "michael.torres@hospital.com",  "DOCTOR",     "ICU",          40, ["critical_care","cardiology"]),
            ("Dr. Emma Wilson",     "emma.wilson@hospital.com",     "DOCTOR",     "General Ward", 40, ["general_medicine"]),
            ("Dr. Ravi Patel",      "ravi.patel@hospital.com",      "DOCTOR",     "General Ward", 48, ["general_medicine"]),
            ("Dr. Fatima Al-Hassan","fatima.alhassan@hospital.com", "DOCTOR",     "Pediatrics",   40, ["pediatrics"]),
            ("Dr. Lucas Mendez",    "lucas.mendez@hospital.com",    "DOCTOR",     "Pediatrics",   48, ["pediatrics"]),
            ("Nurse Alice Park",    "alice.park@hospital.com",      "NURSE",      "Emergency",    40, ["triage"]),
            ("Nurse Bob Freeman",   "bob.freeman@hospital.com",     "NURSE",      "Emergency",    40, ["emergency_care"]),
            ("Nurse Carol Singh",   "carol.singh@hospital.com",     "NURSE",      "Emergency",    40, ["trauma"]),
            ("Nurse David Lee",     "david.lee@hospital.com",       "NURSE",      "Emergency",    40, ["emergency_care"]),
            ("Nurse Elena Martinez","elena.martinez@hospital.com",  "NURSE",      "General Ward", 40, ["general_care"]),
            ("Nurse Frank Nguyen",  "frank.nguyen@hospital.com",    "NURSE",      "General Ward", 40, ["wound_care"]),
            ("Nurse Grace Kim",     "grace.kim@hospital.com",       "NURSE",      "General Ward", 40, ["general_care"]),
            ("Nurse Henry Osei",    "henry.osei@hospital.com",      "NURSE",      "General Ward", 40, ["general_care"]),
            ("Nurse Isabelle Russo","isabelle.russo@hospital.com",  "NURSE",      "ICU",          40, ["ventilator"]),
            ("Nurse Jacob Moore",   "jacob.moore@hospital.com",     "NURSE",      "ICU",          40, ["critical_care"]),
            ("Nurse Karen Liu",     "karen.liu@hospital.com",       "NURSE",      "ICU",          40, ["cardiac_monitoring"]),
            ("Nurse Leo Fernandez", "leo.fernandez@hospital.com",   "NURSE",      "ICU",          40, ["critical_care"]),
            ("Nurse Mia Thompson",  "mia.thompson@hospital.com",    "NURSE",      "Pediatrics",   40, ["pediatric_care"]),
            ("Nurse Noah Williams", "noah.williams@hospital.com",   "NURSE",      "Pediatrics",   40, ["neonatal"]),
            ("Nurse Olivia Brown",  "olivia.brown@hospital.com",    "NURSE",      "Pediatrics",   40, ["pediatric_care"]),
            ("Nurse Pedro Garcia",  "pedro.garcia@hospital.com",    "NURSE",      "Pediatrics",   40, ["pediatric_care"]),
            ("Tech Rita Nair",      "rita.nair@hospital.com",       "TECHNICIAN", "Emergency",    40, ["lab","radiology"]),
            ("Tech Sam Cho",        "sam.cho@hospital.com",         "TECHNICIAN", "General Ward", 40, ["lab","ecg"]),
            ("Tech Uma Desai",      "uma.desai@hospital.com",       "TECHNICIAN", "ICU",          40, ["ventilator_maintenance"]),
            ("Tech Victor Okafor",  "victor.okafor@hospital.com",   "TECHNICIAN", "Pediatrics",   40, ["lab"]),
            ("Admin Wendy Clarke",  "wendy.clarke@hospital.com",    "ADMIN",      "Emergency",    40, ["scheduling"]),
            ("Admin Xavier Dube",   "xavier.dube@hospital.com",     "ADMIN",      "General Ward", 40, ["records"]),
        ]

        from app.models import Employee as EmpModel
        for name, email, role, dept_name, max_hrs, quals in employees_data:
            db.add(EmpModel(
                name           = name,
                email          = email,
                role           = role,
                department_id  = dept_ids[dept_name],
                max_hours_week = max_hrs,
                qualifications = json.dumps(quals),
                created_at     = now,
            ))

        # Sample alerts
        from app.models import Alert as AlertModel
        alerts = [
            AlertModel(alert_type="SHORTAGE", severity="CRITICAL", department_id=dept_ids["Emergency"],
                       message="Emergency dept understaffed on Night shift. Needed: 4, Available: 2.", created_at=now),
            AlertModel(alert_type="SHORTAGE", severity="WARNING", department_id=dept_ids["ICU"],
                       message="ICU staffing below minimum on Afternoon shift.", created_at=now),
            AlertModel(alert_type="OVERTIME", severity="WARNING", employee_id=1, department_id=dept_ids["Emergency"],
                       message="Dr. Sarah Chen has worked 52h this week — exceeds 48h limit.", created_at=now),
            AlertModel(alert_type="BURNOUT", severity="CRITICAL", employee_id=3, department_id=dept_ids["Emergency"],
                       message="Nurse Carol Singh: Burnout risk 82/100 — 4 consecutive nights.", created_at=now),
            AlertModel(alert_type="REST_VIOLATION", severity="WARNING", employee_id=2, department_id=dept_ids["Emergency"],
                       message="Nurse Bob Freeman: Only 9h rest between Night and Morning shifts.", created_at=now),
        ]
        db.add_all(alerts)

        # Sample model metrics
        from app.models import ModelMetric
        metrics = [
            ModelMetric(model_name="LSTM",         department="emergency",    lookback=168, mae=3.21, rmse=4.83, mape=8.14, r_squared=0.907, evaluated_at=now),
            ModelMetric(model_name="GRU",          department="emergency",    lookback=168, mae=3.03, rmse=4.52, mape=7.62, r_squared=0.928, evaluated_at=now),
            ModelMetric(model_name="ARIMA",        department="emergency",    lookback=168, mae=4.78, rmse=6.21, mape=12.3, r_squared=0.820, evaluated_at=now),
            ModelMetric(model_name="SeasonalNaive",department="emergency",    lookback=168, mae=6.12, rmse=8.44, mape=16.7, r_squared=0.712, evaluated_at=now),
            ModelMetric(model_name="GRU",          department="icu",          lookback=168, mae=1.05, rmse=1.57, mape=8.64, r_squared=0.912, evaluated_at=now),
            ModelMetric(model_name="GRU",          department="general_ward", lookback=168, mae=2.31, rmse=3.42, mape=9.70, r_squared=0.901, evaluated_at=now),
        ]
        db.add_all(metrics)

        db.commit()
        print("[DB] ✓ Seeded initial data: 4 departments, 30 employees, 5 alerts, 6 model metrics")

    except Exception as e:
        db.rollback()
        print(f"[DB] Seed failed (may already exist): {e}")
    finally:
        db.close()


# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "CarePulse — Hospital Workforce Management API",
    description = "AI-powered hospital workforce management system that intelligently predicts staffing requirements based on patient volume, department workload, room capacity, and historical hospital data.",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
    lifespan    = lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = settings.cors_origins_list + ["*"],  # open in dev
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"
app.include_router(employees.router,   prefix=API_PREFIX)
app.include_router(departments.router, prefix=API_PREFIX)
app.include_router(forecasting.router, prefix=API_PREFIX)
app.include_router(scheduling.router,  prefix=API_PREFIX)
app.include_router(monitoring.router,  prefix=API_PREFIX)
app.include_router(reports.router,     prefix=API_PREFIX)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat(), "version": "1.0.0"}


@app.get("/", tags=["System"])
def root():
    return {"message": "ANNA Hospital Workforce API", "docs": "/docs"}
