// ── Comprehensive mock data for all pages ─────────────────────────────────────

export const mockDepartments = [
  { id: 1, name: 'Emergency',    min_staff_per_shift: 4, patients_per_doctor: 8,  patients_per_nurse: 4,  employee_count: 9,  status: 'at-risk'  },
  { id: 2, name: 'General Ward', min_staff_per_shift: 3, patients_per_doctor: 10, patients_per_nurse: 6,  employee_count: 8,  status: 'healthy'  },
  { id: 3, name: 'ICU',          min_staff_per_shift: 3, patients_per_doctor: 4,  patients_per_nurse: 2,  employee_count: 6,  status: 'critical' },
  { id: 4, name: 'Pediatrics',   min_staff_per_shift: 3, patients_per_doctor: 8,  patients_per_nurse: 5,  employee_count: 7,  status: 'healthy'  },
]

export const mockEmployees = [
  { id: 1,  name: 'Dr. Sarah Chen',       email: 'sarah.chen@hospital.com',      role: 'DOCTOR',     department_id: 1, department_name: 'Emergency',    max_hours_week: 48, qualifications: ['emergency_care','trauma'],      is_active: true  },
  { id: 2,  name: 'Dr. James Okonkwo',    email: 'james.okonkwo@hospital.com',   role: 'DOCTOR',     department_id: 1, department_name: 'Emergency',    max_hours_week: 40, qualifications: ['emergency_care'],               is_active: true  },
  { id: 3,  name: 'Dr. Priya Sharma',     email: 'priya.sharma@hospital.com',    role: 'DOCTOR',     department_id: 3, department_name: 'ICU',          max_hours_week: 48, qualifications: ['critical_care','anesthesia'],   is_active: true  },
  { id: 4,  name: 'Dr. Michael Torres',   email: 'michael.torres@hospital.com',  role: 'DOCTOR',     department_id: 3, department_name: 'ICU',          max_hours_week: 40, qualifications: ['critical_care','cardiology'],   is_active: true  },
  { id: 5,  name: 'Dr. Emma Wilson',      email: 'emma.wilson@hospital.com',     role: 'DOCTOR',     department_id: 2, department_name: 'General Ward', max_hours_week: 40, qualifications: ['general_medicine'],             is_active: true  },
  { id: 6,  name: 'Dr. Ravi Patel',       email: 'ravi.patel@hospital.com',      role: 'DOCTOR',     department_id: 2, department_name: 'General Ward', max_hours_week: 48, qualifications: ['general_medicine','geriatrics'], is_active: true  },
  { id: 7,  name: 'Dr. Fatima Al-Hassan', email: 'fatima.alhassan@hospital.com', role: 'DOCTOR',     department_id: 4, department_name: 'Pediatrics',   max_hours_week: 40, qualifications: ['pediatrics','neonatology'],     is_active: true  },
  { id: 8,  name: 'Dr. Lucas Mendez',     email: 'lucas.mendez@hospital.com',    role: 'DOCTOR',     department_id: 4, department_name: 'Pediatrics',   max_hours_week: 48, qualifications: ['pediatrics'],                   is_active: true  },
  { id: 9,  name: 'Nurse Alice Park',     email: 'alice.park@hospital.com',      role: 'NURSE',      department_id: 1, department_name: 'Emergency',    max_hours_week: 40, qualifications: ['emergency_care','triage'],      is_active: true  },
  { id: 10, name: 'Nurse Bob Freeman',    email: 'bob.freeman@hospital.com',     role: 'NURSE',      department_id: 1, department_name: 'Emergency',    max_hours_week: 40, qualifications: ['emergency_care'],               is_active: true  },
  { id: 11, name: 'Nurse Carol Singh',    email: 'carol.singh@hospital.com',     role: 'NURSE',      department_id: 1, department_name: 'Emergency',    max_hours_week: 40, qualifications: ['emergency_care','trauma'],      is_active: true  },
  { id: 12, name: 'Nurse David Lee',      email: 'david.lee@hospital.com',       role: 'NURSE',      department_id: 1, department_name: 'Emergency',    max_hours_week: 40, qualifications: ['emergency_care'],               is_active: true  },
  { id: 13, name: 'Nurse Elena Martinez', email: 'elena.martinez@hospital.com',  role: 'NURSE',      department_id: 2, department_name: 'General Ward', max_hours_week: 40, qualifications: ['general_care'],                 is_active: true  },
  { id: 14, name: 'Nurse Frank Nguyen',   email: 'frank.nguyen@hospital.com',    role: 'NURSE',      department_id: 2, department_name: 'General Ward', max_hours_week: 40, qualifications: ['general_care','wound_care'],    is_active: true  },
  { id: 15, name: 'Nurse Grace Kim',      email: 'grace.kim@hospital.com',       role: 'NURSE',      department_id: 2, department_name: 'General Ward', max_hours_week: 40, qualifications: ['general_care'],                 is_active: true  },
  { id: 16, name: 'Nurse Henry Osei',     email: 'henry.osei@hospital.com',      role: 'NURSE',      department_id: 2, department_name: 'General Ward', max_hours_week: 40, qualifications: ['general_care'],                 is_active: true  },
  { id: 17, name: 'Nurse Isabelle Russo', email: 'isabelle.russo@hospital.com',  role: 'NURSE',      department_id: 3, department_name: 'ICU',          max_hours_week: 40, qualifications: ['critical_care','ventilator'],   is_active: true  },
  { id: 18, name: 'Nurse Jacob Moore',    email: 'jacob.moore@hospital.com',     role: 'NURSE',      department_id: 3, department_name: 'ICU',          max_hours_week: 40, qualifications: ['critical_care'],                is_active: true  },
  { id: 25, name: 'Tech Rita Nair',       email: 'rita.nair@hospital.com',       role: 'TECHNICIAN', department_id: 1, department_name: 'Emergency',    max_hours_week: 40, qualifications: ['lab','radiology'],              is_active: true  },
  { id: 29, name: 'Admin Wendy Clarke',   email: 'wendy.clarke@hospital.com',    role: 'ADMIN',      department_id: 1, department_name: 'Emergency',    max_hours_week: 40, qualifications: ['scheduling','hr'],              is_active: true  },
]

export const mockAlerts = [
  { id: 1, type: 'SHORTAGE',       severity: 'CRITICAL', message: 'Emergency: Night shift understaffed. Need 4, have 2.',           department_id: 1, is_resolved: false, created_at: '2026-11-18T14:30:00Z' },
  { id: 2, type: 'SHORTAGE',       severity: 'WARNING',  message: 'ICU: Afternoon shift below minimum (3 required, 2 assigned).',   department_id: 3, is_resolved: false, created_at: '2026-11-18T10:15:00Z' },
  { id: 3, type: 'OVERTIME',       severity: 'WARNING',  message: 'Dr. Sarah Chen: 52h this week — exceeds 48h limit.',            department_id: 1, is_resolved: false, created_at: '2026-11-17T18:00:00Z' },
  { id: 4, type: 'BURNOUT',        severity: 'CRITICAL', message: 'Nurse Carol Singh: Burnout risk 82/100 — 4 consecutive nights.', department_id: 1, is_resolved: false, created_at: '2026-11-17T09:00:00Z' },
  { id: 5, type: 'REST_VIOLATION', severity: 'WARNING',  message: 'Nurse Bob Freeman: 9h rest gap (minimum 11h required).',        department_id: 1, is_resolved: false, created_at: '2026-11-16T22:00:00Z' },
  { id: 6, type: 'SHORTAGE',       severity: 'INFO',     message: 'Pediatrics: Weekend morning shifts may face minor shortage.',     department_id: 4, is_resolved: false, created_at: '2026-11-16T08:00:00Z' },
  { id: 7, type: 'SYSTEM',         severity: 'INFO',     message: 'GRU model outperforms LSTM on Emergency (MAE: 3.0 vs 3.2).',    department_id: null, is_resolved: true,  created_at: '2026-11-15T12:00:00Z' },
]

export const mockModelMetrics = [
  { model: 'LSTM',          department: 'emergency', lookback: 168, MAE: 3.21, RMSE: 4.83, MAPE: 8.14, R2: 0.907 },
  { model: 'GRU',           department: 'emergency', lookback: 168, MAE: 3.03, RMSE: 4.52, MAPE: 7.62, R2: 0.928 },
  { model: 'ARIMA',         department: 'emergency', lookback: 168, MAE: 4.78, RMSE: 6.21, MAPE: 12.3, R2: 0.820 },
  { model: 'SeasonalNaive', department: 'emergency', lookback: 168, MAE: 6.12, RMSE: 8.44, MAPE: 16.7, R2: 0.712 },
  { model: 'GRU',           department: 'icu',       lookback: 168, MAE: 1.05, RMSE: 1.57, MAPE: 8.64, R2: 0.912 },
  { model: 'GRU',           department: 'general_ward', lookback: 168, MAE: 2.31, RMSE: 3.42, MAPE: 9.70, R2: 0.901 },
]

// 7 days of hourly forecast data for Emergency dept
export const mockForecastData = Array.from({ length: 7 * 24 }, (_, i) => {
  const hour = i % 24
  const day  = Math.floor(i / 24)
  const isWeekend = day >= 5
  const hourPattern = [
    0.45,0.38,0.33,0.30,0.32,0.40,0.60,0.80,0.95,1.00,0.98,0.95,
    0.92,0.90,0.88,0.87,0.90,0.95,1.00,0.98,0.90,0.78,0.65,0.52
  ][hour]
  const base    = 12 * hourPattern * (isWeekend ? 0.85 : 1.0)
  const jitter  = (Math.random() - 0.5) * 2
  return {
    hour:      `Day${day+1} ${String(hour).padStart(2,'0')}:00`,
    actual:    Math.max(0, Math.round(base + jitter + (Math.random() * 2))),
    predicted: Math.max(0, Math.round(base + jitter)),
    confidence_low:  Math.max(0, Math.round(base - 2)),
    confidence_high: Math.round(base + 2),
  }
})

// Shift-level forecast (7 days × 3 shifts × 4 departments)
export const mockShiftForecast = (() => {
  const depts  = ['Emergency', 'General Ward', 'ICU', 'Pediatrics']
  const shifts = ['MORNING', 'AFTERNOON', 'NIGHT']
  const base   = { Emergency: { MORNING:48,AFTERNOON:52,NIGHT:30 }, 'General Ward': { MORNING:32,AFTERNOON:28,NIGHT:18 }, ICU: { MORNING:12,AFTERNOON:12,NIGHT:10 }, Pediatrics: { MORNING:20,AFTERNOON:22,NIGHT:12 } }
  const result: any[] = []
  for (let d = 0; d < 7; d++) {
    const date = `2026-11-${19 + d}`
    for (const dept of depts) {
      for (const shift of shifts) {
        const b = (base as any)[dept][shift]
        result.push({ date, department: dept, shift_type: shift, predicted_patients: b + Math.round((Math.random()-0.5)*6) })
      }
    }
  }
  return result
})()

export const mockBurnoutRisk = [
  { employee_id: 11, employee_name: 'Nurse Carol Singh',    role: 'NURSE',  department: 'Emergency',    burnout_score: 82, risk_level: 'CRITICAL', weekly_hours: 48, night_shifts: 4, days_worked: 6 },
  { employee_id: 1,  employee_name: 'Dr. Sarah Chen',       role: 'DOCTOR', department: 'Emergency',    burnout_score: 71, risk_level: 'HIGH',     weekly_hours: 52, night_shifts: 2, days_worked: 6 },
  { employee_id: 3,  employee_name: 'Dr. Priya Sharma',     role: 'DOCTOR', department: 'ICU',          burnout_score: 64, risk_level: 'HIGH',     weekly_hours: 48, night_shifts: 3, days_worked: 5 },
  { employee_id: 9,  employee_name: 'Nurse Alice Park',     role: 'NURSE',  department: 'Emergency',    burnout_score: 55, risk_level: 'MEDIUM',   weekly_hours: 40, night_shifts: 2, days_worked: 5 },
  { employee_id: 17, employee_name: 'Nurse Isabelle Russo', role: 'NURSE',  department: 'ICU',          burnout_score: 48, risk_level: 'MEDIUM',   weekly_hours: 40, night_shifts: 2, days_worked: 5 },
  { employee_id: 6,  employee_name: 'Dr. Ravi Patel',       role: 'DOCTOR', department: 'General Ward', burnout_score: 32, risk_level: 'LOW',      weekly_hours: 40, night_shifts: 1, days_worked: 5 },
  { employee_id: 7,  employee_name: 'Dr. Fatima Al-Hassan', role: 'DOCTOR', department: 'Pediatrics',   burnout_score: 25, risk_level: 'LOW',      weekly_hours: 32, night_shifts: 0, days_worked: 4 },
]

export const mockSchedule = (() => {
  const depts  = [{ id:1,name:'Emergency' }, { id:2,name:'General Ward' }, { id:3,name:'ICU' }, { id:4,name:'Pediatrics' }]
  const shifts = ['MORNING','AFTERNOON','NIGHT']
  const result: any[] = []
  let id = 1
  for (let d = 0; d < 7; d++) {
    for (const dept of depts) {
      for (const shift of shifts) {
        const req = dept.id === 1 ? 4 : dept.id === 3 ? 3 : 3
        const asgn = shift === 'NIGHT' && dept.id === 1 ? 2 : req - (Math.random() > 0.8 ? 1 : 0)
        result.push({
          shift_id: id++, date: `2026-11-${19 + d}`, shift_type: shift,
          department_id: dept.id, department: dept.name,
          required: req, assigned: Math.round(asgn),
          coverage_pct: Math.round(asgn / req * 100),
        })
      }
    }
  }
  return result
})()

export const mockDashboardKPIs = {
  total_staff:    28,
  coverage_pct:   87,
  active_alerts:  5,
  avg_workload:   72,
}
