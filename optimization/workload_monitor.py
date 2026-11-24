"""
Workload monitoring — detects overtime, rest violations, and estimates burnout risk.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd

from optimization.constraints import (
    Employee, ShiftAssignment, Shift,
    SHIFT_DURATION_HOURS, MAX_WEEKLY_HOURS, MIN_REST_HOURS,
    ShiftType,
)

SHIFT_START_HOUR = {ShiftType.MORNING: 6, ShiftType.AFTERNOON: 14, ShiftType.NIGHT: 22}


@dataclass
class RestViolation:
    employee_id:   int
    employee_name: str
    shift_a_id:    int
    shift_b_id:    int
    actual_rest_h: float
    required_rest_h: float = float(MIN_REST_HOURS)


@dataclass
class BurnoutRiskScore:
    employee_id:      int
    employee_name:    str
    score:            float   # 0–100
    weekly_hours:     float
    consecutive_days: int
    night_shifts:     int
    rest_violations:  int
    risk_level:       str     # LOW / MEDIUM / HIGH / CRITICAL


class WorkloadMonitor:
    """
    Analyses shift assignments to identify overtime, insufficient rest,
    and compute a composite burnout risk indicator per employee.
    """

    def __init__(
        self,
        employees: list[Employee],
        shifts:    list[Shift],
    ) -> None:
        self._emp_map:   dict[int, Employee] = {e.id: e for e in employees}
        self._shift_map: dict[int, Shift]    = {s.id: s for s in shifts}

    # ── Weekly hours ───────────────────────────────────────────────────────────
    def compute_weekly_hours(
        self,
        assignments: list[ShiftAssignment],
        employee_id: int,
    ) -> float:
        """Total hours worked this week by an employee."""
        return sum(
            SHIFT_DURATION_HOURS
            for a in assignments
            if a.employee_id == employee_id
        )

    # ── Overtime detection ─────────────────────────────────────────────────────
    def detect_overtime(
        self,
        assignments: list[ShiftAssignment],
        threshold:   int = 48,
    ) -> list[dict]:
        """
        Return employees who exceed `threshold` hours in a week.
        """
        hours_per_emp: dict[int, float] = defaultdict(float)
        for a in assignments:
            hours_per_emp[a.employee_id] += SHIFT_DURATION_HOURS

        results = []
        for emp_id, hrs in hours_per_emp.items():
            if hrs > threshold:
                emp = self._emp_map.get(emp_id)
                results.append({
                    "employee_id":   emp_id,
                    "employee_name": emp.name if emp else f"Emp#{emp_id}",
                    "weekly_hours":  hrs,
                    "excess_hours":  hrs - threshold,
                    "max_allowed":   threshold,
                })
        return sorted(results, key=lambda r: r["excess_hours"], reverse=True)

    # ── Rest violation detection ───────────────────────────────────────────────
    def detect_rest_violations(
        self,
        assignments: list[ShiftAssignment],
    ) -> list[RestViolation]:
        """
        Find consecutive shift pairs where the gap is less than MIN_REST_HOURS.
        """
        # Group shifts per employee
        emp_shifts: dict[int, list[Shift]] = defaultdict(list)
        for a in assignments:
            sh = self._shift_map.get(a.shift_id)
            if sh:
                emp_shifts[a.employee_id].append(sh)

        violations = []
        for emp_id, shfts in emp_shifts.items():
            # Sort by absolute start time
            shfts_sorted = sorted(
                shfts,
                key=lambda s: (s.date.toordinal() * 24 + SHIFT_START_HOUR[s.shift_type])
            )
            emp = self._emp_map.get(emp_id)
            for i in range(len(shfts_sorted) - 1):
                s1 = shfts_sorted[i]
                s2 = shfts_sorted[i + 1]
                start1 = s1.date.toordinal() * 24 + SHIFT_START_HOUR[s1.shift_type]
                start2 = s2.date.toordinal() * 24 + SHIFT_START_HOUR[s2.shift_type]
                gap = start2 - (start1 + SHIFT_DURATION_HOURS)
                if gap < MIN_REST_HOURS:
                    violations.append(RestViolation(
                        employee_id     = emp_id,
                        employee_name   = emp.name if emp else f"Emp#{emp_id}",
                        shift_a_id      = s1.id,
                        shift_b_id      = s2.id,
                        actual_rest_h   = float(gap),
                    ))
        return violations

    # ── Burnout risk ───────────────────────────────────────────────────────────
    def compute_burnout_risk(
        self,
        assignments: list[ShiftAssignment],
    ) -> list[BurnoutRiskScore]:
        """
        Composite burnout risk score (0–100) per employee.

        Score components
        ----------------
        - Weekly hours component   (0–40 pts)
        - Night shifts (last 7d)   (0–20 pts)
        - Consecutive working days (0–25 pts)
        - Rest violations          (0–15 pts)
        """
        hours_per_emp:  dict[int, float] = defaultdict(float)
        night_per_emp:  dict[int, int]   = defaultdict(int)
        days_per_emp:   dict[int, set]   = defaultdict(set)

        for a in assignments:
            sh = self._shift_map.get(a.shift_id)
            if sh is None:
                continue
            hours_per_emp[a.employee_id] += SHIFT_DURATION_HOURS
            days_per_emp[a.employee_id].add(sh.date)
            if sh.shift_type == ShiftType.NIGHT:
                night_per_emp[a.employee_id] += 1

        violations_map: dict[int, int] = defaultdict(int)
        for v in self.detect_rest_violations(assignments):
            violations_map[v.employee_id] += 1

        scores = []
        for emp_id, emp in self._emp_map.items():
            hrs   = hours_per_emp.get(emp_id, 0.0)
            nights = night_per_emp.get(emp_id, 0)
            days  = days_per_emp.get(emp_id, set())

            # Consecutive days (simple: total distinct days)
            consec = len(days)

            # Score components
            hrs_score   = min(40.0, (hrs / MAX_WEEKLY_HOURS) * 40)
            night_score = min(20.0, nights * 5)
            day_score   = min(25.0, consec * 4)
            viol_score  = min(15.0, violations_map[emp_id] * 7.5)

            total = hrs_score + night_score + day_score + viol_score

            if total < 33:
                level = "LOW"
            elif total < 55:
                level = "MEDIUM"
            elif total < 75:
                level = "HIGH"
            else:
                level = "CRITICAL"

            scores.append(BurnoutRiskScore(
                employee_id      = emp_id,
                employee_name    = emp.name,
                score            = round(total, 1),
                weekly_hours     = hrs,
                consecutive_days = consec,
                night_shifts     = nights,
                rest_violations  = violations_map[emp_id],
                risk_level       = level,
            ))

        return sorted(scores, key=lambda s: s.score, reverse=True)

    # ── Full report ────────────────────────────────────────────────────────────
    def generate_workload_report(
        self,
        assignments: list[ShiftAssignment],
    ) -> pd.DataFrame:
        """Return a per-employee DataFrame with all workload stats."""
        burnout_scores = {b.employee_id: b for b in self.compute_burnout_risk(assignments)}
        rows = []
        for emp_id, emp in self._emp_map.items():
            b = burnout_scores.get(emp_id)
            rows.append({
                "employee_id":    emp_id,
                "name":           emp.name,
                "role":           emp.role.name,
                "weekly_hours":   b.weekly_hours     if b else 0,
                "night_shifts":   b.night_shifts     if b else 0,
                "consecutive_days": b.consecutive_days if b else 0,
                "rest_violations": b.rest_violations  if b else 0,
                "burnout_score":  b.score            if b else 0.0,
                "risk_level":     b.risk_level       if b else "LOW",
            })
        return pd.DataFrame(rows).sort_values("burnout_score", ascending=False)
