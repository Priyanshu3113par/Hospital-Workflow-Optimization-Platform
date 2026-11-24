"""
PyTorch GRU Forecaster — same interface as LSTMForecaster but uses GRU cells.
GRU typically trains faster with fewer parameters while matching LSTM accuracy.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class GRUForecaster(nn.Module):
    """
    Stacked GRU model for hospital patient demand forecasting.

    Parameters
    ----------
    input_size  : number of input features per timestep
    hidden_size : number of GRU hidden units (default 128)
    num_layers  : number of stacked GRU layers (default 2)
    dropout     : dropout probability between layers (default 0.2)
    output_size : forecast horizon length (default 1)
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

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
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
        x   : (batch_size, seq_len, input_size)

        Returns
        -------
        out : (batch_size, output_size)
        """
        gru_out, _ = self.gru(x)                   # (batch, seq, hidden)
        last_hidden = gru_out[:, -1, :]             # (batch, hidden)
        last_hidden = self.dropout(last_hidden)
        out = self.fc(last_hidden)                  # (batch, output_size)
        return out

    def get_model_summary(self) -> str:
        total     = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return (
            f"GRUForecaster  | "
            f"input={self.input_size} | hidden={self.hidden_size} | "
            f"layers={self.num_layers} | output={self.output_size} | "
            f"params={total:,} (trainable={trainable:,})"
        )
