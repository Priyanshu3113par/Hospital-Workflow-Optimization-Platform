"""
Converts predicted patient demand into required staff headcounts per shift.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Optional

from optimization.constraints import (
    Department, Shift, ShiftType, RoleType, SHIFT_DURATION_HOURS
)


# ── Staffing ratio config ──────────────────────────────────────────────────────
# Minimum floors: regardless of demand, at least this many per role per shift
MINIMUM_STAFF = {
    "Doctor": 1,
    "Nurse":  2,
}

# Default ratios by department name (patients per staff member)
DEFAULT_RATIOS: dict[str, dict] = {
    "emergency":    {"patients_per_doctor": 8,  "patients_per_nurse": 4},
    "general_ward": {"patients_per_doctor": 10, "patients_per_nurse": 6},
    "icu":          {"patients_per_doctor": 4,  "patients_per_nurse": 2},
    "pediatrics":   {"patients_per_doctor": 8,  "patients_per_nurse": 5},
}


class StaffAllocator:
    """
    Translates forecast demand into staffing requirements per shift.

    Parameters
    ----------
    departments : list of Department objects from the DB / problem definition
    """

    def __init__(self, departments: list[Department]) -> None:
        self._dept_map: dict[int, Department] = {d.id: d for d in departments}

    def calculate_required_staff(
        self,
        predicted_patients: float,
        department: Department,
    ) -> dict[str, int]:
        """
        Compute required doctor and nurse counts for one shift.

        Parameters
        ----------
        predicted_patients : average patients expected during the shift
        department         : Department object with ratio config

        Returns
        -------
        dict: {'doctor_count': int, 'nurse_count': int, 'total': int}
        """
        doctors = math.ceil(predicted_patients / department.patients_per_doctor)
        nurses  = math.ceil(predicted_patients / department.patients_per_nurse)

        doctors = max(doctors, MINIMUM_STAFF["Doctor"])
        nurses  = max(nurses,  MINIMUM_STAFF["Nurse"])

        return {
            "doctor_count": doctors,
            "nurse_count":  nurses,
            "total":        doctors + nurses,
        }

    def generate_shift_requirements(
        self,
        forecast_df,          # pd.DataFrame: columns [date, shift_type, dept_id, predicted_patients]
        planning_horizon_days: int = 7,
        start_date: Optional[date] = None,
    ) -> list[Shift]:
        """
        Generate a list of Shift objects from a forecast DataFrame.

        The DataFrame must have columns:
            date (date), shift_type (int 0/1/2), department_id (int),
            predicted_patients (float)

        Returns
        -------
        list[Shift] ready for HospitalScheduler
        """
        shifts = []
        shift_id = 1

        for _, row in forecast_df.iterrows():
            dept = self._dept_map.get(int(row["department_id"]))
            if dept is None:
                continue

            staff = self.calculate_required_staff(
                float(row["predicted_patients"]), dept
            )

            shifts.append(Shift(
                id             = shift_id,
                date           = row["date"] if isinstance(row["date"], date) else row["date"].date(),
                department_id  = int(row["department_id"]),
                shift_type     = ShiftType(int(row["shift_type"])),
                required_staff = staff["total"],
                min_qualified  = staff["doctor_count"],
            ))
            shift_id += 1

        return shifts

    def build_default_shifts(
        self,
        planning_horizon_days: int = 7,
        start_date: Optional[date] = None,
        base_demand: Optional[dict[int, float]] = None,
    ) -> list[Shift]:
        """
        Build a simple 7-day shift list using fixed baseline demand per department.
        Useful for testing when no forecast DataFrame is available.

        Parameters
        ----------
        base_demand : dict of department_id → avg patients per shift (optional)
        """
        if start_date is None:
            start_date = date.today()

        default_demand = base_demand or {
            d.id: 20.0 for d in self._dept_map.values()
        }

        shifts = []
        sid = 1
        for day_offset in range(planning_horizon_days):
            d = start_date + timedelta(days=day_offset)
            for dept_id, dept in self._dept_map.items():
                for stype in ShiftType:
                    demand = default_demand.get(dept_id, 20.0)
                    staff  = self.calculate_required_staff(demand, dept)
                    shifts.append(Shift(
                        id             = sid,
                        date           = d,
                        department_id  = dept_id,
                        shift_type     = stype,
                        required_staff = staff["total"],
                        min_qualified  = staff["doctor_count"],
                    ))
                    sid += 1

        return shifts
