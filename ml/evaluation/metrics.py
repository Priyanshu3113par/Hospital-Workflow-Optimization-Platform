"""
Evaluation metrics for time-series forecasting models.
MAE, RMSE, MAPE, R² with plotting utilities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Compute MAE, RMSE, MAPE, R² between true and predicted arrays.

    Parameters
    ----------
    y_true : ground-truth values (original scale)
    y_pred : predicted values (original scale)

    Returns
    -------
    dict with keys: MAE, RMSE, MAPE, R2
    """
    y_true = np.array(y_true, dtype=np.float64).ravel()
    y_pred = np.array(y_pred, dtype=np.float64).ravel()

    mae  = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    # MAPE: avoid division by zero
    nonzero = y_true != 0
    mape = float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100)

    # R²
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = float(1 - ss_res / (ss_tot + 1e-10))

    return {"MAE": round(mae, 4), "RMSE": round(rmse, 4), "MAPE": round(mape, 4), "R2": round(r2, 4)}


def format_metrics_table(results: dict[str, dict]) -> str:
    """
    Format a dict of {model_name: metrics_dict} as a readable table.

    Example
    -------
    results = {"LSTM": {"MAE": 3.2, "RMSE": 4.8, "MAPE": 8.1, "R2": 0.91}}
    """
    rows = []
    for model, m in results.items():
        rows.append({
            "Model": model,
            "MAE":   m.get("MAE",  "-"),
            "RMSE":  m.get("RMSE", "-"),
            "MAPE%": m.get("MAPE", "-"),
            "R²":    m.get("R2",   "-"),
        })
    df = pd.DataFrame(rows)
    return df.to_markdown(index=False)


def plot_forecast(
    y_true:    np.ndarray,
    y_pred:    np.ndarray,
    title:     str = "Forecast vs Actual",
    save_path: Path | str | None = None,
    max_points: int = 500,
) -> None:
    """Plot predicted vs actual demand over time."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Skipping plot.")
        return

    n = min(len(y_true), max_points)
    x = np.arange(n)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(x, y_true[:n], label="Actual",    color="#14b8a6", linewidth=1.5, alpha=0.9)
    ax.plot(x, y_pred[:n], label="Predicted", color="#f97316", linewidth=1.5, alpha=0.9, linestyle="--")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Time Step (hours)")
    ax.set_ylabel("Patient Arrivals")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved → {save_path}")
    plt.close()


def plot_training_history(
    history:   dict,
    save_path: Path | str | None = None,
) -> None:
    """Plot train vs validation loss curves."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(history["train_loss"], label="Train Loss", color="#3b82f6")
    ax.plot(history["val_loss"],   label="Val Loss",   color="#f97316")
    ax.set_title("Training History", fontsize=13, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE Loss")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"History plot saved → {save_path}")
    plt.close()
