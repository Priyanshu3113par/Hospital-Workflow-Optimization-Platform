"""
Dataclasses, enums, and constraint definitions for the scheduling optimizer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import IntEnum
from typing import Optional


# ── Enumerations ───────────────────────────────────────────────────────────────

class ShiftType(IntEnum):
    MORNING   = 0   # 06:00–14:00
    AFTERNOON = 1   # 14:00–22:00
    NIGHT     = 2   # 22:00–06:00


class RoleType(IntEnum):
    DOCTOR     = 0
    NURSE      = 1
    TECHNICIAN = 2
    ADMIN      = 3


class ScheduleStatus(IntEnum):
    OPTIMAL    = 0
    FEASIBLE   = 1
    INFEASIBLE = 2
    UNKNOWN    = 3


SHIFT_DURATION_HOURS = 8   # each shift is 8 hours
MAX_WEEKLY_HOURS     = 48  # contractual cap
MIN_REST_HOURS       = 11  # mandatory rest between shifts
MAX_CONSECUTIVE_DAYS = 5   # no more than 5 consecutive working days

SHIFT_LABELS = {ShiftType.MORNING: "Morning", ShiftType.AFTERNOON: "Afternoon", ShiftType.NIGHT: "Night"}
ROLE_LABELS  = {RoleType.DOCTOR: "Doctor", RoleType.NURSE: "Nurse",
                RoleType.TECHNICIAN: "Technician", RoleType.ADMIN: "Admin"}


# ── Core data structures ───────────────────────────────────────────────────────

@dataclass
class Department:
    id:                  int
    name:                str
    patients_per_doctor: float = 8.0
    patients_per_nurse:  float = 4.0
    min_staff_per_shift: int   = 3


@dataclass
class Employee:
    id:              int
    name:            str
    role:            RoleType
    department_ids:  list[int]           = field(default_factory=list)
    max_hours_week:  int                 = 40
    qualifications:  list[str]           = field(default_factory=list)
    # availability[date] = list of available ShiftTypes
    availability:    dict[date, list[ShiftType]] = field(default_factory=dict)


@dataclass
class Shift:
    id:               int
    date:             date
    department_id:    int
    shift_type:       ShiftType
    required_staff:   int = 3
    min_qualified:    int = 1


@dataclass
class SchedulingProblem:
    employees:              list[Employee]
    shifts:                 list[Shift]
    departments:            list[Department]
    planning_horizon_days:  int = 7


@dataclass
class ShiftAssignment:
    employee_id:  int
    shift_id:     int
    is_overtime:  bool = False


@dataclass
class ShortageFlag:
    shift_id:          int
    department_id:     int
    shift_date:        date
    shift_type:        ShiftType
    required:          int
    assigned:          int

    @property
    def shortage(self) -> int:
        return max(0, self.required - self.assigned)

    def __str__(self) -> str:
        return (f"SHORTAGE | {self.shift_date} {SHIFT_LABELS[self.shift_type]} | "
                f"dept={self.department_id} | need={self.required} got={self.assigned}")


@dataclass
class OvertimeWarning:
    employee_id:    int
    employee_name:  str
    weekly_hours:   float
    excess_hours:   float

    def __str__(self) -> str:
        return (f"OVERTIME | {self.employee_name} | "
                f"{self.weekly_hours:.0f}h (excess={self.excess_hours:.0f}h)")


@dataclass
class ScheduleResult:
    assignments:        list[ShiftAssignment]
    total_cost:         float
    shortage_flags:     list[ShortageFlag]
    overtime_warnings:  list[OvertimeWarning]
    workload_scores:    dict[int, float]      # employee_id → score (0–1)
    solve_time_seconds: float
    status:             ScheduleStatus

    @property
    def is_feasible(self) -> bool:
        return self.status in (ScheduleStatus.OPTIMAL, ScheduleStatus.FEASIBLE)

    def summary(self) -> str:
        lines = [
            f"Status        : {self.status.name}",
            f"Total cost    : {self.total_cost:.2f}",
            f"Assignments   : {len(self.assignments)}",
            f"Shortages     : {len(self.shortage_flags)}",
            f"Overtime warns: {len(self.overtime_warnings)}",
            f"Solve time    : {self.solve_time_seconds:.2f}s",
        ]
        return "\n".join(lines)
