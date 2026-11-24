"""
Data loader and PyTorch Dataset for hospital ED arrivals time-series.
Handles feature engineering, normalization, and sliding-window generation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional
import torch
from torch.utils.data import Dataset

DEPARTMENTS = ["emergency", "general_ward", "icu", "pediatrics"]

RAW_PATH = Path(__file__).resolve().parents[1] / "datasets" / "raw" / "synthetic_ed_arrivals.csv"


# ── Feature engineering ────────────────────────────────────────────────────────

def add_cyclic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add sine/cosine cyclic encodings for hour, day-of-week, month."""
    df = df.copy()
    df["hour_sin"]  = np.sin(2 * np.pi * df["hour"]        / 24)
    df["hour_cos"]  = np.cos(2 * np.pi * df["hour"]        / 24)
    df["dow_sin"]   = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"]   = np.cos(2 * np.pi * df["day_of_week"] / 7)
    df["month_sin"] = np.sin(2 * np.pi * df["month"]       / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"]       / 12)
    return df


def add_rolling_features(df: pd.DataFrame, dept: str) -> pd.DataFrame:
    """Rolling mean windows: 3h, 6h, 24h, 168h (1 week)."""
    df = df.copy()
    s = df[dept]
    df[f"{dept}_roll3"]   = s.rolling(3,   min_periods=1).mean()
    df[f"{dept}_roll6"]   = s.rolling(6,   min_periods=1).mean()
    df[f"{dept}_roll24"]  = s.rolling(24,  min_periods=1).mean()
    df[f"{dept}_roll168"] = s.rolling(168, min_periods=1).mean()
    return df


def add_lag_features(df: pd.DataFrame, dept: str) -> pd.DataFrame:
    """Lag features: 1h, 24h, 168h (same hour yesterday / last week)."""
    df = df.copy()
    df[f"{dept}_lag1"]   = df[dept].shift(1)
    df[f"{dept}_lag24"]  = df[dept].shift(24)
    df[f"{dept}_lag168"] = df[dept].shift(168)
    return df


def engineer_features(df: pd.DataFrame, dept: str) -> pd.DataFrame:
    """Full feature engineering pipeline for one department."""
    df = add_cyclic_features(df)
    df = add_rolling_features(df, dept)
    df = add_lag_features(df, dept)
    df = df.dropna().reset_index(drop=True)
    return df


# ── Chronological split ────────────────────────────────────────────────────────

def chronological_split(
    df: pd.DataFrame,
    train_frac: float = 0.70,
    val_frac:   float = 0.15,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split DataFrame into train / val / test using strict chronological order.
    Never shuffle — this is time-series data.
    """
    n = len(df)
    t = int(n * train_frac)
    v = int(n * (train_frac + val_frac))
    return df.iloc[:t], df.iloc[t:v], df.iloc[v:]


# ── Feature columns helper ─────────────────────────────────────────────────────

def get_feature_cols(dept: str) -> list[str]:
    """Return ordered list of input features for a given department."""
    return [
        dept,
        "hour_sin", "hour_cos",
        "dow_sin",  "dow_cos",
        "month_sin","month_cos",
        "is_weekend", "is_holiday",
        f"{dept}_roll3",   f"{dept}_roll6",
        f"{dept}_roll24",  f"{dept}_roll168",
        f"{dept}_lag1",    f"{dept}_lag24", f"{dept}_lag168",
    ]


# ── PyTorch Dataset ────────────────────────────────────────────────────────────

class EDArrivalsDataset(Dataset):
    """
    Sliding-window time-series Dataset for one department.

    Parameters
    ----------
    df          : preprocessed + feature-engineered DataFrame (scaled)
    dept        : target department column name
    lookback    : number of past hours used as input (24, 48, or 168)
    horizon     : number of future hours to predict (default 1)
    """

    def __init__(
        self,
        df:       pd.DataFrame,
        dept:     str,
        lookback: int = 168,
        horizon:  int = 1,
    ) -> None:
        self.lookback  = lookback
        self.horizon   = horizon
        self.dept      = dept
        self.feat_cols = get_feature_cols(dept)

        self.X = df[self.feat_cols].values.astype(np.float32)
        self.y = df[dept].values.astype(np.float32)

    def __len__(self) -> int:
        return len(self.X) - self.lookback - self.horizon + 1

    def __getitem__(self, idx: int):
        x = self.X[idx : idx + self.lookback]                        # (lookback, features)
        y = self.y[idx + self.lookback : idx + self.lookback + self.horizon]  # (horizon,)
        return torch.tensor(x), torch.tensor(y)


# ── Top-level loader ───────────────────────────────────────────────────────────

def load_and_prepare(
    csv_path: Optional[Path] = None,
    dept:     str = "emergency",
    lookback: int = 168,
    horizon:  int = 1,
    train_frac: float = 0.70,
    val_frac:   float = 0.15,
) -> dict:
    """
    Load CSV, engineer features, split, and return Dataset objects + raw splits.

    Returns
    -------
    dict with keys: train_ds, val_ds, test_ds, train_df, val_df, test_df,
                    feat_cols, n_features
    """
    path = csv_path or RAW_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}.\n"
            "Run: python ml/preprocessing/synthetic_data.py"
        )

    df = pd.read_csv(path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    df = engineer_features(df, dept)

    train_df, val_df, test_df = chronological_split(df, train_frac, val_frac)

    feat_cols  = get_feature_cols(dept)
    n_features = len(feat_cols)

    train_ds = EDArrivalsDataset(train_df, dept, lookback, horizon)
    val_ds   = EDArrivalsDataset(val_df,   dept, lookback, horizon)
    test_ds  = EDArrivalsDataset(test_df,  dept, lookback, horizon)

    return {
        "train_ds":   train_ds,
        "val_ds":     val_ds,
        "test_ds":    test_ds,
        "train_df":   train_df,
        "val_df":     val_df,
        "test_df":    test_df,
        "feat_cols":  feat_cols,
        "n_features": n_features,
        "dept":       dept,
        "lookback":   lookback,
    }


if __name__ == "__main__":
    data = load_and_prepare(dept="emergency", lookback=168)
    print(f"Train samples : {len(data['train_ds'])}")
    print(f"Val   samples : {len(data['val_ds'])}")
    print(f"Test  samples : {len(data['test_ds'])}")
    print(f"Input features: {data['n_features']}")
    x, y = data["train_ds"][0]
    print(f"Sample X shape: {x.shape}, y shape: {y.shape}")
