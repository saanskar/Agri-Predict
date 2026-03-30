"""
@design-guard
role: Train RF/XGB/NN models and write artifacts for backend inference.
layer: service
non_goals:
- Provide an online inference API.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [cli_entrypoint]
invariants:
- Training is deterministic given fixed dataset and random seed.
authority:
  decides: [training_orchestration]
  delegates: [model_training_to_wrappers, persistence_to_registry]
extension_policy:
- Add models by extending orchestrator and updating ensemble logic with tests.
failure_contract:
- Raise explicit exceptions on data/schema/model failures.
testing_contract:
- Unit tests validate training pipeline on small fixtures.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.data.loader import load_training_dataframe
from ml.features import FEATURE_COLUMNS
from ml.models.nn_model import NeuralNetClassifier, train_neural_net
from ml.models.rf_model import train_random_forest
from ml.models.xgb_model import train_xgboost
from ml.registry import default_artifact_paths, ensure_artifact_root, save_labels


@dataclass(frozen=True)
class TrainConfig:
    seed: int
    test_size: float
    top_k: int


def _build_preprocessor() -> Pipeline:
    return Pipeline([("scaler", StandardScaler())])


def main() -> int:
    import sys
    from pathlib import Path
    cfg = TrainConfig(seed=1337, test_size=0.2, top_k=5)
    data_path = None
    if len(sys.argv) > 1:
        data_path = Path(sys.argv[1])
    df = load_training_dataframe(data_path)

    x = df.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=np.float32, copy=True)
    labels = sorted(df["label"].astype(str).unique().tolist())
    label_to_idx = {lab: i for i, lab in enumerate(labels)}
    y = df["label"].astype(str).map(label_to_idx).to_numpy(dtype=np.int64, copy=True)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=cfg.test_size, random_state=cfg.seed, stratify=y
    )

    pre = _build_preprocessor()
    x_train_t = pre.fit_transform(x_train)
    x_test_t = pre.transform(x_test)

    rf = train_random_forest(x_train_t, y_train, seed=cfg.seed)
    xgb = train_xgboost(x_train_t, y_train, seed=cfg.seed)
    nn: NeuralNetClassifier = train_neural_net(x_train_t, y_train, seed=cfg.seed, epochs=30)

    # Quick sanity evaluation (not persisted as a metric artifact yet).
    rf_acc = float((rf.predict(x_test_t) == y_test).mean())
    xgb_acc = float((xgb.predict(x_test_t) == y_test).mean())
    nn_acc = float((np.argmax(nn.predict_proba(x_test_t), axis=1) == y_test).mean())
    print(f"RF acc={rf_acc:.3f} XGB acc={xgb_acc:.3f} NN acc={nn_acc:.3f}")

    paths = default_artifact_paths()
    ensure_artifact_root(paths)
    joblib.dump(pre, paths.preprocessor_path)
    joblib.dump(rf, paths.rf_model_path)
    joblib.dump(xgb, paths.xgb_model_path)
    # torch save is inside nn wrapper (weights only).
    import torch

    torch.save(nn.net.state_dict(), paths.nn_model_path)
    save_labels(labels, paths)

    print(f"Wrote artifacts to: {paths.root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
