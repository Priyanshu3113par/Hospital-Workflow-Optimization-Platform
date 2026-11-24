"""SQLAlchemy ORM models for all database entities."""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id                   = Column(Integer, primary_key=True, index=True)
    name                 = Column(String, unique=True, nullable=False)
    code                 = Column(String, default="WARD")
    rooms_capacity       = Column(Integer, default=15)
    beds_total           = Column(Integer, default=25)
    current_occupancy    = Column(Integer, default=18)
    min_staff_per_shift  = Column(Integer, default=3)
    patients_per_doctor  = Column(Float,   default=8.0)
    patients_per_nurse   = Column(Float,   default=4.0)
    is_active            = Column(Boolean, default=True)
    created_at           = Column(String)

    employees    = relationship("Employee",   back_populates="department")
    shifts       = relationship("Shift",      back_populates="department")
    forecasts    = relationship("Forecast",   back_populates="department")
    alerts       = relationship("Alert",      back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String,  nullable=False)
    email           = Column(String,  unique=True)
    role            = Column(String,  nullable=False)   # DOCTOR|NURSE|TECHNICIAN|ADMIN
    department_id   = Column(Integer, ForeignKey("departments.id"))
    max_hours_week  = Column(Integer, default=40)
    qualifications  = Column(Text,    default="[]")     # JSON string
    is_active       = Column(Boolean, default=True)
    created_at      = Column(String)

    department   = relationship("Department", back_populates="employees")
    assignments  = relationship("Assignment", back_populates="employee")
    availability = relationship("Availability", back_populates="employee", cascade="all, delete-orphan")
    alerts       = relationship("Alert", back_populates="employee")


class Availability(Base):
    __tablename__ = "availability"

    id              = Column(Integer, primary_key=True, index=True)
    employee_id     = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    avail_date      = Column(String,  nullable=False)
    morning_avail   = Column(Boolean, default=True)
    afternoon_avail = Column(Boolean, default=True)
    night_avail     = Column(Boolean, default=True)

    employee = relationship("Employee", back_populates="availability")


class Shift(Base):
    __tablename__ = "shifts"

    id              = Column(Integer, primary_key=True, index=True)
    shift_date      = Column(String,  nullable=False)
    department_id   = Column(Integer, ForeignKey("departments.id"), nullable=False)
    shift_type      = Column(String,  nullable=False)   # MORNING|AFTERNOON|NIGHT
    required_staff  = Column(Integer, default=3)
    min_qualified   = Column(Integer, default=1)
    created_at      = Column(String)

    department  = relationship("Department", back_populates="shifts")
    assignments = relationship("Assignment",  back_populates="shift", cascade="all, delete-orphan")


class Assignment(Base):
    __tablename__ = "assignments"

    id             = Column(Integer, primary_key=True, index=True)
    shift_id       = Column(Integer, ForeignKey("shifts.id",    ondelete="CASCADE"), nullable=False)
    employee_id    = Column(Integer, ForeignKey("employees.id"), nullable=False)
    is_overtime    = Column(Boolean, default=False)
    workload_score = Column(Float,   default=0.0)
    assigned_at    = Column(String)

    shift    = relationship("Shift",    back_populates="assignments")
    employee = relationship("Employee", back_populates="assignments")


class Forecast(Base):
    __tablename__ = "forecasts"

    id                 = Column(Integer, primary_key=True, index=True)
    department_id      = Column(Integer, ForeignKey("departments.id"), nullable=False)
    forecast_date      = Column(String,  nullable=False)
    shift_type         = Column(String,  nullable=False)
    predicted_patients = Column(Float,   nullable=False)
    required_doctors   = Column(Integer, default=1)
    required_nurses    = Column(Integer, default=2)
    model_used         = Column(String,  default="gru")
    confidence_low     = Column(Float)
    confidence_high    = Column(Float)
    created_at         = Column(String)

    department = relationship("Department", back_populates="forecasts")


class Alert(Base):
    __tablename__ = "alerts"

    id            = Column(Integer, primary_key=True, index=True)
    alert_type    = Column(String,  nullable=False)
    severity      = Column(String,  nullable=False)
    employee_id   = Column(Integer, ForeignKey("employees.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    message       = Column(Text,    nullable=False)
    is_resolved   = Column(Boolean, default=False)
    resolved_at   = Column(String)
    created_at    = Column(String)

    employee   = relationship("Employee",   back_populates="alerts")
    department = relationship("Department", back_populates="alerts")


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id           = Column(Integer, primary_key=True, index=True)
    model_name   = Column(String, nullable=False)
    department   = Column(String, nullable=False)
    lookback     = Column(Integer, nullable=False)
    mae          = Column(Float)
    rmse         = Column(Float)
    mape         = Column(Float)
    r_squared    = Column(Float)
    evaluated_at = Column(String)
