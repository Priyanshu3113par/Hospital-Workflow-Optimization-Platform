import React, { useState } from 'react'
import {
  Users,
  UserPlus,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Edit2,
  Trash2,
  Shield,
  Clock,
  Sparkles,
  Phone,
  Mail,
  Check,
  X
} from 'lucide-react'
import Badge from '@/components/common/Badge'
import Modal from '@/components/common/Modal'
import { useHospital } from '@/context/HospitalContext'
import { Employee, RoleType } from '@/types'

export default function Employees() {
  const {
    departments,
    employees,
    addEmployee,
    updateEmployee,
    deleteEmployee,
    toggleEmployeeStatus,
    burnoutRecords,
  } = useHospital()

  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRole, setSelectedRole] = useState<string>('ALL')
  const [selectedDept, setSelectedDept] = useState<string>('ALL')

  // Modals state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null)

  // Form State for Add
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    role: 'NURSE' as RoleType,
    department_id: 1,
    max_hours_week: 40,
    qualifications: 'general_care, bls',
  })

  // Filtered employees list
  const filteredEmployees = employees.filter((emp) => {
    const matchesSearch = emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          emp.email.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = selectedRole === 'ALL' || emp.role === selectedRole
    const matchesDept = selectedDept === 'ALL' || String(emp.department_id) === selectedDept
    return matchesSearch && matchesRole && matchesDept
  })

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name.trim() || !formData.email.trim()) return

    addEmployee({
      name: formData.name.trim(),
      email: formData.email.trim(),
      phone: formData.phone.trim() || '+1 (555) 019-2834',
      role: formData.role,
      department_id: Number(formData.department_id),
      max_hours_week: Number(formData.max_hours_week),
      qualifications: formData.qualifications.split(',').map(s => s.trim()).filter(Boolean),
      is_active: true,
      created_at: new Date().toISOString(),
    })

    setIsAddModalOpen(false)
    setFormData({
      name: '',
      email: '',
      phone: '',
      role: 'NURSE',
      department_id: 1,
      max_hours_week: 40,
      qualifications: 'general_care, bls',
    })
  }

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingEmployee) return

    updateEmployee(editingEmployee.id, {
      name: editingEmployee.name,
      email: editingEmployee.email,
      role: editingEmployee.role,
      department_id: Number(editingEmployee.department_id),
      max_hours_week: Number(editingEmployee.max_hours_week),
      qualifications: Array.isArray(editingEmployee.qualifications)
        ? editingEmployee.qualifications
        : String(editingEmployee.qualifications).split(',').map((s: string) => s.trim()),
    })

    setEditingEmployee(null)
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Hospital Staff & Clinical Personnel
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Maintain clinical credentials, contract hours, department affiliations, and active workforce status.
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          className="btn-primary"
        >
          <UserPlus className="w-4 h-4" />
          Add Healthcare Professional
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="hospital-card p-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name, email, credentials..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-9"
          />
        </div>

        <div>
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="input-field"
          >
            <option value="ALL">All Clinical Roles</option>
            <option value="DOCTOR">Doctors</option>
            <option value="NURSE">Nurses</option>
            <option value="TECHNICIAN">Technicians</option>
            <option value="ADMIN">Administrators</option>
          </select>
        </div>

        <div>
          <select
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            className="input-field"
          >
            <option value="ALL">All Departments</option>
            {departments.map(d => (
              <option key={d.id} value={String(d.id)}>{d.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Employee List Table */}
      <div className="hospital-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Staff Member</th>
                <th className="py-3 px-3">Role</th>
                <th className="py-3 px-3">Department</th>
                <th className="py-3 px-3">Weekly Assigned / Cap</th>
                <th className="py-3 px-3">Burnout Risk</th>
                <th className="py-3 px-4">Clinical Qualifications</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredEmployees.map((emp) => {
                const burnout = burnoutRecords.find(b => b.employee_id === emp.id)
                const dept = departments.find(d => d.id === emp.department_id)

                return (
                  <tr key={emp.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4">
                      <div>
                        <span className="font-bold text-slate-800 text-sm">{emp.name}</span>
                        <span className="text-[11px] text-slate-400 block font-normal">{emp.email}</span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <Badge variant={
                        emp.role === 'DOCTOR' ? 'purple' :
                        emp.role === 'NURSE' ? 'teal' :
                        emp.role === 'TECHNICIAN' ? 'warning' : 'neutral'
                      }>
                        {emp.role}
                      </Badge>
                    </td>
                    <td className="py-3 px-3 text-slate-700 font-medium">
                      {dept?.name || 'Float Pool'}
                    </td>
                    <td className="py-3 px-3 font-mono">
                      <span className={`font-semibold ${
                        burnout && burnout.weekly_hours > emp.max_hours_week ? 'text-rose-600' : 'text-slate-800'
                      }`}>
                        {burnout?.weekly_hours || 0}h
                      </span>
                      <span className="text-slate-400 text-[10px]"> / {emp.max_hours_week}h max</span>
                    </td>
                    <td className="py-3 px-3">
                      {burnout && (
                        <span className={`inline-flex items-center gap-1 font-semibold text-[11px] ${
                          burnout.risk_level === 'CRITICAL' ? 'text-rose-700' :
                          burnout.risk_level === 'HIGH' ? 'text-amber-700' : 'text-emerald-700'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            burnout.risk_level === 'CRITICAL' ? 'bg-rose-500' :
                            burnout.risk_level === 'HIGH' ? 'bg-amber-500' : 'bg-emerald-500'
                          }`} />
                          {burnout.burnout_score}/100 ({burnout.risk_level})
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {emp.qualifications.map((q, idx) => (
                          <span key={idx} className="px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 border border-slate-200">
                            {q}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <button
                        onClick={() => toggleEmployeeStatus(emp.id)}
                        className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full cursor-pointer transition-colors ${
                          emp.is_active
                            ? 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
                            : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                        }`}
                        title="Click to toggle active status"
                      >
                        {emp.is_active ? <Check className="w-3 h-3 text-emerald-600" /> : <X className="w-3 h-3 text-slate-400" />}
                        {emp.is_active ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => setEditingEmployee(emp)}
                          className="p-1 rounded text-slate-400 hover:text-teal-700 hover:bg-teal-50 transition-colors"
                          title="Edit employee details"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            if (window.confirm(`Are you sure you want to remove ${emp.name} from the staff directory?`)) {
                              deleteEmployee(emp.id)
                            }
                          }}
                          className="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Delete employee"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Employee Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Register Healthcare Professional"
        subtitle="Add a clinical doctor, nurse, or technician to the hospital workforce."
      >
        <form onSubmit={handleCreate} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-700 mb-1 font-bold">Full Name & Title</label>
            <input
              type="text"
              required
              placeholder="e.g. Dr. Maya Lin, MD"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input-field"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Email Address</label>
              <input
                type="email"
                required
                placeholder="maya.lin@medcenter.org"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Contact Phone</label>
              <input
                type="text"
                placeholder="+1 (555) 019-2834"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="input-field"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Clinical Role</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value as RoleType })}
                className="input-field"
              >
                <option value="DOCTOR">Doctor / Physician</option>
                <option value="NURSE">Registered Nurse (RN)</option>
                <option value="TECHNICIAN">Clinical Technician</option>
                <option value="ADMIN">Shift Administrator</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 mb-1 font-bold">Primary Department</label>
              <select
                value={formData.department_id}
                onChange={(e) => setFormData({ ...formData, department_id: Number(e.target.value) })}
                className="input-field"
              >
                {departments.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Contract Weekly Cap (Hours)</label>
              <input
                type="number"
                min="20"
                max="60"
                value={formData.max_hours_week}
                onChange={(e) => setFormData({ ...formData, max_hours_week: Number(e.target.value) })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1 font-bold">Clinical Credentials</label>
              <input
                type="text"
                placeholder="trauma, ventilator, triage"
                value={formData.qualifications}
                onChange={(e) => setFormData({ ...formData, qualifications: e.target.value })}
                className="input-field"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsAddModalOpen(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
            >
              Save Healthcare Professional
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Employee Modal */}
      {editingEmployee && (
        <Modal
          isOpen={true}
          onClose={() => setEditingEmployee(null)}
          title={`Edit Personnel: ${editingEmployee.name}`}
          subtitle="Update contract hours, department, or clinical credentials."
        >
          <form onSubmit={handleUpdate} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Full Name</label>
              <input
                type="text"
                required
                value={editingEmployee.name}
                onChange={(e) => setEditingEmployee({ ...editingEmployee, name: e.target.value })}
                className="input-field"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-700 mb-1 font-bold">Email</label>
                <input
                  type="email"
                  required
                  value={editingEmployee.email}
                  onChange={(e) => setEditingEmployee({ ...editingEmployee, email: e.target.value })}
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-slate-700 mb-1 font-bold">Role</label>
                <select
                  value={editingEmployee.role}
                  onChange={(e) => setEditingEmployee({ ...editingEmployee, role: e.target.value as RoleType })}
                  className="input-field"
                >
                  <option value="DOCTOR">Doctor</option>
                  <option value="NURSE">Nurse</option>
                  <option value="TECHNICIAN">Technician</option>
                  <option value="ADMIN">Admin</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-700 mb-1 font-bold">Department</label>
                <select
                  value={editingEmployee.department_id}
                  onChange={(e) => setEditingEmployee({ ...editingEmployee, department_id: Number(e.target.value) })}
                  className="input-field"
                >
                  {departments.map(d => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-700 mb-1 font-bold">Max Hours / Week</label>
                <input
                  type="number"
                  min="20"
                  max="60"
                  value={editingEmployee.max_hours_week}
                  onChange={(e) => setEditingEmployee({ ...editingEmployee, max_hours_week: Number(e.target.value) })}
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-700 mb-1 font-bold">Qualifications (comma-separated)</label>
              <input
                type="text"
                value={Array.isArray(editingEmployee.qualifications) ? editingEmployee.qualifications.join(', ') : editingEmployee.qualifications}
                onChange={(e) => setEditingEmployee({ ...editingEmployee, qualifications: e.target.value.split(',').map(s => s.trim()) })}
                className="input-field"
              />
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setEditingEmployee(null)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
              >
                Save Changes
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
