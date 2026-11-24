-- ═══════════════════════════════════════════════════════════════════════
-- Seed Data — 4 Departments, 30 Employees, Shifts, Alerts, Metrics
-- ═══════════════════════════════════════════════════════════════════════

-- ── Departments ───────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO departments (id, name, min_staff_per_shift, patients_per_doctor, patients_per_nurse) VALUES
(1, 'Emergency',    4, 8.0,  4.0),
(2, 'General Ward', 3, 10.0, 6.0),
(3, 'ICU',          3, 4.0,  2.0),
(4, 'Pediatrics',   3, 8.0,  5.0);

-- ── Employees (8 Doctors, 16 Nurses, 4 Technicians, 2 Admin) ─────────────────
INSERT OR IGNORE INTO employees (id, name, email, role, department_id, max_hours_week, qualifications) VALUES
-- Doctors
(1,  'Dr. Sarah Chen',     'sarah.chen@hospital.com',     'DOCTOR', 1, 48, '["emergency_care","trauma"]'),
(2,  'Dr. James Okonkwo',  'james.okonkwo@hospital.com',  'DOCTOR', 1, 40, '["emergency_care","pediatrics"]'),
(3,  'Dr. Priya Sharma',   'priya.sharma@hospital.com',   'DOCTOR', 3, 48, '["critical_care","anesthesia"]'),
(4,  'Dr. Michael Torres', 'michael.torres@hospital.com', 'DOCTOR', 3, 40, '["critical_care","cardiology"]'),
(5,  'Dr. Emma Wilson',    'emma.wilson@hospital.com',    'DOCTOR', 2, 40, '["general_medicine"]'),
(6,  'Dr. Ravi Patel',     'ravi.patel@hospital.com',     'DOCTOR', 2, 48, '["general_medicine","geriatrics"]'),
(7,  'Dr. Fatima Al-Hassan','fatima.alhassan@hospital.com','DOCTOR',4, 40, '["pediatrics","neonatology"]'),
(8,  'Dr. Lucas Mendez',   'lucas.mendez@hospital.com',   'DOCTOR', 4, 48, '["pediatrics"]'),
-- Nurses
(9,  'Nurse Alice Park',       'alice.park@hospital.com',       'NURSE', 1, 40, '["emergency_care","triage"]'),
(10, 'Nurse Bob Freeman',      'bob.freeman@hospital.com',      'NURSE', 1, 40, '["emergency_care"]'),
(11, 'Nurse Carol Singh',      'carol.singh@hospital.com',      'NURSE', 1, 40, '["emergency_care","trauma"]'),
(12, 'Nurse David Lee',        'david.lee@hospital.com',        'NURSE', 1, 40, '["emergency_care"]'),
(13, 'Nurse Elena Martinez',   'elena.martinez@hospital.com',   'NURSE', 2, 40, '["general_care"]'),
(14, 'Nurse Frank Nguyen',     'frank.nguyen@hospital.com',     'NURSE', 2, 40, '["general_care","wound_care"]'),
(15, 'Nurse Grace Kim',        'grace.kim@hospital.com',        'NURSE', 2, 40, '["general_care"]'),
(16, 'Nurse Henry Osei',       'henry.osei@hospital.com',       'NURSE', 2, 40, '["general_care"]'),
(17, 'Nurse Isabelle Russo',   'isabelle.russo@hospital.com',   'NURSE', 3, 40, '["critical_care","ventilator"]'),
(18, 'Nurse Jacob Moore',      'jacob.moore@hospital.com',      'NURSE', 3, 40, '["critical_care"]'),
(19, 'Nurse Karen Liu',        'karen.liu@hospital.com',        'NURSE', 3, 40, '["critical_care","cardiac_monitoring"]'),
(20, 'Nurse Leo Fernandez',    'leo.fernandez@hospital.com',    'NURSE', 3, 40, '["critical_care"]'),
(21, 'Nurse Mia Thompson',     'mia.thompson@hospital.com',     'NURSE', 4, 40, '["pediatric_care"]'),
(22, 'Nurse Noah Williams',    'noah.williams@hospital.com',    'NURSE', 4, 40, '["pediatric_care","neonatal"]'),
(23, 'Nurse Olivia Brown',     'olivia.brown@hospital.com',     'NURSE', 4, 40, '["pediatric_care"]'),
(24, 'Nurse Pedro Garcia',     'pedro.garcia@hospital.com',     'NURSE', 4, 40, '["pediatric_care"]'),
-- Technicians
(25, 'Tech Rita Nair',         'rita.nair@hospital.com',        'TECHNICIAN', 1, 40, '["lab","radiology"]'),
(26, 'Tech Sam Cho',           'sam.cho@hospital.com',          'TECHNICIAN', 2, 40, '["lab","ecg"]'),
(27, 'Tech Uma Desai',         'uma.desai@hospital.com',        'TECHNICIAN', 3, 40, '["lab","ventilator_maintenance"]'),
(28, 'Tech Victor Okafor',     'victor.okafor@hospital.com',    'TECHNICIAN', 4, 40, '["lab"]'),
-- Admin
(29, 'Admin Wendy Clarke',     'wendy.clarke@hospital.com',     'ADMIN', 1, 40, '["scheduling","hr"]'),
(30, 'Admin Xavier Dube',      'xavier.dube@hospital.com',      'ADMIN', 2, 40, '["records","billing"]');

-- ── Availability (next 14 days, all available) ────────────────────────────────
-- (In production, this is inserted via the API; seed data has blanket availability)

-- ── Sample Alerts ──────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO alerts (id, alert_type, severity, employee_id, department_id, message, is_resolved) VALUES
(1, 'SHORTAGE',       'CRITICAL', NULL, 1, 'Emergency dept is understaffed on Night shift (Nov 20). Needed: 4, Available: 2.', 0),
(2, 'SHORTAGE',       'WARNING',  NULL, 3, 'ICU staffing below minimum on Afternoon shift (Nov 21). Needed: 3, Available: 2.', 0),
(3, 'OVERTIME',       'WARNING',  1,    1, 'Dr. Sarah Chen has worked 52 hours this week — exceeds 48h contractual limit.', 0),
(4, 'OVERTIME',       'WARNING',  9,    1, 'Nurse Alice Park has worked 50 hours this week.', 0),
(5, 'BURNOUT',        'CRITICAL', 11,   1, 'Nurse Carol Singh: Burnout risk score 82/100 — 4 consecutive nights + rest violation.', 0),
(6, 'REST_VIOLATION', 'WARNING',  10,   1, 'Nurse Bob Freeman: Only 9h rest between Night (Nov 18) and Morning (Nov 19) shifts.', 0),
(7, 'SHORTAGE',       'INFO',     NULL, 4, 'Pediatrics dept may face minor shortage on Weekend Morning shifts.', 0),
(8, 'SYSTEM',         'INFO',     NULL, NULL, 'Model comparison complete: GRU outperforms LSTM on Emergency dept (MAE: 3.0 vs 3.2).', 1);

-- ── Sample Model Metrics ───────────────────────────────────────────────────────
INSERT OR IGNORE INTO model_metrics (id, model_name, department, lookback, mae, rmse, mape, r_squared) VALUES
(1, 'LSTM',          'emergency', 168, 3.21, 4.83, 8.14, 0.907),
(2, 'GRU',           'emergency', 168, 3.03, 4.52, 7.62, 0.928),
(3, 'ARIMA',         'emergency', 168, 4.78, 6.21, 12.3, 0.820),
(4, 'SeasonalNaive', 'emergency', 168, 6.12, 8.44, 16.7, 0.712),
(5, 'LSTM',          'icu',       168, 1.12, 1.68, 9.21, 0.891),
(6, 'GRU',           'icu',       168, 1.05, 1.57, 8.64, 0.912),
(7, 'LSTM',          'general_ward', 168, 2.44, 3.61, 10.2, 0.883),
(8, 'GRU',           'general_ward', 168, 2.31, 3.42, 9.70, 0.901);
