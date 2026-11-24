"""
MinMaxScaler wrapper with save/load capability for consistent inference.
"""

from __future__ import annotations

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler


class DepartmentScaler:
    """
    Per-department MinMaxScaler that scales all feature columns together.
    Fit only on training data; apply to val/test.

    Usage
    -----
    scaler = DepartmentScaler()
    train_df_scaled = scaler.fit_transform(train_df, feat_cols)
    val_df_scaled   = scaler.transform(val_df, feat_cols)
    preds_original  = scaler.inverse_transform_target(scaled_preds, dept)
    """

    def __init__(self) -> None:
        self._scaler: MinMaxScaler | None = None
        self._feat_cols: list[str] = []

    def fit_transform(self, df: pd.DataFrame, feat_cols: list[str]) -> pd.DataFrame:
        """Fit scaler on df and return scaled copy."""
        self._feat_cols = feat_cols
        self._scaler    = MinMaxScaler(feature_range=(0, 1))

        df_out = df.copy()
        df_out[feat_cols] = self._scaler.fit_transform(df[feat_cols])
        return df_out

    def transform(self, df: pd.DataFrame, feat_cols: list[str] | None = None) -> pd.DataFrame:
        """Apply fitted scaler to new data."""
        if self._scaler is None:
            raise RuntimeError("Scaler not fitted yet. Call fit_transform first.")
        cols = feat_cols or self._feat_cols
        df_out = df.copy()
        df_out[cols] = self._scaler.transform(df[cols])
        return df_out

    def inverse_transform_target(
        self,
        scaled_values: np.ndarray,
        target_col: str,
    ) -> np.ndarray:
        """
        Invert scaling for the target column only.
        Uses a dummy array to work around sklearn's requirement for
        the full feature matrix during inverse_transform.
        """
        if self._scaler is None:
            raise RuntimeError("Scaler not fitted.")

        col_idx = self._feat_cols.index(target_col)
        n       = len(scaled_values)
        dummy   = np.zeros((n, len(self._feat_cols)), dtype=np.float32)
        dummy[:, col_idx] = scaled_values.ravel()

        inv = self._scaler.inverse_transform(dummy)
        return inv[:, col_idx]

    def save(self, path: Path | str) -> None:
        """Persist scaler to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"scaler": self._scaler, "feat_cols": self._feat_cols}, f)
        print(f"Scaler saved → {path}")

    @classmethod
    def load(cls, path: Path | str) -> "DepartmentScaler":
        """Load scaler from disk."""
        with open(path, "rb") as f:
            state = pickle.load(f)
        obj = cls()
        obj._scaler    = state["scaler"]
        obj._feat_cols = state["feat_cols"]
        return obj


def chronological_split_arrays(
    X: np.ndarray,
    y: np.ndarray,
    train_frac: float = 0.70,
    val_frac:   float = 0.15,
) -> tuple[tuple, tuple, tuple]:
    """Split numpy arrays chronologically. Returns (X_tr,y_tr),(X_val,y_val),(X_te,y_te)."""
    n = len(X)
    t = int(n * train_frac)
    v = int(n * (train_frac + val_frac))
    return (X[:t], y[:t]), (X[t:v], y[t:v]), (X[v:], y[v:])
