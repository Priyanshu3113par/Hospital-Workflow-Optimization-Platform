import React, { useState } from 'react'
import { Bell, Search, CheckCircle2, AlertTriangle, X, Check, Activity } from 'lucide-react'
import { useHospital } from '@/context/HospitalContext'

export default function Header() {
  const { alerts, resolveAlert } = useHospital()
  const [showAlertsDropdown, setShowAlertsDropdown] = useState(false)
  const activeAlerts = alerts.filter(a => !a.is_resolved)

  return (
    <header className="h-16 border-b border-slate-200 bg-white sticky top-0 z-20 px-6 flex items-center justify-between shadow-xs">
      {/* Search Input */}
      <div className="relative w-72 sm:w-88">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Search staff, shifts, clinical units..."
          className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600 transition-all"
        />
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* System Health Indicator */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200/80 text-emerald-800 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>CP-SAT Optimizer: Online</span>
        </div>

        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowAlertsDropdown(!showAlertsDropdown)}
            className="p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors relative"
            title="Shortage and Overtime Alerts"
          >
            <Bell className="w-4 h-4" />
            {activeAlerts.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-600 text-white text-[10px] font-bold flex items-center justify-center shadow-xs">
                {activeAlerts.length}
              </span>
            )}
          </button>

          {showAlertsDropdown && (
            <div className="absolute right-0 mt-2 w-88 bg-white border border-slate-200 rounded-xl shadow-lg p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100 mb-2">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-slate-800">Operational Alerts</span>
                  <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-rose-50 text-rose-700">
                    {activeAlerts.length} Active
                  </span>
                </div>
                <button
                  onClick={() => setShowAlertsDropdown(false)}
                  className="p-1 rounded text-slate-400 hover:text-slate-600"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {activeAlerts.length === 0 ? (
                  <div className="text-center py-6 text-xs text-slate-500">
                    <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto mb-1" />
                    No active shortages or violations
                  </div>
                ) : (
                  activeAlerts.map(alert => (
                    <div
                      key={alert.id}
                      className={`p-2.5 rounded-lg border text-xs space-y-1.5 transition-all ${
                        alert.severity === 'CRITICAL'
                          ? 'bg-rose-50/50 border-rose-200'
                          : 'bg-amber-50/50 border-amber-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className={`font-bold text-[11px] ${
                          alert.severity === 'CRITICAL' ? 'text-rose-700' : 'text-amber-800'
                        }`}>
                          {alert.type}
                        </span>
                        <span className="text-[10px] text-slate-400">{alert.timestamp}</span>
                      </div>
                      <p className="text-slate-700 text-[11px] leading-relaxed">{alert.message}</p>
                      <div className="flex justify-end pt-1">
                        <button
                          onClick={() => resolveAlert(alert.id)}
                          className="px-2 py-0.5 rounded text-[10px] font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 flex items-center gap-1 shadow-2xs"
                        >
                          <Check className="w-3 h-3 text-emerald-600" /> Mark Resolved
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Clinical Director User Pill */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-primary-700 text-white font-bold text-xs flex items-center justify-center shadow-xs">
            MS
          </div>
          <div className="hidden sm:block text-left leading-none">
            <p className="text-xs font-semibold text-slate-800">Hospital Administration</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Workforce Dispatch Center</p>
          </div>
        </div>
      </div>
    </header>
  )
}
