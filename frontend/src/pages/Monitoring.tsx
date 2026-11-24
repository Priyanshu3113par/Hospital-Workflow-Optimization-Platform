import React, { useState } from 'react'
import {
  Activity,
  AlertTriangle,
  Flame,
  Clock,
  ShieldAlert,
  CheckCircle2,
  Filter,
  UserCheck,
  Plus,
  RotateCcw,
  Sparkles,
  Check,
  X
} from 'lucide-react'
import Badge from '@/components/common/Badge'
import Modal from '@/components/common/Modal'
import { useHospital } from '@/context/HospitalContext'
import { AlertType, SeverityType } from '@/types'

export default function Monitoring() {
  const {
    burnoutRecords,
    alerts,
    resolveAlert,
    dismissAlert,
    addManualAlert,
    runOptimizationSolver,
    departments,
  } = useHospital()

  const [riskFilter, setRiskFilter] = useState<string>('ALL')
  const [alertTypeFilter, setAlertTypeFilter] = useState<string>('ALL')
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false)
  const [rebalanceNotification, setRebalanceNotification] = useState<string | null>(null)

  // New alert form state
  const [newAlertForm, setNewAlertForm] = useState({
    type: 'SHORTAGE' as AlertType,
    severity: 'WARNING' as SeverityType,
    department_id: 1,
    message: '',
  })

  const filteredBurnout = burnoutRecords.filter((rec) => {
    if (riskFilter === 'ALL') return true
    return rec.risk_level === riskFilter
  })

  const filteredAlerts = alerts.filter((alert) => {
    if (alertTypeFilter === 'ALL') return true
    if (alertTypeFilter === 'UNRESOLVED') return !alert.is_resolved
    return alert.type === alertTypeFilter
  })

  const handleCreateAlert = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newAlertForm.message.trim()) return

    addManualAlert({
      type: newAlertForm.type,
      severity: newAlertForm.severity,
      department_id: Number(newAlertForm.department_id),
      message: newAlertForm.message.trim(),
    })

    setIsAlertModalOpen(false)
    setNewAlertForm({
      type: 'SHORTAGE',
      severity: 'WARNING',
      department_id: 1,
      message: '',
    })
  }

  const handleAutoRebalance = () => {
    const res = runOptimizationSolver()
    setRebalanceNotification(`Workload rebalanced across ${res.assignedCount} shifts. Solver status: ${res.status}.`)
    setTimeout(() => setRebalanceNotification(null), 4000)
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Rebalance Toast */}
      {rebalanceNotification && (
        <div className="p-3.5 rounded-xl bg-teal-50 border border-teal-200 text-teal-800 text-xs font-medium flex items-center justify-between shadow-xs">
          <span className="flex items-center gap-2">
            <Check className="w-4 h-4 text-teal-600" />
            {rebalanceNotification}
          </span>
        </div>
      )}

      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Workforce Health, Burnout & Safety Monitoring
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time tracking of consecutive working days, weekly contractual hour limits, mandatory 11h rest gaps, and dynamic burnout scores.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleAutoRebalance}
            className="btn-primary"
          >
            <Sparkles className="w-4 h-4" />
            Auto-Rebalance Burnout Risk
          </button>
          <button
            onClick={() => setIsAlertModalOpen(true)}
            className="btn-secondary"
          >
            <Plus className="w-4 h-4" />
            Issue Safety Alert
          </button>
        </div>
      </div>

      {/* Burnout Risk Matrix Table */}
      <div className="hospital-card p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-100">
          <div>
            <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
              <Flame className="w-4 h-4 text-amber-600" />
              Composite Employee Burnout Risk Index (0 – 100)
            </h2>
            <p className="text-xs text-slate-500">
              Heuristic formulated from: Weekly Hours (40 pts), Night Shifts (20 pts), Consecutive Days (25 pts), Rest Infractions (15 pts).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="input-field py-1 text-xs"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical (&ge;75)</option>
              <option value="HIGH">High (55–74)</option>
              <option value="MEDIUM">Medium (35–54)</option>
              <option value="LOW">Low (&lt;35)</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Healthcare Professional</th>
                <th className="py-2.5 px-3">Role</th>
                <th className="py-2.5 px-3">Primary Unit</th>
                <th className="py-2.5 px-3">Weekly Hours</th>
                <th className="py-2.5 px-3">Night Shifts</th>
                <th className="py-2.5 px-3">Days Worked</th>
                <th className="py-2.5 px-3">Rest Infractions</th>
                <th className="py-2.5 px-3">Burnout Meter</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredBurnout.map((rec) => (
                <tr key={rec.employee_id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-3 font-bold text-slate-800">
                    {rec.employee_name}
                  </td>
                  <td className="py-3 px-3">
                    <Badge variant={rec.role === 'DOCTOR' ? 'purple' : 'teal'}>
                      {rec.role}
                    </Badge>
                  </td>
                  <td className="py-3 px-3 text-slate-600 font-medium">{rec.department_name}</td>
                  <td className="py-3 px-3 font-mono">
                    <span className={rec.weekly_hours > 40 ? 'text-amber-700 font-bold' : 'text-slate-800'}>
                      {rec.weekly_hours}h
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-700">{rec.night_shifts} nights</td>
                  <td className="py-3 px-3 font-mono text-slate-700">{rec.consecutive_days} days</td>
                  <td className="py-3 px-3 font-mono">
                    <span className={rec.rest_violations > 0 ? 'text-rose-600 font-bold' : 'text-slate-400'}>
                      {rec.rest_violations}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-slate-100 rounded-full h-1.5 overflow-hidden border border-slate-200/60">
                        <div
                          className={`h-1.5 rounded-full transition-all duration-300 ${
                            rec.burnout_score >= 75 ? 'bg-rose-500' :
                            rec.burnout_score >= 55 ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${rec.burnout_score}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs font-bold text-slate-800">{rec.burnout_score}</span>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <Badge variant={
                      rec.risk_level === 'CRITICAL' ? 'danger' :
                      rec.risk_level === 'HIGH' ? 'warning' : 'success'
                    }>
                      {rec.risk_level}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Operational Dispatch Alerts Queue */}
      <div className="hospital-card p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-100">
          <div>
            <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-600" />
              Automated Hospital Safety Alerts & Violations
            </h2>
            <p className="text-xs text-slate-500">
              Generated automatically by CP-SAT solver audits and room capacity triggers
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={alertTypeFilter}
              onChange={(e) => setAlertTypeFilter(e.target.value)}
              className="input-field py-1 text-xs"
            >
              <option value="ALL">All Alerts</option>
              <option value="UNRESOLVED">Active / Unresolved Only</option>
              <option value="SHORTAGE">Staff Shortages</option>
              <option value="OVERTIME">Overtime Violations</option>
              <option value="BURNOUT">Burnout Warnings</option>
              <option value="CAPACITY_SURGE">Bed Capacity Surges</option>
            </select>
          </div>
        </div>

        <div className="space-y-3">
          {filteredAlerts.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-400">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              No alerts match the selected filter.
            </div>
          ) : (
            filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                  alert.is_resolved
                    ? 'bg-slate-50/70 border-slate-200 opacity-60'
                    : alert.severity === 'CRITICAL'
                    ? 'bg-rose-50/60 border-rose-200'
                    : 'bg-amber-50/60 border-amber-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className={`p-2 rounded-lg mt-0.5 shrink-0 ${
                    alert.is_resolved ? 'bg-slate-200 text-slate-600' :
                    alert.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    <AlertTriangle className="w-4 h-4" />
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-slate-800">{alert.type}</span>
                      <Badge variant={
                        alert.is_resolved ? 'neutral' :
                        alert.severity === 'CRITICAL' ? 'danger' : 'warning'
                      }>
                        {alert.is_resolved ? 'RESOLVED' : alert.severity}
                      </Badge>
                      <span className="text-[10px] text-slate-400">{alert.timestamp}</span>
                    </div>
                    <p className="text-xs text-slate-700 mt-1 leading-relaxed">{alert.message}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {!alert.is_resolved ? (
                    <button
                      onClick={() => resolveAlert(alert.id)}
                      className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
                    >
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                      Mark Resolved
                    </button>
                  ) : (
                    <span className="text-[11px] text-slate-500 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Resolved
                    </span>
                  )}
                  <button
                    onClick={() => dismissAlert(alert.id)}
                    className="p-1.5 text-slate-400 hover:text-slate-600 rounded"
                    title="Dismiss alert"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Manual Issue Safety Alert Modal */}
      <Modal
        isOpen={isAlertModalOpen}
        onClose={() => setIsAlertModalOpen(false)}
        title="Dispatch Clinical Safety Alert"
        subtitle="Manually notify shift supervisors of unexpected ward surges or emergency staffing requests."
      >
        <form onSubmit={handleCreateAlert} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Alert Category</label>
              <select
                value={newAlertForm.type}
                onChange={(e) => setNewAlertForm({ ...newAlertForm, type: e.target.value as AlertType })}
                className="input-field"
              >
                <option value="SHORTAGE">Staff Shortage</option>
                <option value="CAPACITY_SURGE">Bed Capacity Surge</option>
                <option value="OVERTIME">Overtime Infraction</option>
                <option value="BURNOUT">Burnout Risk</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Severity Level</label>
              <select
                value={newAlertForm.severity}
                onChange={(e) => setNewAlertForm({ ...newAlertForm, severity: e.target.value as SeverityType })}
                className="input-field"
              >
                <option value="CRITICAL">Critical (Immediate Action)</option>
                <option value="WARNING">Warning (Elevated Risk)</option>
                <option value="INFO">Informational Advisory</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-slate-700 mb-1 font-bold">Clinical Department</label>
            <select
              value={newAlertForm.department_id}
              onChange={(e) => setNewAlertForm({ ...newAlertForm, department_id: Number(e.target.value) })}
              className="input-field"
            >
              {departments.map(d => (
                <option key={d.id} value={d.id}>{d.name} ({d.code})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-700 mb-1 font-bold">Alert Description & Instructions</label>
            <textarea
              required
              rows={3}
              placeholder="e.g. Mass casualty incident incoming. Emergency unit requesting 2 additional trauma nurses for Night shift."
              value={newAlertForm.message}
              onChange={(e) => setNewAlertForm({ ...newAlertForm, message: e.target.value })}
              className="input-field resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsAlertModalOpen(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
            >
              Broadcast Alert
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
