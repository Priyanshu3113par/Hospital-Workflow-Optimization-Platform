"""
Synthetic Emergency Department Arrivals Data Generator
Generates 3 years of realistic hourly patient arrival data for 4 departments.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# ── Reproducibility ────────────────────────────────────────────────────────────
np.random.seed(42)

# ── Output path ────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "datasets" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "synthetic_ed_arrivals.csv"


# ── Holiday calendar (approximate US/international) ────────────────────────────
def get_holidays(years: list[int]) -> set:
    holidays = set()
    for y in years:
        holidays.update([
            datetime(y, 1, 1),   # New Year
            datetime(y, 1, 15),  # MLK Day (approx)
            datetime(y, 7, 4),   # Independence Day
            datetime(y, 10, 31), # Halloween
            datetime(y, 11, 25), # Thanksgiving (approx)
            datetime(y, 12, 24), # Christmas Eve
            datetime(y, 12, 25), # Christmas
            datetime(y, 12, 31), # New Year Eve
        ])
    return holidays


def hourly_pattern(hour: int, dept: str) -> float:
    """
    Returns a demand multiplier for a given hour of the day per department.
    Peaks modelled from real ED literature (morning and evening surges).
    """
    patterns = {
        "emergency": [
            0.45, 0.38, 0.33, 0.30, 0.32, 0.40,  # 00–05
            0.60, 0.80, 0.95, 1.00, 0.98, 0.95,  # 06–11
            0.92, 0.90, 0.88, 0.87, 0.90, 0.95,  # 12–17
            1.00, 0.98, 0.90, 0.78, 0.65, 0.52,  # 18–23
        ],
        "general_ward": [
            0.30, 0.25, 0.22, 0.20, 0.22, 0.30,
            0.50, 0.75, 0.90, 0.95, 1.00, 0.95,
            0.90, 0.88, 0.85, 0.82, 0.80, 0.78,
            0.75, 0.68, 0.58, 0.48, 0.38, 0.32,
        ],
        "icu": [
            0.80, 0.78, 0.76, 0.75, 0.76, 0.80,  # ICU relatively flat (continuous care)
            0.88, 0.95, 1.00, 1.00, 0.98, 0.96,
            0.95, 0.94, 0.93, 0.93, 0.94, 0.96,
            0.98, 0.95, 0.90, 0.87, 0.84, 0.82,
        ],
        "pediatrics": [
            0.25, 0.20, 0.18, 0.17, 0.18, 0.25,
            0.40, 0.65, 0.85, 0.95, 1.00, 0.98,
            0.92, 0.88, 0.85, 0.87, 0.90, 0.92,
            0.88, 0.80, 0.68, 0.52, 0.38, 0.28,
        ],
    }
    return patterns[dept][hour]


def weekly_pattern(dow: int, dept: str) -> float:
    """
    Returns a demand multiplier for each day of week (0=Mon … 6=Sun).
    """
    patterns = {
        "emergency":    [1.05, 1.00, 0.98, 1.00, 1.08, 1.10, 0.95],
        "general_ward": [1.10, 1.05, 1.00, 0.98, 1.05, 0.90, 0.85],
        "icu":          [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00],  # constant
        "pediatrics":   [1.05, 1.00, 0.98, 0.95, 1.05, 1.08, 0.92],
    }
    return patterns[dept][dow]


def seasonal_pattern(month: int, dept: str) -> float:
    """
    Returns annual seasonal multiplier per month (1–12).
    Emergency surges in winter (flu) and summer heat.
    """
    patterns = {
        "emergency": [
            1.15, 1.10, 1.00, 0.95, 0.90, 0.95,
            1.05, 1.08, 0.95, 0.90, 1.00, 1.12,
        ],
        "general_ward": [
            1.10, 1.05, 1.00, 0.95, 0.92, 0.90,
            0.95, 0.98, 0.95, 0.95, 1.00, 1.08,
        ],
        "icu": [
            1.08, 1.05, 1.00, 0.97, 0.95, 0.95,
            0.98, 1.00, 0.97, 0.97, 1.00, 1.05,
        ],
        "pediatrics": [
            1.12, 1.08, 1.00, 0.95, 0.90, 0.88,
            0.92, 0.95, 1.00, 1.05, 1.08, 1.15,
        ],
    }
    return patterns[dept][month - 1]


# ── Base arrival rates (mean patients per hour at peak) ───────────────────────
BASE_RATES = {
    "emergency":    12.0,
    "general_ward":  7.0,
    "icu":           2.5,
    "pediatrics":    5.0,
}

DEPARTMENTS = list(BASE_RATES.keys())


def generate_dataset(
    start_date: str = "2021-01-01",
    end_date: str   = "2023-12-31",
) -> pd.DataFrame:
    """
    Generate a full hourly patient arrival dataset.

    Returns
    -------
    pd.DataFrame with columns:
        timestamp, emergency, general_ward, icu, pediatrics,
        hour, day_of_week, is_weekend, is_holiday,
        month, day_of_year
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end   = datetime.strptime(end_date,   "%Y-%m-%d") + timedelta(days=1)

    years    = list(range(start.year, end.year + 1))
    holidays = get_holidays(years)

    timestamps = pd.date_range(start=start, end=end, freq="h", inclusive="left")
    n = len(timestamps)

    records = []
    for ts in timestamps:
        hour       = ts.hour
        dow        = ts.dayofweek          # 0=Mon
        month      = ts.month
        is_weekend = int(dow >= 5)
        is_holiday = int(datetime(ts.year, ts.month, ts.day) in holidays)

        row: dict = {
            "timestamp":  ts,
            "hour":       hour,
            "day_of_week": dow,
            "month":      month,
            "day_of_year": ts.dayofyear,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
        }

        for dept in DEPARTMENTS:
            base   = BASE_RATES[dept]
            h_mult = hourly_pattern(hour, dept)
            w_mult = weekly_pattern(dow, dept)
            s_mult = seasonal_pattern(month, dept)

            # Holiday effect: ED sees surge, elective wards see reduction
            if is_holiday:
                h_eff = 1.20 if dept == "emergency" else 0.70
            else:
                h_eff = 1.0

            lam = base * h_mult * w_mult * s_mult * h_eff
            lam = max(lam, 0.1)  # floor

            # Poisson noise captures natural randomness
            arrivals = np.random.poisson(lam)
            row[dept] = int(arrivals)

        records.append(row)

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    print("Generating 3-year synthetic ED arrivals dataset …")
    df = generate_dataset()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df):,} rows → {OUTPUT_PATH}")
    print(df.head(5).to_string())
    print("\nColumn stats:")
    print(df[DEPARTMENTS].describe().round(2))
