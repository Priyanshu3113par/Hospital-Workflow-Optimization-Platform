"""
Baseline forecasting models for comparison against LSTM/GRU.
Implements Seasonal Naive and ARIMA baselines.
"""

from __future__ import annotations

import time
import warnings
import numpy as np
import pandas as pd
from typing import Optional

warnings.filterwarnings("ignore")


class BaselineForecaster:
    """
    Baseline models for time-series comparison.

    Models
    ------
    1. Seasonal Naive  — predict using same hour exactly one week ago (168h lag)
    2. ARIMA           — fitted on training series, evaluated on test
    """

    @staticmethod
    def seasonal_naive(
        series:   np.ndarray,
        horizon:  int = 1,
        period:   int = 168,          # 1 week = 168 hours
    ) -> dict:
        """
        Seasonal Naive baseline: ŷ_{t+h} = y_{t+h-period}

        Parameters
        ----------
        series  : full 1-D array (train + test concatenated)
        horizon : number of steps to forecast
        period  : seasonal period in steps (default 168h = 1 week)

        Returns
        -------
        dict with 'predictions' (np.ndarray) and 'fit_time' (float)
        """
        t0    = time.time()
        n     = len(series)
        preds = []

        # For each test position predict using the value from one season ago
        for i in range(horizon):
            look_back_idx = n - horizon + i - period
            if look_back_idx < 0:
                look_back_idx = 0
            preds.append(series[look_back_idx])

        return {
            "predictions": np.array(preds, dtype=np.float32),
            "fit_time":    time.time() - t0,
            "model":       "SeasonalNaive",
        }

    @staticmethod
    def arima_forecast(
        train_series: np.ndarray,
        test_length:  int,
        order:        tuple = (2, 1, 2),
        seasonal_order: Optional[tuple] = None,
    ) -> dict:
        """
        ARIMA / SARIMA forecast using statsmodels.

        Parameters
        ----------
        train_series  : 1-D training array
        test_length   : number of test-set steps to predict
        order         : (p, d, q) ARIMA order
        seasonal_order: optional (P, D, Q, s) for SARIMA

        Returns
        -------
        dict with 'predictions', 'fit_time', 'model', 'aic'
        """
        try:
            from statsmodels.tsa.arima.model import ARIMA
            from statsmodels.tsa.statespace.sarimax import SARIMAX
        except ImportError:
            raise ImportError("Install statsmodels: pip install statsmodels")

        t0 = time.time()

        if seasonal_order is not None:
            model = SARIMAX(
                train_series,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
        else:
            model = ARIMA(train_series, order=order)

        fit   = model.fit(disp=False)
        preds = fit.forecast(steps=test_length)

        return {
            "predictions": np.array(preds, dtype=np.float32),
            "fit_time":    time.time() - t0,
            "model":       "ARIMA" if seasonal_order is None else "SARIMA",
            "aic":         fit.aic,
        }

    @staticmethod
    def rolling_mean_baseline(
        series:  np.ndarray,
        horizon: int,
        window:  int = 24,
    ) -> dict:
        """Simple rolling-mean baseline (mean of last `window` steps)."""
        t0   = time.time()
        last = series[-window:].mean()
        return {
            "predictions": np.full(horizon, last, dtype=np.float32),
            "fit_time":    time.time() - t0,
            "model":       f"RollingMean{window}",
        }
