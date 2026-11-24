export type RoleType = 'DOCTOR' | 'NURSE' | 'TECHNICIAN' | 'ADMIN'
export type ShiftType = 'MORNING' | 'AFTERNOON' | 'NIGHT'
export type SeverityType = 'INFO' | 'WARNING' | 'CRITICAL'
export type AlertType = 'SHORTAGE' | 'OVERTIME' | 'BURNOUT' | 'REST_VIOLATION' | 'CAPACITY_SURGE'

export interface Department {
  id: number
  name: string
  code: string
  rooms_capacity: number       // Hospital room / infrastructure capacity
  beds_total: number           // Total physical bed capacity
  current_occupancy: number    // Active occupied beds
  min_staff_per_shift: number  // Baseline safety staffing requirement
  patients_per_doctor: number  // Acuity ratio: 1 Doctor per X patients
  patients_per_nurse: number   // Acuity ratio: 1 Nurse per X patients
  is_active: boolean
  description: string
}

export interface EmployeeAvailability {
  date: string       // YYYY-MM-DD
  MORNING: boolean
  AFTERNOON: boolean
  NIGHT: boolean
}

export interface Employee {
  id: number
  name: string
  email: string
  phone?: string
  role: RoleType
  department_id: number
  department_name?: string
  max_hours_week: number
  qualifications: string[]
  is_active: boolean
  created_at?: string
  custom_notes?: string
}

export interface ShiftRecord {
  id: string
  date: string                   // YYYY-MM-DD
  shift_type: ShiftType
  department_id: number
  required_doctors: number
  required_nurses: number
  required_total: number
  assigned_employee_ids: number[]
  notes?: string
}

export interface AlertItem {
  id: string | number
  type: AlertType
  severity: SeverityType
  department_id?: number | null
  employee_id?: number | null
  message: string
  is_resolved: boolean
  timestamp?: string
  created_at?: string
}

export interface BurnoutRecord {
  employee_id: number
  employee_name: string
  role: RoleType
  department_name: string
  weekly_hours: number
  night_shifts: number
  consecutive_days: number
  rest_violations: number
  burnout_score: number        // 0 - 100
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
}

export interface ModelMetricRecord {
  model: string
  department: string
  lookback: number
  MAE: number
  RMSE: number
  MAPE: number
  R2: number
  evaluated_at?: string
}

// Convenient type aliases for backwards compatibility
export type Alert = AlertItem
export type ModelMetric = ModelMetricRecord
export type BurnoutRiskRecord = BurnoutRecord
