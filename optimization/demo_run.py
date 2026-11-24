"""
Demo runner — generates a 7-day scheduling problem and runs the optimizer.
Run: python optimization/demo_run.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from optimization.scheduler import HospitalScheduler, generate_demo_problem
from optimization.workload_monitor import WorkloadMonitor


def main():
    print("=" * 60)
    print("  Hospital Workforce Optimizer — Demo Run")
    print("=" * 60)

    # 1. Build a 7-day scheduling problem
    print("\n[1] Generating demo scheduling problem (30 employees, 7 days) …")
    problem = generate_demo_problem(n_employees=30, n_days=7)
    print(f"    Employees : {len(problem.employees)}")
    print(f"    Shifts    : {len(problem.shifts)}")
    print(f"    Departments: {len(problem.departments)}")

    # 2. Run OR-Tools (or greedy fallback)
    print("\n[2] Running scheduler …")
    scheduler = HospitalScheduler(time_limit_sec=15)
    result    = scheduler.solve(problem)

    print("\n── Schedule Result ──────────────────────────────────────────")
    print(result.summary())

    # 3. Print shortage flags
    if result.shortage_flags:
        print(f"\n── Shortage Flags ({len(result.shortage_flags)}) ──")
        for f in result.shortage_flags[:5]:
            print(f"  {f}")
    else:
        print("\n✓ No staffing shortages!")

    # 4. Print overtime warnings
    if result.overtime_warnings:
        print(f"\n── Overtime Warnings ({len(result.overtime_warnings)}) ──")
        for w in result.overtime_warnings[:5]:
            print(f"  {w}")
    else:
        print("✓ No overtime violations!")

    # 5. Workload report
    print("\n[3] Computing workload report …")
    monitor = WorkloadMonitor(problem.employees, problem.shifts)
    report  = monitor.generate_workload_report(result.assignments)
    print("\n── Top 10 Employees by Burnout Risk ─────────────────────────")
    print(report.head(10).to_string(index=False))

    print("\n✓ Demo complete.")


if __name__ == "__main__":
    main()
