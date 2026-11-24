import React, { useState } from 'react'
import {
  Users,
  CalendarCheck,
  AlertTriangle,
  Activity,
  ArrowUpRight,
  TrendingUp,
  Brain,
  BedDouble,
  Sparkles,
  CheckCircle2,
  Clock,
  ChevronRight,
  ShieldAlert
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import StatCard from '@/components/common/StatCard'
import Badge from '@/components/common/Badge'
import { useHospital } from '@/context/HospitalContext'
import { mockForecastData } from '@/data/mockData'
import { useNavigate } from 'react-router-dom'

export default function Dashboard() {
  const navigate = useNavigate()
  const {
    departments,
    employees,
    shifts,
    alerts,
    resolveAlert,
    runOptimizationSolver,
    burnoutRecords,
  } = useHospital()

  const [isSolving, setIsSolving] = useState(false)
  const [solverNotification, setSolverNotification] = useState<string | null>(null)

  // Calculate live summary stats
  const activeStaff = employees.filter(e => e.is_active)
  const activeAlerts = alerts.filter(a => !a.is_resolved)
  const criticalAlerts = activeAlerts.filter(a => a.severity === 'CRITICAL')

  // Calculate shift coverage percentage
  const totalShifts = shifts.length
  const coveredShifts = shifts.filter(s => s.assigned_employee_ids.length >= s.required_total).length
  const coveragePct = totalShifts > 0 ? Math.round((coveredShifts / totalShifts) * 100) : 0

  // Total bed capacity
  const totalBeds = departments.reduce((acc, d) => acc + d.beds_total, 0)
  const occupiedBeds = departments.reduce((acc, d) => acc + d.current_occupancy, 0)
  const bedOccupancyPct = totalBeds > 0 ? Math.round((occupiedBeds / totalBeds) * 100) : 0

  // 24-hour ED patient arrival trajectory
  const todayForecast = mockForecastData.slice(0, 24).map(d => ({
    hour: d.hour.split(' ')[1],
    actual: d.actual,
    predicted: d.predicted,
  }))

  const handleQuickOptimize = () => {
    setIsSolving(true)
    setTimeout(() => {
      const res = runOptimizationSolver()
      setIsSolving(false)
      setSolverNotification(`CP-SAT Optimizer completed in ${res.solverTimeMs}ms: ${res.assignedCount} shifts balanced.`)
      setTimeout(() => setSolverNotification(null), 4000)
    }, 700)
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Top Banner / Notification if solver ran */}
      {solverNotification && (
        <div className="p-3.5 rounded-xl bg-teal-50 border border-teal-200 text-teal-800 text-xs font-medium flex items-center justify-between shadow-xs animate-in slide-in-from-top-1">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-teal-600" />
            {solverNotification}
          </span>
          <button
            onClick={() => navigate('/scheduling')}
            className="underline font-bold hover:text-teal-900"
          >
            View Roster
          </button>
        </div>
      )}

      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Hospital Operations & Staffing Control
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time patient inflow forecasting, bed infrastructure tracking, and constraint-optimized clinical rosters.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleQuickOptimize}
            disabled={isSolving}
            className="btn-primary"
          >
            <Brain className={`w-4 h-4 ${isSolving ? 'animate-spin' : ''}`} />
            {isSolving ? 'Solving Constraints...' : 'Run Auto-Scheduler'}
          </button>
        </div>
      </div>

      {/* KPI Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Healthcare Staff"
          value={activeStaff.length}
          change={`${employees.filter(e => e.role === 'DOCTOR').length} Doctors`}
          changeType="positive"
          icon={Users}
          iconColor="text-teal-700 bg-teal-50"
          subtitle={`${employees.filter(e => e.role === 'NURSE').length} Nurses, ${employees.filter(e => e.role === 'TECHNICIAN').length} Techs`}
        />
        <StatCard
          title="Shift Coverage Rate"
          value={`${coveragePct}%`}
          change={`${coveredShifts}/${totalShifts} Shifts`}
          changeType={coveragePct >= 85 ? 'positive' : 'negative'}
          icon={CalendarCheck}
          iconColor="text-emerald-700 bg-emerald-50"
          subtitle={`${totalShifts - coveredShifts} shifts need attention`}
        />
        <StatCard
          title="Bed Capacity In-Use"
          value={`${bedOccupancyPct}%`}
          change={`${occupiedBeds} / ${totalBeds} Beds`}
          changeType={bedOccupancyPct > 85 ? 'negative' : 'neutral'}
          icon={BedDouble}
          iconColor="text-sky-700 bg-sky-50"
          subtitle="4 Active Clinical Departments"
        />
        <StatCard
          title="Staffing & Safety Alerts"
          value={activeAlerts.length}
          change={`${criticalAlerts.length} Critical`}
          changeType={criticalAlerts.length > 0 ? 'negative' : 'positive'}
          icon={AlertTriangle}
          iconColor="text-rose-700 bg-rose-50"
          subtitle="Shortages, Overtime & Rest Violations"
        />
      </div>

      {/* Main Charts & Department Capacity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Real-Time Patient Inflow Forecast */}
        <div className="lg:col-span-2 hospital-card p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-teal-700" />
                Emergency Department: 24h Patient Arrival Inflow
              </h2>
              <p className="text-xs text-slate-500">
                Ground truth hourly patient admissions vs. Deep Learning GRU predicted trajectory
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-slate-600 font-medium">
                <span className="w-2.5 h-2.5 rounded-sm bg-slate-400" /> Actual
              </span>
              <span className="flex items-center gap-1.5 text-slate-800 font-semibold">
                <span className="w-2.5 h-2.5 rounded-sm bg-teal-600" /> PyTorch GRU Forecast
              </span>
            </div>
          </div>

          <div className="h-68 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={todayForecast} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#94a3b8" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="predGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0d9488" stopOpacity={0.35}/>
                    <stop offset="95%" stopColor="#0d9488" stopOpacity={0.02}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="hour" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                  labelStyle={{ color: '#0f172a', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="actual" stroke="#94a3b8" strokeWidth={2} fillOpacity={1} fill="url(#actualGrad)" name="Actual Patient Admissions" />
                <Area type="monotone" dataKey="predicted" stroke="#0f766e" strokeWidth={2.5} fillOpacity={1} fill="url(#predGrad)" name="GRU Model Prediction" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Model selected: <strong>2-Layer Stacked GRU (168h Lookback)</strong></span>
            <button
              onClick={() => navigate('/forecasting')}
              className="text-primary-700 hover:text-primary-800 font-semibold flex items-center gap-1"
            >
              Adjust Forecast & Scenarios <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Right 1 Col: Department Bed Capacity & Acuity Ratios */}
        <div className="hospital-card p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h2 className="text-sm font-bold text-slate-800 flex items-center gap-1.5">
                <BedDouble className="w-4 h-4 text-teal-700" />
                Department Bed Occupancy
              </h2>
              <button
                onClick={() => navigate('/departments')}
                className="text-xs text-primary-700 hover:underline font-semibold"
              >
                Manage
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-1.5">
              Live patient load determining clinical staffing headcount
            </p>
          </div>

          <div className="space-y-4 my-2">
            {departments.map((dept) => {
              const occPct = Math.round((dept.current_occupancy / dept.beds_total) * 100)
              const deptStaffCount = employees.filter(e => e.department_id === dept.id && e.is_active).length

              return (
                <div key={dept.id} className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="font-semibold text-slate-800">{dept.name}</span>
                    <span className="text-slate-500 font-mono">
                      {dept.current_occupancy}/{dept.beds_total} beds ({occPct}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200/60">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        occPct >= 90 ? 'bg-rose-500' : occPct >= 75 ? 'bg-amber-500' : 'bg-teal-600'
                      }`}
                      style={{ width: `${occPct}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>Active staff: {deptStaffCount} personnel</span>
                    <span>1 Dr / {dept.patients_per_doctor} pts</span>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 text-xs text-slate-600 flex items-center justify-between">
            <span>Burnout Risk Index:</span>
            <span className="font-bold text-emerald-700">Healthy (Avg: 38/100)</span>
          </div>
        </div>
      </div>

      {/* Bottom Row: Active Safety Alerts & Staff Shortages */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Alerts List */}
        <div className="lg:col-span-2 hospital-card p-5 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-600" />
              Active Dispatch Alerts & Staffing Shortages
            </h2>
            <button
              onClick={() => navigate('/monitoring')}
              className="text-xs text-primary-700 hover:underline font-semibold flex items-center gap-1"
            >
              Workforce Health & Alerts <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-slate-100">
            {activeAlerts.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto mb-1.5" />
                All shifts are adequately covered and no rest violations are active!
              </div>
            ) : (
              activeAlerts.slice(0, 4).map((alert) => (
                <div key={alert.id} className="py-3 flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <span className={`p-1.5 rounded-md mt-0.5 shrink-0 ${
                      alert.severity === 'CRITICAL' ? 'bg-rose-50 text-rose-700' : 'bg-amber-50 text-amber-700'
                    }`}>
                      <AlertTriangle className="w-4 h-4" />
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-800">{alert.type}</span>
                        <Badge variant={alert.severity === 'CRITICAL' ? 'danger' : 'warning'}>
                          {alert.severity}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{alert.message}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => resolveAlert(alert.id)}
                    className="btn-secondary text-xs py-1 px-2.5 shrink-0"
                  >
                    Resolve
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Burnout Watchlist Preview */}
        <div className="hospital-card p-5 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-800 flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-amber-600" />
              Burnout Risk Watchlist
            </h2>
            <button
              onClick={() => navigate('/monitoring')}
              className="text-xs text-primary-700 hover:underline font-semibold"
            >
              View All
            </button>
          </div>

          <div className="space-y-2.5">
            {burnoutRecords.slice(0, 4).map((rec) => (
              <div key={rec.employee_id} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/60 flex items-center justify-between text-xs">
                <div>
                  <p className="font-bold text-slate-800">{rec.employee_name}</p>
                  <p className="text-[11px] text-slate-500">{rec.role} • {rec.weekly_hours}h / wk</p>
                </div>
                <div className="text-right">
                  <Badge variant={
                    rec.risk_level === 'CRITICAL' ? 'danger' :
                    rec.risk_level === 'HIGH' ? 'warning' : 'success'
                  }>
                    {rec.risk_level} ({rec.burnout_score})
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
