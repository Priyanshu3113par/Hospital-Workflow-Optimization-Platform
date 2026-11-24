"""
Inference wrapper — loads a saved LSTM/GRU checkpoint and generates forecasts.
Used by the FastAPI backend service layer.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.training.lstm_model import LSTMForecaster
from ml.training.gru_model  import GRUForecaster
from ml.preprocessing.scalers import DepartmentScaler

SAVED_MODELS_DIR = ROOT / "ml" / "saved_models"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

ShiftType = Literal["morning", "afternoon", "night"]
SHIFT_HOURS = {"morning": range(6, 14), "afternoon": range(14, 22), "night": list(range(22, 24)) + list(range(0, 6))}


class DemandPredictor:
    """
    High-level inference interface for the trained LSTM/GRU models.

    Usage
    -----
    predictor = DemandPredictor()
    predictor.load_model("ml/saved_models/gru_emergency_168.pt", "gru")
    preds = predictor.predict_next_24h(recent_df, "emergency")
    """

    def __init__(self) -> None:
        self._model:     torch.nn.Module | None = None
        self._scaler:    DepartmentScaler | None = None
        self._meta:      dict = {}

    def load_model(
        self,
        model_path: Path | str,
        model_type: Literal["lstm", "gru"] = "gru",
    ) -> None:
        """Load a saved checkpoint and its associated scaler."""
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found: {model_path}")

        ckpt = torch.load(model_path, map_location=DEVICE)
        self._meta = {k: v for k, v in ckpt.items() if k != "model_state"}

        ModelClass = LSTMForecaster if model_type == "lstm" else GRUForecaster
        model = ModelClass(
            input_size  = ckpt["n_features"],
            hidden_size = ckpt.get("hidden_size", 128),
            num_layers  = ckpt.get("num_layers", 2),
            dropout     = ckpt.get("dropout", 0.2),
            output_size = 1,
        )
        model.load_state_dict(ckpt["model_state"])
        model.eval()
        self._model = model.to(DEVICE)

        # Load scaler
        dept = ckpt["department"]
        scaler_path = SAVED_MODELS_DIR / f"scaler_{dept}.pkl"
        if scaler_path.exists():
            self._scaler = DepartmentScaler.load(scaler_path)

        print(f"Loaded {model_type.upper()} for '{dept}' (lookback={ckpt['lookback']}h)")

    @staticmethod
    def _auto_load(department: str, model_type: str = "gru") -> "DemandPredictor":
        """Auto-detect and load the best available checkpoint for a department."""
        pred = DemandPredictor()
        for lookback in [168, 48, 24]:
            ckpt_path = SAVED_MODELS_DIR / f"{model_type}_{department}_{lookback}.pt"
            if ckpt_path.exists():
                pred.load_model(ckpt_path, model_type)
                return pred
        raise FileNotFoundError(
            f"No trained model found for department='{department}', model='{model_type}'.\n"
            f"Run: python ml/training/train.py --model {model_type} --department {department}"
        )

    @torch.no_grad()
    def predict_next_24h(
        self,
        recent_history_df: pd.DataFrame,
        department: str,
    ) -> list[float]:
        """
        Predict hourly patient arrivals for the next 24 hours.

        Parameters
        ----------
        recent_history_df : DataFrame with the most recent N hours of data
                            (must have same feature columns as training)
        department        : target department name

        Returns
        -------
        list of 24 float predictions (one per hour)
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        from ml.preprocessing.data_loader import engineer_features, get_feature_cols

        df = engineer_features(recent_history_df, department)
        if self._scaler:
            df = self._scaler.transform(df, get_feature_cols(department))

        feat_cols  = get_feature_cols(department)
        lookback   = self._meta.get("lookback", 168)

        # Use last `lookback` rows as the input window
        window = df[feat_cols].values[-lookback:].astype(np.float32)
        if len(window) < lookback:
            # Pad with zeros if not enough history
            pad = np.zeros((lookback - len(window), len(feat_cols)), dtype=np.float32)
            window = np.vstack([pad, window])

        predictions = []
        # Autoregressive 24-step forecast
        for _ in range(24):
            x = torch.tensor(window[np.newaxis, :, :]).to(DEVICE)  # (1, lookback, features)
            pred_scaled = self._model(x).squeeze().cpu().numpy()

            if self._scaler:
                pred_val = float(self._scaler.inverse_transform_target(
                    np.array([pred_scaled]), department
                )[0])
            else:
                pred_val = float(pred_scaled)

            predictions.append(max(0.0, pred_val))

            # Slide the window forward by 1 step (use predicted value)
            new_row        = window[-1].copy()
            feat_idx       = get_feature_cols(department).index(department)
            new_row[feat_idx] = pred_scaled
            window = np.vstack([window[1:], new_row])

        return predictions

    def predict_shift_demand(
        self,
        department: str,
        shift_type: ShiftType,
        recent_history_df: pd.DataFrame,
    ) -> float:
        """
        Predict total patient demand for a specific shift (morning/afternoon/night).

        Returns
        -------
        float — expected total patients for the entire shift period
        """
        hourly = self.predict_next_24h(recent_history_df, department)
        hours  = SHIFT_HOURS[shift_type]
        return float(sum(hourly[h % 24] for h in hours))
