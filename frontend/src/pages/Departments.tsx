import React, { useState } from 'react'
import {
  Building2,
  Plus,
  Users,
  BedDouble,
  HeartPulse,
  Settings,
  Edit2,
  Trash2,
  SlidersHorizontal,
  CheckCircle2,
  AlertTriangle,
  Info
} from 'lucide-react'
import Badge from '@/components/common/Badge'
import Modal from '@/components/common/Modal'
import { useHospital } from '@/context/HospitalContext'
import { Department } from '@/types'

export default function Departments() {
  const {
    departments,
    employees,
    addDepartment,
    updateDepartment,
    deleteDepartment,
    updateOccupancy,
  } = useHospital()

  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingDept, setEditingDept] = useState<Department | null>(null)

  const [newDeptForm, setNewDeptForm] = useState({
    name: '',
    code: '',
    rooms_capacity: 15,
    beds_total: 25,
    current_occupancy: 18,
    min_staff_per_shift: 3,
    patients_per_doctor: 8.0,
    patients_per_nurse: 4.0,
    description: '',
  })

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newDeptForm.name.trim() || !newDeptForm.code.trim()) return

    addDepartment({
      name: newDeptForm.name.trim(),
      code: newDeptForm.code.trim().toUpperCase(),
      rooms_capacity: Number(newDeptForm.rooms_capacity),
      beds_total: Number(newDeptForm.beds_total),
      current_occupancy: Number(newDeptForm.current_occupancy),
      min_staff_per_shift: Number(newDeptForm.min_staff_per_shift),
      patients_per_doctor: Number(newDeptForm.patients_per_doctor),
      patients_per_nurse: Number(newDeptForm.patients_per_nurse),
      description: newDeptForm.description.trim() || 'Clinical specialty inpatient unit.',
      is_active: true,
    })

    setIsAddModalOpen(false)
    setNewDeptForm({
      name: '',
      code: '',
      rooms_capacity: 15,
      beds_total: 25,
      current_occupancy: 18,
      min_staff_per_shift: 3,
      patients_per_doctor: 8.0,
      patients_per_nurse: 4.0,
      description: '',
    })
  }

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingDept) return

    updateDepartment(editingDept.id, {
      name: editingDept.name,
      code: editingDept.code,
      rooms_capacity: Number(editingDept.rooms_capacity),
      beds_total: Number(editingDept.beds_total),
      min_staff_per_shift: Number(editingDept.min_staff_per_shift),
      patients_per_doctor: Number(editingDept.patients_per_doctor),
      patients_per_nurse: Number(editingDept.patients_per_nurse),
      description: editingDept.description,
    })

    setEditingDept(null)
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Clinical Departments & Hospital Infrastructure
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure room capacities, physical bed infrastructure, acuity staffing ratios, and continuous baseline requirements.
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          className="btn-primary"
        >
          <Plus className="w-4 h-4" />
          Add Clinical Unit
        </button>
      </div>

      {/* Department Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {departments.map((dept) => {
          const occPct = Math.round((dept.current_occupancy / dept.beds_total) * 100)
          const deptStaff = employees.filter(e => e.department_id === dept.id && e.is_active)
          const doctorsCount = deptStaff.filter(e => e.role === 'DOCTOR').length
          const nursesCount = deptStaff.filter(e => e.role === 'NURSE').length

          // Dynamic recommended staff for currently occupied beds
          const neededDocs = Math.max(1, Math.ceil(dept.current_occupancy / dept.patients_per_doctor))
          const neededNurses = Math.max(2, Math.ceil(dept.current_occupancy / dept.patients_per_nurse))

          return (
            <div key={dept.id} className="hospital-card p-6 space-y-5">
              {/* Card Header */}
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-slate-900">{dept.name}</h3>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                      {dept.code}
                    </span>
                    <Badge variant={occPct >= 90 ? 'danger' : occPct >= 75 ? 'warning' : 'teal'}>
                      {occPct >= 90 ? 'Near Capacity' : occPct >= 75 ? 'Moderate' : 'Optimal'}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                    {dept.description}
                  </p>
                </div>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setEditingDept(dept)}
                    className="p-1.5 text-slate-400 hover:text-teal-700 hover:bg-teal-50 rounded-lg"
                    title="Edit Department Configuration"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  {departments.length > 1 && (
                    <button
                      onClick={() => {
                        if (window.confirm(`Delete ${dept.name}? Shifts associated with this unit will be cleared.`)) {
                          deleteDepartment(dept.id)
                        }
                      }}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg"
                      title="Delete Department"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Bed Occupancy Interactive Slider */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-700 flex items-center gap-1.5">
                    <BedDouble className="w-4 h-4 text-teal-700" />
                    Active Bed Occupancy Simulator
                  </span>
                  <span className="font-mono font-bold text-slate-900">
                    {dept.current_occupancy} / {dept.beds_total} beds ({occPct}%)
                  </span>
                </div>

                <input
                  type="range"
                  min="0"
                  max={dept.beds_total}
                  value={dept.current_occupancy}
                  onChange={(e) => updateOccupancy(dept.id, Number(e.target.value))}
                  className="w-full accent-teal-700 cursor-pointer"
                />

                <div className="flex justify-between text-[11px] text-slate-500">
                  <span>Rooms capacity: {dept.rooms_capacity} rooms</span>
                  <span className="text-teal-800 font-semibold">
                    Dynamic Need: {neededDocs} Docs, {neededNurses} Nurses
                  </span>
                </div>
              </div>

              {/* Acuity Ratios & Min Staff Grid */}
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="p-2.5 rounded-lg bg-white border border-slate-200 text-center">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Min Staff / Shift</span>
                  <span className="font-bold text-slate-800 text-sm mt-0.5 block">{dept.min_staff_per_shift} staff</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white border border-slate-200 text-center">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Doctor Acuity</span>
                  <span className="font-bold text-teal-900 text-sm mt-0.5 block">1 : {dept.patients_per_doctor} pts</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white border border-slate-200 text-center">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Nurse Acuity</span>
                  <span className="font-bold text-teal-900 text-sm mt-0.5 block">1 : {dept.patients_per_nurse} pts</span>
                </div>
              </div>

              {/* Department Personnel Summary */}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1.5 font-medium">
                  <Users className="w-3.5 h-3.5 text-slate-400" />
                  Assigned Roster: <strong>{deptStaff.length} Total</strong> ({doctorsCount} Docs, {nursesCount} Nurses)
                </span>
                <span className="text-emerald-700 font-semibold">Continuous 24/7 Coverage</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Add Department Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Register New Clinical Department"
        subtitle="Configure physical rooms, beds, and patient-to-staff ratios."
      >
        <form onSubmit={handleCreate} className="space-y-4 text-xs">
          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2">
              <label className="block text-slate-700 mb-1 font-bold">Department Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Cardiology Care Unit"
                value={newDeptForm.name}
                onChange={(e) => setNewDeptForm({ ...newDeptForm, name: e.target.value })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Code</label>
              <input
                type="text"
                required
                placeholder="CCU"
                value={newDeptForm.code}
                onChange={(e) => setNewDeptForm({ ...newDeptForm, code: e.target.value })}
                className="input-field uppercase"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Physical Rooms</label>
              <input
                type="number"
                min="1"
                max="100"
                value={newDeptForm.rooms_capacity}
                onChange={(e) => setNewDeptForm({ ...newDeptForm, rooms_capacity: Number(e.target.value) })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Total Beds</label>
              <input
                type="number"
                min="1"
                max="200"
                value={newDeptForm.beds_total}
                onChange={(e) => setNewDeptForm({ ...newDeptForm, beds_total: Number(e.target.value) })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Initial Occupancy</label>
              <input
                type="number"
                min="0"
                max="200"
                value={newDeptForm.current_occupancy}
                onChange={(e) => setNewDeptForm({ ...newDeptForm, current_occupancy: Number(e.target.value) })}
                className="input-field"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Min Staff / Shift</label>
              <input
                type="number"
                min="1"
                max="20"
                value={newDeptForm.min_staff_per_shift}
                onChange={(e) => setNewDeptForm({ ...newDeptForm, min_staff_per_shift: Number(e.target.value) })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Patients / Doctor</label>
              <input
                type="number"
                step="0.5"
                min="1"
                max="30"
                value={newDeptForm.patients_per_doctor}
                onChange={(e) => setNewDeptForm({ ...newDeptForm, patients_per_doctor: Number(e.target.value) })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-slate-700 mb-1 font-bold">Patients / Nurse</label>
              <input
                type="number"
                step="0.5"
                min="1"
                max="20"
                value={newDeptForm.patients_per_nurse}
                onChange={(e) => setNewDeptForm({ ...newDeptForm, patients_per_nurse: Number(e.target.value) })}
                className="input-field"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-700 mb-1 font-bold">Ward Clinical Description</label>
            <input
              type="text"
              placeholder="e.g. Coronary care and post-angiography continuous telemetry monitoring."
              value={newDeptForm.description}
              onChange={(e) => setNewDeptForm({ ...newDeptForm, description: e.target.value })}
              className="input-field"
            />
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
              Create Department
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Department Modal */}
      {editingDept && (
        <Modal
          isOpen={true}
          onClose={() => setEditingDept(null)}
          title={`Edit Unit: ${editingDept.name}`}
          subtitle="Update infrastructure beds, room capacity, and clinical staffing ratios."
        >
          <form onSubmit={handleUpdate} className="space-y-4 text-xs">
            <div className="grid grid-cols-3 gap-3">
              <div className="col-span-2">
                <label className="block text-slate-700 mb-1 font-bold">Department Name</label>
                <input
                  type="text"
                  required
                  value={editingDept.name}
                  onChange={(e) => setEditingDept({ ...editingDept, name: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-bold">Code</label>
                <input
                  type="text"
                  required
                  value={editingDept.code}
                  onChange={(e) => setEditingDept({ ...editingDept, code: e.target.value })}
                  className="input-field uppercase"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-700 mb-1 font-bold">Physical Rooms</label>
                <input
                  type="number"
                  min="1"
                  value={editingDept.rooms_capacity}
                  onChange={(e) => setEditingDept({ ...editingDept, rooms_capacity: Number(e.target.value) })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-bold">Total Physical Beds</label>
                <input
                  type="number"
                  min="1"
                  value={editingDept.beds_total}
                  onChange={(e) => setEditingDept({ ...editingDept, beds_total: Number(e.target.value) })}
                  className="input-field"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-slate-700 mb-1 font-bold">Min Staff / Shift</label>
                <input
                  type="number"
                  min="1"
                  value={editingDept.min_staff_per_shift}
                  onChange={(e) => setEditingDept({ ...editingDept, min_staff_per_shift: Number(e.target.value) })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-bold">Patients / Doctor</label>
                <input
                  type="number"
                  step="0.5"
                  value={editingDept.patients_per_doctor}
                  onChange={(e) => setEditingDept({ ...editingDept, patients_per_doctor: Number(e.target.value) })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-bold">Patients / Nurse</label>
                <input
                  type="number"
                  step="0.5"
                  value={editingDept.patients_per_nurse}
                  onChange={(e) => setEditingDept({ ...editingDept, patients_per_nurse: Number(e.target.value) })}
                  className="input-field"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setEditingDept(null)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
              >
                Save Configuration
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
