import React from 'react'
import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon: LucideIcon
  iconColor?: string
  subtitle?: string
}

export default function StatCard({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  iconColor = 'text-primary-700 bg-primary-50',
  subtitle
}: StatCardProps) {
  const getChangeStyles = () => {
    if (changeType === 'positive') return 'text-emerald-700 bg-emerald-50 border-emerald-200'
    if (changeType === 'negative') return 'text-rose-700 bg-rose-50 border-rose-200'
    return 'text-slate-600 bg-slate-50 border-slate-200'
  }

  return (
    <div className="hospital-card p-5 relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div className="space-y-1.5">
          <p className="text-xs font-semibold text-slate-500 tracking-wider uppercase">{title}</p>
          <div className="flex items-baseline gap-2">
            <h3 className="text-2xl font-bold text-slate-900 tracking-tight">{value}</h3>
            {change && (
              <span className={`text-[11px] px-2 py-0.5 rounded-md border font-semibold ${getChangeStyles()}`}>
                {change}
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs text-slate-500 font-medium">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-xl border border-slate-100 ${iconColor} shrink-0`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  )
}
