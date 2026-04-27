"""
retrain_50crops.py
===================
Retrains AgriPredict on the 500k / 50-crop dataset.

Usage:
    cd C:\Capstone\Capstone\Agri
    python retrain_50crops.py

Output:
    model_artifacts/labels.json
    model_artifacts/preprocessor.joblib
    model_artifacts/random_forest.joblib
    model_artifacts/xgboost.joblib
"""

import json, warnings, joblib, numpy as np, pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import xgboost as xgb

warnings.filterwarnings("ignore")

DATA_PATH     = "AgriPredict_India_500k.csv"
ARTIFACTS_DIR = Path("model_artifacts")   # goes into ui/model_artifacts/
FEATURES      = ["N","P","K","temperature","humidity","ph","rainfall"]
ROWS_PER_CROP = 2000   # 2000 × 50 crops = 100k training rows

print("="*55)
print("AgriPredict — 50 Crop Model Training")
print("="*55)

# ── Load ───────────────────────────────────────────────────────
print(f"\nLoading {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)
print(f"  Shape: {df.shape}  Crops: {df['label'].nunique()}")

# Sample evenly per crop
frames = [
    s.sample(min(ROWS_PER_CROP, len(s)), random_state=42)
    for _, s in df.groupby("label")
]
df_s = pd.concat(frames).sample(frac=1, random_state=42).reset_index(drop=True)
del df, frames
print(f"  Training sample: {len(df_s):,} rows")

# ── Encode ─────────────────────────────────────────────────────
X  = df_s[FEATURES].values.astype("float32")
le = LabelEncoder()
le.fit(sorted(df_s["label"].unique()))
y  = le.transform(df_s["label"].values)
labels = list(le.classes_)
print(f"  Labels ({len(labels)}): {labels}")

X_tr,X_te,y_tr,y_te = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y)

pre = Pipeline([("s", StandardScaler())])
Xtr = pre.fit_transform(X_tr).astype("float32")
Xte = pre.transform(X_te).astype("float32")

# ── Random Forest ──────────────────────────────────────────────
print("\n[1/2] Training Random Forest (150 trees)...")
rf = RandomForestClassifier(
    n_estimators=150, n_jobs=-1,
    random_state=42, class_weight="balanced")
rf.fit(Xtr, y_tr)
print(f"      Accuracy: {accuracy_score(y_te, rf.predict(Xte))*100:.2f}%")

# ── XGBoost ────────────────────────────────────────────────────
print("\n[2/2] Training XGBoost (150 trees)...")
xm = xgb.XGBClassifier(
    n_estimators=150, max_depth=8, learning_rate=0.1,
    subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
    tree_method="hist", eval_metric="mlogloss",
    random_state=42, use_label_encoder=False)
xm.fit(Xtr, y_tr, eval_set=[(Xte,y_te)], verbose=False)
print(f"      Accuracy: {accuracy_score(y_te, xm.predict(Xte))*100:.2f}%")

ens = (rf.predict_proba(Xte) + xm.predict_proba(Xte)) / 2
print(f"\n      Ensemble: {accuracy_score(y_te, ens.argmax(1))*100:.2f}%")

# ── Save ───────────────────────────────────────────────────────
ARTIFACTS_DIR.mkdir(exist_ok=True)
(ARTIFACTS_DIR/"labels.json").write_text(json.dumps(labels, indent=2))
joblib.dump(pre, ARTIFACTS_DIR/"preprocessor.joblib")
joblib.dump(rf,  ARTIFACTS_DIR/"random_forest.joblib")
joblib.dump(xm,  ARTIFACTS_DIR/"xgboost.joblib")

print(f"\nSaved to {ARTIFACTS_DIR}/")
for f in sorted(ARTIFACTS_DIR.iterdir()):
    print(f"  {f.name:30s}  {f.stat().st_size//1024:6d} KB")

print("\nDone! Copy model_artifacts/ into ui/ and run: streamlit run app.py")
