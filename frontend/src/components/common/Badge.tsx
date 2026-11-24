import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'purple' | 'teal' | 'neutral'
  className?: string
}

export default function Badge({ children, variant = 'teal', className = '' }: BadgeProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case 'success':
        return 'bg-emerald-50 text-emerald-800 border-emerald-200'
      case 'warning':
        return 'bg-amber-50 text-amber-800 border-amber-200'
      case 'danger':
        return 'bg-rose-50 text-rose-800 border-rose-200'
      case 'purple':
        return 'bg-purple-50 text-purple-800 border-purple-200'
      case 'teal':
        return 'bg-teal-50 text-teal-800 border-teal-200'
      case 'info':
        return 'bg-sky-50 text-sky-800 border-sky-200'
      case 'neutral':
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200'
    }
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold border ${getVariantStyles()} ${className}`}>
      {children}
    </span>
  )
}
