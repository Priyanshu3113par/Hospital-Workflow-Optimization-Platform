"""
Full training pipeline for LSTM / GRU patient demand forecasters.
Supports early stopping, LR scheduling, and checkpoint saving.

Usage
-----
python ml/training/train.py --model lstm --department emergency --epochs 50
python ml/training/train.py --model gru  --department icu       --lookback 48 --smoke-test
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau

# ── Path setup (allow running from project root) ───────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.preprocessing.synthetic_data import generate_dataset, OUTPUT_PATH as SYNTH_PATH
from ml.preprocessing.data_loader import load_and_prepare
from ml.preprocessing.scalers import DepartmentScaler
from ml.training.lstm_model import LSTMForecaster
from ml.training.gru_model import GRUForecaster
from ml.evaluation.metrics import compute_metrics, format_metrics_table

SAVED_MODELS_DIR   = ROOT / "ml" / "saved_models"
EXPERIMENTS_DIR    = ROOT / "research" / "experiments"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Early Stopping ─────────────────────────────────────────────────────────────
class EarlyStopping:
    def __init__(self, patience: int = 10, min_delta: float = 1e-5) -> None:
        self.patience  = patience
        self.min_delta = min_delta
        self.counter   = 0
        self.best_loss = float("inf")
        self.triggered = False

    def step(self, val_loss: float) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter   = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.triggered = True
        return self.triggered


# ── Training loop ──────────────────────────────────────────────────────────────
def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
) -> float:
    model.train()
    total_loss = 0.0
    for X_batch, y_batch in loader:
        X_batch = X_batch.to(DEVICE)
        y_batch = y_batch.to(DEVICE)

        optimizer.zero_grad()
        preds = model(X_batch).squeeze(-1)
        loss  = criterion(preds, y_batch.squeeze(-1))
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item() * len(X_batch)

    return total_loss / len(loader.dataset)


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
) -> float:
    model.eval()
    total_loss = 0.0
    for X_batch, y_batch in loader:
        X_batch = X_batch.to(DEVICE)
        y_batch = y_batch.to(DEVICE)
        preds   = model(X_batch).squeeze(-1)
        loss    = criterion(preds, y_batch.squeeze(-1))
        total_loss += loss.item() * len(X_batch)
    return total_loss / len(loader.dataset)


@torch.no_grad()
def collect_predictions(
    model: nn.Module,
    loader: DataLoader,
) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    all_preds, all_true = [], []
    for X_batch, y_batch in loader:
        preds = model(X_batch.to(DEVICE)).squeeze(-1).cpu().numpy()
        all_preds.append(preds)
        all_true.append(y_batch.squeeze(-1).numpy())
    return np.concatenate(all_preds), np.concatenate(all_true)


# ── Main training function ─────────────────────────────────────────────────────
def train(
    model_type:  str   = "lstm",
    department:  str   = "emergency",
    lookback:    int   = 168,
    epochs:      int   = 50,
    batch_size:  int   = 32,
    hidden_size: int   = 128,
    num_layers:  int   = 2,
    dropout:     float = 0.2,
    lr:          float = 1e-3,
    patience:    int   = 10,
    smoke_test:  bool  = False,
) -> dict:
    """
    Full training pipeline. Returns evaluation metrics dict.
    """
    # ── 0. Ensure synthetic data exists ───────────────────────────────────────
    if not SYNTH_PATH.exists():
        print("Synthetic data not found. Generating …")
        df = generate_dataset()
        df.to_csv(SYNTH_PATH, index=False)
        print(f"Generated {len(df):,} rows.")

    # ── 1. Load data ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f" Model: {model_type.upper()} | Dept: {department} | Lookback: {lookback}h")
    print(f"{'='*60}")

    data = load_and_prepare(dept=department, lookback=lookback)

    # Scale features (fit on train only)
    scaler = DepartmentScaler()
    data["train_df"] = scaler.fit_transform(data["train_df"], data["feat_cols"])
    data["val_df"]   = scaler.transform(data["val_df"],   data["feat_cols"])
    data["test_df"]  = scaler.transform(data["test_df"],  data["feat_cols"])

    # Re-create datasets with scaled data
    from ml.preprocessing.data_loader import EDArrivalsDataset
    train_ds = EDArrivalsDataset(data["train_df"], department, lookback)
    val_ds   = EDArrivalsDataset(data["val_df"],   department, lookback)
    test_ds  = EDArrivalsDataset(data["test_df"],  department, lookback)

    if smoke_test:
        print("[smoke-test] Using 200-sample subset …")
        from torch.utils.data import Subset
        train_ds = Subset(train_ds, range(min(200, len(train_ds))))
        val_ds   = Subset(val_ds,   range(min(50,  len(val_ds))))
        test_ds  = Subset(test_ds,  range(min(50,  len(test_ds))))
        epochs   = min(epochs, 2)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader  = DataLoader(test_ds,  batch_size=batch_size, shuffle=False, num_workers=0)

    n_features = data["n_features"]

    # ── 2. Build model ────────────────────────────────────────────────────────
    ModelClass = LSTMForecaster if model_type == "lstm" else GRUForecaster
    model = ModelClass(
        input_size=n_features,
        hidden_size=hidden_size,
        num_layers=num_layers,
        dropout=dropout,
        output_size=1,
    ).to(DEVICE)

    print(model.get_model_summary())
    print(f"Device: {DEVICE}")
    print(f"Train / Val / Test sizes: {len(train_ds)} / {len(val_ds)} / {len(test_ds)}")

    # ── 3. Training setup ─────────────────────────────────────────────────────
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=5)
    criterion = nn.MSELoss()
    stopper   = EarlyStopping(patience=patience)

    best_val_loss = float("inf")
    ckpt_path = SAVED_MODELS_DIR / f"{model_type}_{department}_{lookback}.pt"
    history   = {"train_loss": [], "val_loss": []}

    # ── 4. Training loop ──────────────────────────────────────────────────────
    t_start = time.time()
    for epoch in range(1, epochs + 1):
        tr_loss  = train_one_epoch(model, train_loader, optimizer, criterion)
        val_loss = evaluate(model, val_loader, criterion)
        scheduler.step(val_loss)

        history["train_loss"].append(tr_loss)
        history["val_loss"].append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                "epoch":       epoch,
                "model_state": model.state_dict(),
                "model_type":  model_type,
                "department":  department,
                "lookback":    lookback,
                "n_features":  n_features,
                "hidden_size": hidden_size,
                "num_layers":  num_layers,
                "dropout":     dropout,
                "val_loss":    val_loss,
            }, ckpt_path)

        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{epochs} | "
                  f"train_loss={tr_loss:.5f} | val_loss={val_loss:.5f} | "
                  f"lr={optimizer.param_groups[0]['lr']:.6f}")

        if stopper.step(val_loss):
            print(f"  Early stopping triggered at epoch {epoch}.")
            break

    elapsed = time.time() - t_start
    print(f"\nTraining complete in {elapsed:.1f}s | Best val loss: {best_val_loss:.5f}")
    print(f"Checkpoint saved → {ckpt_path}")

    # ── 5. Test evaluation ────────────────────────────────────────────────────
    # Load best checkpoint
    ckpt = torch.load(ckpt_path, map_location=DEVICE)
    model.load_state_dict(ckpt["model_state"])

    test_preds, test_true = collect_predictions(model, test_loader)

    # Inverse-scale to original patient counts
    test_preds_inv = scaler.inverse_transform_target(test_preds, department)
    test_true_inv  = scaler.inverse_transform_target(test_true,  department)
    test_preds_inv = np.maximum(test_preds_inv, 0)   # floor at 0

    metrics = compute_metrics(test_true_inv, test_preds_inv)
    metrics["model"]      = model_type.upper()
    metrics["department"] = department
    metrics["lookback"]   = lookback
    metrics["train_time_s"] = round(elapsed, 2)

    print("\n── Test-set Metrics ──────────────────────────────────────────")
    print(format_metrics_table({f"{model_type.upper()}": metrics}))

    # ── 6. Save training history ───────────────────────────────────────────────
    hist_path = EXPERIMENTS_DIR / f"history_{model_type}_{department}_{lookback}.json"
    with open(hist_path, "w") as f:
        json.dump(history, f, indent=2)

    # ── 7. Save scaler ────────────────────────────────────────────────────────
    scaler.save(SAVED_MODELS_DIR / f"scaler_{department}.pkl")

    return metrics


# ── CLI entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train LSTM/GRU patient demand forecaster")
    parser.add_argument("--model",       choices=["lstm", "gru"], default="gru")
    parser.add_argument("--department",  choices=["emergency", "general_ward", "icu", "pediatrics"], default="emergency")
    parser.add_argument("--lookback",    type=int,   default=168)
    parser.add_argument("--epochs",      type=int,   default=50)
    parser.add_argument("--batch-size",  type=int,   default=32)
    parser.add_argument("--hidden-size", type=int,   default=128)
    parser.add_argument("--lr",          type=float, default=1e-3)
    parser.add_argument("--patience",    type=int,   default=10)
    parser.add_argument("--smoke-test",  action="store_true", help="Run 2-epoch smoke test")
    args = parser.parse_args()

    train(
        model_type  = args.model,
        department  = args.department,
        lookback    = args.lookback,
        epochs      = args.epochs,
        batch_size  = args.batch_size,
        hidden_size = args.hidden_size,
        lr          = args.lr,
        patience    = args.patience,
        smoke_test  = args.smoke_test,
    )
