import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  CalendarDays,
  Users,
  Building2,
  Activity,
  FileBarChart2,
  HeartPulse,
  RotateCcw,
  BedDouble,
  ShieldCheck
} from 'lucide-react'
import { useHospital } from '@/context/HospitalContext'

const navItems = [
  { path: '/',            label: 'Overview & Control',  icon: LayoutDashboard },
  { path: '/forecasting', label: 'AI Demand Forecast',  icon: TrendingUp },
  { path: '/scheduling',  label: 'Shift Scheduler',     icon: CalendarDays },
  { path: '/employees',   label: 'Staff Directory',     icon: Users },
  { path: '/departments', label: 'Departments & Beds',  icon: Building2 },
  { path: '/monitoring',  label: 'Workforce Health',    icon: Activity },
  { path: '/reports',     label: 'Audit & Reports',     icon: FileBarChart2 },
]

export default function Sidebar() {
  const { departments, resetToSampleData } = useHospital()

  // Calculate hospital-wide bed occupancy
  const totalBeds = departments.reduce((acc, d) => acc + d.beds_total, 0)
  const occupiedBeds = departments.reduce((acc, d) => acc + d.current_occupancy, 0)
  const occupancyPct = totalBeds > 0 ? Math.round((occupiedBeds / totalBeds) * 100) : 0

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0 z-30 select-none shadow-sm">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-100 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary-700 flex items-center justify-center text-white shadow-sm shrink-0">
          <HeartPulse className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <h1 className="font-bold text-base text-slate-900 tracking-tight leading-none">CarePulse</h1>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-primary-100 text-primary-800">
              AI
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-medium truncate mt-0.5">
            Workforce Management
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <p className="px-3 pt-2 pb-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Hospital Operations
        </p>
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all duration-150 ${
                  isActive
                    ? 'bg-primary-50 text-primary-800 font-semibold border-l-4 border-primary-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Live Hospital Capacity Status */}
      <div className="p-4 m-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="font-semibold text-slate-700 flex items-center gap-1.5">
            <BedDouble className="w-3.5 h-3.5 text-primary-700" />
            Bed Occupancy
          </span>
          <span className="font-bold text-slate-900">{occupancyPct}%</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${
              occupancyPct > 85 ? 'bg-amber-500' : 'bg-primary-600'
            }`}
            style={{ width: `${occupancyPct}%` }}
          />
        </div>
        <div className="flex justify-between text-[11px] text-slate-500">
          <span>{occupiedBeds} occupied</span>
          <span>{totalBeds} total beds</span>
        </div>
      </div>

      {/* Reset Data for Viva/Testing */}
      <div className="p-3 border-t border-slate-100 flex items-center justify-between">
        <button
          onClick={() => {
            if (window.confirm('Reset all shifts and employee rosters to initial sample data?')) {
              resetToSampleData()
            }
          }}
          className="text-[11px] text-slate-500 hover:text-primary-700 flex items-center gap-1 font-medium transition-colors"
          title="Reset back to default demonstration records"
        >
          <RotateCcw className="w-3 h-3" />
          Reset Demo Data
        </button>
        <span className="text-[10px] text-emerald-700 font-medium flex items-center gap-1">
          <ShieldCheck className="w-3 h-3" /> Verified
        </span>
      </div>
    </aside>
  )
}
