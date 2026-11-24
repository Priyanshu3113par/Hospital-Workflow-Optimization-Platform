"""
PyTorch LSTM Forecaster for hospital patient demand prediction.
Stacked 2-layer LSTM with dropout for regularization.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class LSTMForecaster(nn.Module):
    """
    Stacked LSTM model for univariate/multivariate time-series forecasting.

    Architecture
    ------------
    Input  → LSTM Layer 1 → Dropout → LSTM Layer 2 → Dropout
           → FC Layer → Output

    Parameters
    ----------
    input_size  : number of input features per timestep
    hidden_size : number of LSTM hidden units (default 128)
    num_layers  : number of stacked LSTM layers (default 2)
    dropout     : dropout probability between layers (default 0.2)
    output_size : forecast horizon length (default 1 for one-step-ahead)
    """

    def __init__(
        self,
        input_size:  int   = 17,
        hidden_size: int   = 128,
        num_layers:  int   = 2,
        dropout:     float = 0.2,
        output_size: int   = 1,
    ) -> None:
        super().__init__()
        self.input_size  = input_size
        self.hidden_size = hidden_size
        self.num_layers  = num_layers
        self.output_size = output_size

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,          # (batch, seq, features)
        )

        self.dropout = nn.Dropout(p=dropout)

        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(p=dropout),
            nn.Linear(hidden_size // 2, output_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        x : (batch_size, seq_len, input_size)

        Returns
        -------
        out : (batch_size, output_size)
        """
        # lstm_out: (batch, seq, hidden)
        lstm_out, _ = self.lstm(x)

        # Take the hidden state at the last time step
        last_hidden = lstm_out[:, -1, :]           # (batch, hidden)
        last_hidden = self.dropout(last_hidden)

        out = self.fc(last_hidden)                 # (batch, output_size)
        return out

    def get_model_summary(self) -> str:
        total  = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return (
            f"LSTMForecaster | "
            f"input={self.input_size} | hidden={self.hidden_size} | "
            f"layers={self.num_layers} | output={self.output_size} | "
            f"params={total:,} (trainable={trainable:,})"
        )
