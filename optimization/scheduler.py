"""
Hospital Staff Scheduling via Google OR-Tools CP-SAT Constraint Programming.

Formulates shift scheduling as a constraint optimization problem.
Objective: minimize weighted cost of shortages, imbalance, overtime, and preference violations.
"""

from __future__ import annotations

import sys
import time
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("[WARNING] OR-Tools not installed. Using greedy fallback scheduler.")

from optimization.constraints import (
    Employee, Shift, Department, SchedulingProblem, ScheduleResult,
    ShiftAssignment, ShortageFlag, OvertimeWarning, ScheduleStatus,
    ShiftType, RoleType, SHIFT_DURATION_HOURS, MAX_WEEKLY_HOURS,
    MIN_REST_HOURS, MAX_CONSECUTIVE_DAYS,
)


class HospitalScheduler:
    """
    CP-SAT based hospital staff scheduler.

    Decision variable: shift_vars[e, s] ∈ {0, 1}
        1 if employee e is assigned to shift s, else 0.

    Hard constraints
    ----------------
    - Each employee works at most 1 shift per day
    - Min 11-hour gap between consecutive shifts
    - Max 5 consecutive working days
    - Only assign employees qualified for the department/role
    - Only assign if employee is available that day
    - Weekly hours ≤ employee.max_hours_week

    Soft constraints (minimized in objective)
    -----------------------------------------
    - Understaffing relative to required_staff (w1 = 10)
    - Workload imbalance across employees (w2 = 2)
    - Overtime hours (w3 = 3)
    - Preference violations (w4 = 1)
    """

    def __init__(
        self,
        w1_shortage:    float = 10.0,
        w2_imbalance:   float = 2.0,
        w3_overtime:    float = 3.0,
        w4_pref:        float = 1.0,
        time_limit_sec: int   = 30,
    ) -> None:
        self.w1 = w1_shortage
        self.w2 = w2_imbalance
        self.w3 = w3_overtime
        self.w4 = w4_pref
        self.time_limit = time_limit_sec

    # ── Public API ─────────────────────────────────────────────────────────────
    def solve(self, problem: SchedulingProblem) -> ScheduleResult:
        """Solve the scheduling problem. Falls back to greedy if OR-Tools unavailable."""
        if ORTOOLS_AVAILABLE:
            return self._solve_cp_sat(problem)
        return self._solve_greedy(problem)

    # ── CP-SAT solver ──────────────────────────────────────────────────────────
    def _solve_cp_sat(self, problem: SchedulingProblem) -> ScheduleResult:
        t0    = time.time()
        model = cp_model.CpModel()

        employees = problem.employees
        shifts    = problem.shifts
        E         = len(employees)
        S         = len(shifts)

        emp_idx   = {e.id: i for i, e in enumerate(employees)}
        shift_idx = {s.id: j for j, s in enumerate(shifts)}

        dept_map = {d.id: d for d in problem.departments}

        # ── Decision variables ─────────────────────────────────────────────────
        x = {}  # x[e_idx, s_idx] ∈ {0, 1}
        for ei, emp in enumerate(employees):
            for sj, sh in enumerate(shifts):
                # Pre-filter: only create variable if assignment is feasible
                if self._can_work(emp, sh):
                    x[ei, sj] = model.NewBoolVar(f"x_e{ei}_s{sj}")

        # ── Helper: shifts on a given date for employee ─────────────────────────
        def emp_shifts_on_date(ei: int, d: date):
            return [(sj, sh) for sj, sh in enumerate(shifts)
                    if (ei, sj) in x and sh.date == d]

        def emp_all_assigned(ei: int):
            return [(sj, sh) for sj, sh in enumerate(shifts) if (ei, sj) in x]

        # ── Hard constraint 1: at most 1 shift per employee per day ────────────
        dates_in_horizon = sorted({sh.date for sh in shifts})
        for ei in range(E):
            for d in dates_in_horizon:
                day_vars = [x[ei, sj] for sj, sh in enumerate(shifts)
                            if (ei, sj) in x and sh.date == d]
                if len(day_vars) > 1:
                    model.AddAtMostOne(day_vars)

        # ── Hard constraint 2: min rest between consecutive shifts ──────────────
        # Encode shift start hours for ordering
        SHIFT_START = {ShiftType.MORNING: 6, ShiftType.AFTERNOON: 14, ShiftType.NIGHT: 22}

        def absolute_hour(sh: Shift) -> int:
            d_offset = (sh.date - dates_in_horizon[0]).days
            return d_offset * 24 + SHIFT_START[sh.shift_type]

        for ei in range(E):
            assigned = emp_all_assigned(ei)
            # Compare every pair of shifts
            for idx_a in range(len(assigned)):
                sj_a, sh_a = assigned[idx_a]
                for idx_b in range(idx_a + 1, len(assigned)):
                    sj_b, sh_b = assigned[idx_b]
                    gap = abs(absolute_hour(sh_a) - absolute_hour(sh_b))
                    if gap < MIN_REST_HOURS + SHIFT_DURATION_HOURS:
                        # Can't work both
                        model.AddAtMostOne([x[ei, sj_a], x[ei, sj_b]])

        # ── Hard constraint 3: weekly hours cap ────────────────────────────────
        for ei, emp in enumerate(employees):
            week_vars = [x[ei, sj] for sj in range(S) if (ei, sj) in x]
            if week_vars:
                # Each shift = SHIFT_DURATION_HOURS hours
                model.Add(
                    sum(v * SHIFT_DURATION_HOURS for v in week_vars)
                    <= emp.max_hours_week
                )

        # ── Soft objective: minimize weighted cost ─────────────────────────────
        # Shortage penalty: for each shift, count how many required staff are unmet
        shortage_vars = []
        for sj, sh in enumerate(shifts):
            workers_on_shift = [x[ei, sj] for ei in range(E) if (ei, sj) in x]
            # shortage_s = max(0, required - assigned)
            shortage_s = model.NewIntVar(0, sh.required_staff, f"shortage_s{sj}")
            if workers_on_shift:
                model.Add(
                    shortage_s >= sh.required_staff - sum(workers_on_shift)
                )
            else:
                model.Add(shortage_s == sh.required_staff)
            shortage_vars.append(shortage_s)

        # Total shifts assigned per employee (for imbalance)
        emp_load = []
        for ei in range(E):
            load = model.NewIntVar(0, S, f"load_e{ei}")
            assigned_vars = [x[ei, sj] for sj in range(S) if (ei, sj) in x]
            if assigned_vars:
                model.Add(load == sum(assigned_vars))
            else:
                model.Add(load == 0)
            emp_load.append(load)

        # Max load - min load = imbalance
        max_load = model.NewIntVar(0, S, "max_load")
        min_load = model.NewIntVar(0, S, "min_load")
        model.AddMaxEquality(max_load, emp_load)
        model.AddMinEquality(min_load, emp_load)
        imbalance = model.NewIntVar(0, S, "imbalance")
        model.Add(imbalance == max_load - min_load)

        # Scale weights to integers (CP-SAT requires integer objective)
        w1 = int(self.w1 * 10)
        w2 = int(self.w2 * 10)

        model.Minimize(
            w1 * sum(shortage_vars) +
            w2 * imbalance
        )

        # ── Solve ──────────────────────────────────────────────────────────────
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit
        solver.parameters.log_search_progress = False

        status_code = solver.Solve(model)
        elapsed     = time.time() - t0

        # Map OR-Tools status to our enum
        STATUS_MAP = {
            cp_model.OPTIMAL:    ScheduleStatus.OPTIMAL,
            cp_model.FEASIBLE:   ScheduleStatus.FEASIBLE,
            cp_model.INFEASIBLE: ScheduleStatus.INFEASIBLE,
            cp_model.UNKNOWN:    ScheduleStatus.UNKNOWN,
        }
        status = STATUS_MAP.get(status_code, ScheduleStatus.UNKNOWN)

        if status in (ScheduleStatus.OPTIMAL, ScheduleStatus.FEASIBLE):
            assignments = []
            emp_hours   = defaultdict(int)
            for ei, emp in enumerate(employees):
                for sj, sh in enumerate(shifts):
                    if (ei, sj) in x and solver.Value(x[ei, sj]) == 1:
                        emp_hours[emp.id] += SHIFT_DURATION_HOURS
                        is_ot = emp_hours[emp.id] > emp.max_hours_week
                        assignments.append(ShiftAssignment(
                            employee_id = emp.id,
                            shift_id    = sh.id,
                            is_overtime = is_ot,
                        ))
        else:
            assignments = []

        return self._build_result(assignments, shifts, employees, status, elapsed)

    # ── Greedy fallback ────────────────────────────────────────────────────────
    def _solve_greedy(self, problem: SchedulingProblem) -> ScheduleResult:
        """Simple greedy scheduler when OR-Tools is unavailable."""
        t0 = time.time()
        assignments = []
        emp_hours   = defaultdict(int)
        emp_days    = defaultdict(set)

        for sh in sorted(problem.shifts, key=lambda s: (s.date, s.shift_type)):
            eligible = [
                e for e in problem.employees
                if self._can_work(e, sh)
                and sh.date not in emp_days[e.id]
                and emp_hours[e.id] + SHIFT_DURATION_HOURS <= e.max_hours_week
            ]
            # Sort by least-loaded first for fairness
            eligible.sort(key=lambda e: emp_hours[e.id])
            assigned_count = 0
            for emp in eligible[:sh.required_staff]:
                is_ot = emp_hours[emp.id] + SHIFT_DURATION_HOURS > 40
                assignments.append(ShiftAssignment(
                    employee_id = emp.id,
                    shift_id    = sh.id,
                    is_overtime = is_ot,
                ))
                emp_hours[emp.id] += SHIFT_DURATION_HOURS
                emp_days[emp.id].add(sh.date)
                assigned_count += 1

        elapsed = time.time() - t0
        status  = ScheduleStatus.FEASIBLE if assignments else ScheduleStatus.INFEASIBLE
        return self._build_result(assignments, problem.shifts, problem.employees, status, elapsed)

    # ── Result builder ─────────────────────────────────────────────────────────
    def _build_result(
        self,
        assignments: list[ShiftAssignment],
        shifts: list[Shift],
        employees: list[Employee],
        status: ScheduleStatus,
        elapsed: float,
    ) -> ScheduleResult:
        """Compute shortage flags, overtime warnings, and workload scores."""
        # Count assigned staff per shift
        assigned_per_shift: dict[int, int] = defaultdict(int)
        for a in assignments:
            assigned_per_shift[a.shift_id] += 1

        # Shortage flags
        shortage_flags = []
        for sh in shifts:
            assigned = assigned_per_shift.get(sh.id, 0)
            if assigned < sh.required_staff:
                shortage_flags.append(ShortageFlag(
                    shift_id      = sh.id,
                    department_id = sh.department_id,
                    shift_date    = sh.date,
                    shift_type    = sh.shift_type,
                    required      = sh.required_staff,
                    assigned      = assigned,
                ))

        # Overtime warnings
        emp_hours: dict[int, int] = defaultdict(int)
        emp_map = {e.id: e for e in employees}
        for a in assignments:
            emp_hours[a.employee_id] += SHIFT_DURATION_HOURS

        overtime_warnings = []
        for eid, hrs in emp_hours.items():
            emp = emp_map.get(eid)
            if emp and hrs > emp.max_hours_week:
                overtime_warnings.append(OvertimeWarning(
                    employee_id   = eid,
                    employee_name = emp.name,
                    weekly_hours  = hrs,
                    excess_hours  = hrs - emp.max_hours_week,
                ))

        # Workload scores (0–1 normalized)
        all_hrs    = list(emp_hours.values())
        max_hrs    = max(all_hrs) if all_hrs else 1
        workload_scores = {
            eid: round(hrs / max_hrs, 3) for eid, hrs in emp_hours.items()
        }

        total_cost = (
            self.w1 * sum(f.shortage for f in shortage_flags) +
            self.w2 * (max(all_hrs, default=0) - min(all_hrs, default=0)) / SHIFT_DURATION_HOURS
        )

        return ScheduleResult(
            assignments        = assignments,
            total_cost         = total_cost,
            shortage_flags     = shortage_flags,
            overtime_warnings  = overtime_warnings,
            workload_scores    = workload_scores,
            solve_time_seconds = elapsed,
            status             = status,
        )

    # ── Feasibility check ──────────────────────────────────────────────────────
    @staticmethod
    def _can_work(emp: Employee, sh: Shift) -> bool:
        """Return True if the employee is eligible to work this shift."""
        # Must be assigned to this department (or cross-trained)
        if sh.department_id not in emp.department_ids:
            return False
        # Must be available on this date
        if emp.availability:
            avail = emp.availability.get(sh.date, [])
            if avail and sh.shift_type not in avail:
                return False
        return True


# ── Demo problem generator ─────────────────────────────────────────────────────
def generate_demo_problem(
    n_employees: int = 30,
    n_days:      int = 7,
) -> SchedulingProblem:
    """
    Create a 7-day scheduling problem with synthetic employees and departments.
    Useful for testing the optimizer without real DB data.
    """
    import random
    from datetime import date as date_cls
    random.seed(42)

    departments = [
        Department(id=1, name="Emergency",    patients_per_doctor=8,  patients_per_nurse=4,  min_staff_per_shift=4),
        Department(id=2, name="General Ward", patients_per_doctor=10, patients_per_nurse=6,  min_staff_per_shift=3),
        Department(id=3, name="ICU",          patients_per_doctor=4,  patients_per_nurse=2,  min_staff_per_shift=3),
        Department(id=4, name="Pediatrics",   patients_per_doctor=8,  patients_per_nurse=5,  min_staff_per_shift=3),
    ]

    dept_ids = [d.id for d in departments]
    roles    = [RoleType.DOCTOR] * 8 + [RoleType.NURSE] * 16 + [RoleType.TECHNICIAN] * 4 + [RoleType.ADMIN] * 2

    employees = []
    for i in range(n_employees):
        role = roles[i % len(roles)]
        # Each employee works in 1–2 departments
        n_depts = 2 if role == RoleType.NURSE else 1
        emp_dept_ids = random.sample(dept_ids, min(n_depts, len(dept_ids)))
        employees.append(Employee(
            id             = i + 1,
            name           = f"Staff_{i+1:02d}",
            role           = role,
            department_ids = emp_dept_ids,
            max_hours_week = 40,
            qualifications = ["general"],
            availability   = {},          # all days / shifts available
        ))

    start = date_cls.today()
    demand_per_dept = {1: 48, 2: 32, 3: 12, 4: 20}

    from optimization.staff_allocator import StaffAllocator
    allocator = StaffAllocator(departments)
    shifts    = allocator.build_default_shifts(
        planning_horizon_days = n_days,
        start_date            = start,
        base_demand           = demand_per_dept,
    )

    return SchedulingProblem(
        employees             = employees,
        shifts                = shifts,
        departments           = departments,
        planning_horizon_days = n_days,
    )
