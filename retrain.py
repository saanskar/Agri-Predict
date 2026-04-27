"""
retrain.py
===========
Retrains AgriPredict models on the expanded 10,000-row dataset.

Usage:
    python retrain.py

What it does:
    1. Loads the new dataset (only the 7 core features matching the backend)
    2. Trains Random Forest + XGBoost + Neural Network
    3. Saves artifacts to the artifacts/ folder (replaces old models)
    4. Prints accuracy for each model

Run from your project root:
    cd C:\\Capstone\\Capstone\\Agri
    python retrain.py
"""

import json
import os
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import xgboost as xgb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings("ignore")

# ── Config ──────────────────────────────────────────────────────────────────
DATA_PATH = "AgriPredict_India_100k.csv"
ARTIFACTS_DIR = Path("artifacts")
FEATURE_COLS  = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
LABEL_COL     = "label"
TEST_SIZE     = 0.2
RANDOM_STATE  = 42

# ── Neural Network definition (must match backend ml/models/nn_model.py) ───
class Net(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, output_dim),
        )

    def forward(self, x):
        return self.net(x)


# ── 1. Load and prepare data ─────────────────────────────────────────────────
print("=" * 60)
print("AgriPredict Model Retraining")
print("=" * 60)

print(f"\n[1/6] Loading dataset: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print(f"      Shape: {df.shape}")
print(f"      Crops: {sorted(df[LABEL_COL].unique())}")

# Rename columns to match FEATURE_COLS (dataset uses lowercase)
col_map = {"n": "N", "p": "P", "k": "K"}
df = df.rename(columns=col_map)

# Use ONLY the 7 core features — extra columns (state, season, soil_type etc)
# are synthetically generated and do not improve accuracy
X = df[FEATURE_COLS].values.astype(np.float32)
y_raw = df[LABEL_COL].values

# Encode labels — sort alphabetically so label index is deterministic
label_encoder = LabelEncoder()
label_encoder.fit(sorted(np.unique(y_raw)))
y = label_encoder.transform(y_raw)
labels = list(label_encoder.classes_)
n_classes = len(labels)

print(f"      Features: {FEATURE_COLS}")
print(f"      Classes ({n_classes}): {labels}")

# Train / test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)
print(f"      Train: {len(X_train)}  Test: {len(X_test)}")


# ── 2. Preprocessor ──────────────────────────────────────────────────────────
print("\n[2/6] Fitting preprocessor (StandardScaler)...")
preprocessor = Pipeline([("scaler", StandardScaler())])
X_train_t = preprocessor.fit_transform(X_train).astype(np.float32)
X_test_t  = preprocessor.transform(X_test).astype(np.float32)
print("      Done.")


# ── 3. Random Forest ─────────────────────────────────────────────────────────
print("\n[3/6] Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    n_jobs=-1,
    random_state=RANDOM_STATE,
    class_weight="balanced",
)
rf.fit(X_train_t, y_train)
rf_acc = accuracy_score(y_test, rf.predict(X_test_t))
print(f"      Accuracy: {rf_acc*100:.2f}%")


# ── 4. XGBoost ───────────────────────────────────────────────────────────────
print("\n[4/6] Training XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric="mlogloss",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)
xgb_model.fit(X_train_t, y_train,
              eval_set=[(X_test_t, y_test)],
              verbose=False)
xgb_acc = accuracy_score(y_test, xgb_model.predict(X_test_t))
print(f"      Accuracy: {xgb_acc*100:.2f}%")


# ── 5. Neural Network ────────────────────────────────────────────────────────
print("\n[5/6] Training Neural Network...")
EPOCHS     = 80
BATCH_SIZE = 64
LR         = 1e-3

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"      Device: {device}")

X_tr_t = torch.tensor(X_train_t, dtype=torch.float32)
y_tr_t = torch.tensor(y_train,   dtype=torch.long)
X_te_t = torch.tensor(X_test_t,  dtype=torch.float32)
y_te_t = torch.tensor(y_test,    dtype=torch.long)

train_ds = TensorDataset(X_tr_t, y_tr_t)
train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

net = Net(input_dim=len(FEATURE_COLS), output_dim=n_classes).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=LR, weight_decay=1e-4)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

best_acc  = 0.0
best_state = None

for epoch in range(1, EPOCHS + 1):
    net.train()
    for xb, yb in train_dl:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        loss = criterion(net(xb), yb)
        loss.backward()
        optimizer.step()
    scheduler.step()

    # Evaluate every 10 epochs
    if epoch % 10 == 0:
        net.eval()
        with torch.no_grad():
            preds = net(X_te_t.to(device)).argmax(dim=1).cpu()
        acc = accuracy_score(y_test, preds.numpy())
        print(f"      Epoch {epoch:3d}/{EPOCHS}  acc={acc*100:.2f}%")
        if acc > best_acc:
            best_acc   = acc
            best_state = {k: v.clone() for k, v in net.state_dict().items()}

# Load best weights
net.load_state_dict(best_state)
net.eval()
with torch.no_grad():
    nn_preds = net(X_te_t.to(device)).argmax(dim=1).cpu().numpy()
nn_acc = accuracy_score(y_test, nn_preds)
print(f"      Best Accuracy: {nn_acc*100:.2f}%")


# ── 5b. Ensemble accuracy ─────────────────────────────────────────────────────
rf_probs  = rf.predict_proba(X_test_t)
xgb_probs = xgb_model.predict_proba(X_test_t)
with torch.no_grad():
    nn_logits = net(X_te_t.to(device)).cpu().numpy()
nn_probs  = torch.softmax(torch.tensor(nn_logits), dim=1).numpy()
ens_probs = (rf_probs + xgb_probs + nn_probs) / 3.0
ens_preds = np.argmax(ens_probs, axis=1)
ens_acc   = accuracy_score(y_test, ens_preds)
print(f"\n      Ensemble Accuracy: {ens_acc*100:.2f}%")


# ── 6. Save artifacts ─────────────────────────────────────────────────────────
print(f"\n[6/6] Saving artifacts to {ARTIFACTS_DIR}/")
ARTIFACTS_DIR.mkdir(exist_ok=True)

# Labels
labels_path = ARTIFACTS_DIR / "labels.json"
labels_path.write_text(json.dumps(labels, indent=2), encoding="utf-8")
print(f"      Saved: {labels_path}")

# Preprocessor
pre_path = ARTIFACTS_DIR / "preprocessor.joblib"
joblib.dump(preprocessor, pre_path)
print(f"      Saved: {pre_path}")

# Random Forest
rf_path = ARTIFACTS_DIR / "random_forest.joblib"
joblib.dump(rf, rf_path)
print(f"      Saved: {rf_path}")

# XGBoost
xgb_path = ARTIFACTS_DIR / "xgboost.joblib"
joblib.dump(xgb_model, xgb_path)
print(f"      Saved: {xgb_path}")

# Neural Network
nn_path = ARTIFACTS_DIR / "neural_net.pt"
torch.save(best_state, nn_path)
print(f"      Saved: {nn_path}")


# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)
print(f"  Random Forest : {rf_acc*100:.2f}%")
print(f"  XGBoost       : {xgb_acc*100:.2f}%")
print(f"  Neural Network: {nn_acc*100:.2f}%")
print(f"  Ensemble      : {ens_acc*100:.2f}%")
print()
print("Artifacts saved:")
for f in ARTIFACTS_DIR.iterdir():
    size = f.stat().st_size / 1024
    print(f"  {f.name:30s} {size:.0f} KB")
print()
print("Next step: push the artifacts/ folder to GitHub and redeploy on Render.")
print("The backend will automatically use the new models on next startup.")
