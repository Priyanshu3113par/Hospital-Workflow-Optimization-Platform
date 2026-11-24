-- ═══════════════════════════════════════════════════════════════════════
-- Hospital Workforce Optimization — Database Schema
-- Compatible with both SQLite (dev) and PostgreSQL (prod)
-- ═══════════════════════════════════════════════════════════════════════

-- ── Departments ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT NOT NULL UNIQUE,
    code                 TEXT NOT NULL DEFAULT 'WARD',
    rooms_capacity       INTEGER NOT NULL DEFAULT 15,
    beds_total           INTEGER NOT NULL DEFAULT 25,
    current_occupancy    INTEGER NOT NULL DEFAULT 18,
    min_staff_per_shift  INTEGER NOT NULL DEFAULT 3,
    patients_per_doctor  REAL    NOT NULL DEFAULT 8.0,
    patients_per_nurse   REAL    NOT NULL DEFAULT 4.0,
    is_active            INTEGER NOT NULL DEFAULT 1,
    created_at           TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ── Employees ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS employees (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL,
    email            TEXT    UNIQUE,
    role             TEXT    NOT NULL CHECK (role IN ('DOCTOR','NURSE','TECHNICIAN','ADMIN')),
    department_id    INTEGER REFERENCES departments(id),
    max_hours_week   INTEGER NOT NULL DEFAULT 40,
    qualifications   TEXT    NOT NULL DEFAULT '[]',   -- JSON array
    is_active        INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_role ON employees(role);

-- ── Availability ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS availability (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id      INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    avail_date       TEXT    NOT NULL,     -- ISO date YYYY-MM-DD
    morning_avail    INTEGER NOT NULL DEFAULT 1,
    afternoon_avail  INTEGER NOT NULL DEFAULT 1,
    night_avail      INTEGER NOT NULL DEFAULT 1,
    UNIQUE(employee_id, avail_date)
);
CREATE INDEX IF NOT EXISTS idx_avail_emp  ON availability(employee_id);
CREATE INDEX IF NOT EXISTS idx_avail_date ON availability(avail_date);

-- ── Shifts ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shifts (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_date       TEXT    NOT NULL,     -- ISO date
    department_id    INTEGER NOT NULL REFERENCES departments(id),
    shift_type       TEXT    NOT NULL CHECK (shift_type IN ('MORNING','AFTERNOON','NIGHT')),
    required_staff   INTEGER NOT NULL DEFAULT 3,
    min_qualified    INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_shifts_date ON shifts(shift_date);
CREATE INDEX IF NOT EXISTS idx_shifts_dept ON shifts(department_id);

-- ── Assignments ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS assignments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_id         INTEGER NOT NULL REFERENCES shifts(id) ON DELETE CASCADE,
    employee_id      INTEGER NOT NULL REFERENCES employees(id),
    is_overtime      INTEGER NOT NULL DEFAULT 0,
    workload_score   REAL    NOT NULL DEFAULT 0.0,
    assigned_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(shift_id, employee_id)
);
CREATE INDEX IF NOT EXISTS idx_assignments_shift ON assignments(shift_id);
CREATE INDEX IF NOT EXISTS idx_assignments_emp   ON assignments(employee_id);

-- ── Forecasts ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS forecasts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id       INTEGER NOT NULL REFERENCES departments(id),
    forecast_date       TEXT    NOT NULL,
    shift_type          TEXT    NOT NULL CHECK (shift_type IN ('MORNING','AFTERNOON','NIGHT')),
    predicted_patients  REAL    NOT NULL,
    required_doctors    INTEGER NOT NULL DEFAULT 1,
    required_nurses     INTEGER NOT NULL DEFAULT 2,
    model_used          TEXT    NOT NULL DEFAULT 'gru',
    confidence_low      REAL,
    confidence_high     REAL,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_forecasts_dept ON forecasts(department_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_date ON forecasts(forecast_date);

-- ── Alerts ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alerts (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type       TEXT    NOT NULL CHECK (alert_type IN ('SHORTAGE','OVERTIME','BURNOUT','REST_VIOLATION','SYSTEM')),
    severity         TEXT    NOT NULL CHECK (severity IN ('INFO','WARNING','CRITICAL')),
    employee_id      INTEGER REFERENCES employees(id),
    department_id    INTEGER REFERENCES departments(id),
    message          TEXT    NOT NULL,
    is_resolved      INTEGER NOT NULL DEFAULT 0,
    resolved_at      TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_alerts_type     ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(is_resolved);

-- ── Model Metrics ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS model_metrics (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name   TEXT    NOT NULL,
    department   TEXT    NOT NULL,
    lookback     INTEGER NOT NULL,
    mae          REAL,
    rmse         REAL,
    mape         REAL,
    r_squared    REAL,
    evaluated_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
