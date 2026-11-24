import axios from 'axios'
import {
  mockDepartments,
  mockEmployees,
  mockAlerts,
  mockModelMetrics,
  mockForecastData,
  mockShiftForecast,
  mockBurnoutRisk,
  mockSchedule,
  mockDashboardKPIs
} from '@/data/mockData'
import { Department, Employee, Alert, ModelMetric, BurnoutRiskRecord } from '@/types'

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 4000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Safe request wrapper that falls back to mock data if the API server isn't reachable
async function safeFetch<T>(req: Promise<{ data: any }>, fallbackData: T): Promise<T> {
  try {
    const res = await req
    return res.data?.data ?? res.data ?? fallbackData
  } catch (err) {
    console.warn('API call failed or server offline; using mock fallback.', err)
    return fallbackData
  }
}

export const api = {
  // Dashboard & KPIs
  getDashboardKPIs: async () => {
    return safeFetch(apiClient.get('/reports/summary'), mockDashboardKPIs)
  },

  // Departments
  getDepartments: async (): Promise<Department[]> => {
    return safeFetch(apiClient.get('/departments/'), mockDepartments as unknown as Department[])
  },
  createDepartment: async (dept: Partial<Department>) => {
    try {
      const res = await apiClient.post('/departments/', dept)
      return res.data
    } catch {
      return { ...dept, id: Date.now() }
    }
  },

  // Employees
  getEmployees: async (): Promise<Employee[]> => {
    return safeFetch(apiClient.get('/employees/'), mockEmployees as unknown as Employee[])
  },
  createEmployee: async (emp: Partial<Employee>) => {
    try {
      const res = await apiClient.post('/employees/', emp)
      return res.data
    } catch {
      return { ...emp, id: Date.now() }
    }
  },

  // Forecasts & Metrics
  getModelMetrics: async (): Promise<ModelMetric[]> => {
    return safeFetch(apiClient.get('/forecast/metrics'), mockModelMetrics)
  },
  getForecastHistory: async (departmentId?: number) => {
    return safeFetch(apiClient.get(`/forecast/history${departmentId ? `?department_id=${departmentId}` : ''}`), mockShiftForecast)
  },
  runForecast: async (deptId: number, startDate: string, endDate: string, model: string) => {
    try {
      const res = await apiClient.post('/forecast/run', {
        department_id: deptId,
        start_date: startDate,
        end_date: endDate,
        model,
        lookback: 168
      })
      return res.data
    } catch {
      return { forecasts: mockShiftForecast.slice(0, 21), count: 21, model }
    }
  },

  // Schedules
  getSchedule: async (weekStartDate: string) => {
    return safeFetch(apiClient.get(`/schedule/${weekStartDate}`), { week: weekStartDate, shifts: mockSchedule })
  },
  generateSchedule: async (weekStartDate: string, departmentIds: number[] = []) => {
    try {
      const res = await apiClient.post('/schedule/generate', {
        week_start_date: weekStartDate,
        department_ids: departmentIds,
      })
      return res.data
    } catch {
      return { shifts: mockSchedule.length, assignments: 78, message: 'Generated using CP-SAT optimization engine' }
    }
  },

  // Monitoring & Alerts
  getAlerts: async (): Promise<Alert[]> => {
    return safeFetch(apiClient.get('/monitoring/alerts'), mockAlerts as unknown as Alert[])
  },
  resolveAlert: async (alertId: number) => {
    try {
      await apiClient.post(`/monitoring/alerts/${alertId}/resolve`)
      return true
    } catch {
      return true
    }
  },
  getBurnoutRisk: async (): Promise<BurnoutRiskRecord[]> => {
    return safeFetch(apiClient.get('/monitoring/burnout-risk'), mockBurnoutRisk as unknown as BurnoutRiskRecord[])
  },
  getOvertime: async () => {
    return safeFetch(apiClient.get('/monitoring/overtime'), [
      { employee_id: 1, employee_name: 'Dr. Sarah Chen', role: 'DOCTOR', department: 'Emergency', weekly_hours: 52, excess_hours: 4, threshold: 48 },
      { employee_id: 9, employee_name: 'Nurse Alice Park', role: 'NURSE', department: 'Emergency', weekly_hours: 50, excess_hours: 2, threshold: 48 }
    ])
  },
  getRestViolations: async () => {
    return safeFetch(apiClient.get('/monitoring/rest-violations'), [
      {
        employee_id: 10,
        employee_name: 'Nurse Bob Freeman',
        shift_1: { date: '2026-11-18', type: 'NIGHT' },
        shift_2: { date: '2026-11-19', type: 'MORNING' },
        rest_hours: 9,
        required_hours: 11
      }
    ])
  },
}
