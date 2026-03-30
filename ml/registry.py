"""
@design-guard
role: Define how trained artifacts are stored and loaded for inference.
layer: service
non_goals:
- Implement web serving or UI.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [artifact_paths_contract]
invariants:
- Artifacts are stored under ./artifacts and excluded from git.
authority:
  decides: [artifact_naming_and_layout]
  delegates: []
extension_policy:
- Add versioning by introducing new directories, not by mutating existing formats.
failure_contract:
- Raise explicit exceptions on missing/corrupt artifacts.
testing_contract:
- Unit tests validate save/load roundtrips for small objects.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib


@dataclass(frozen=True)
class ArtifactPaths:
    root: Path

    @property
    def preprocessor_path(self) -> Path:
        return self.root / "preprocessor.joblib"

    @property
    def rf_model_path(self) -> Path:
        return self.root / "random_forest.joblib"

    @property
    def xgb_model_path(self) -> Path:
        return self.root / "xgboost.joblib"

    @property
    def nn_model_path(self) -> Path:
        return self.root / "neural_net.pt"

    @property
    def labels_path(self) -> Path:
        return self.root / "labels.json"


def default_artifact_paths() -> ArtifactPaths:
    return ArtifactPaths(root=Path("artifacts"))


def ensure_artifact_root(paths: ArtifactPaths) -> None:
    paths.root.mkdir(parents=True, exist_ok=True)


def save_labels(labels: list[str], paths: ArtifactPaths) -> None:
    ensure_artifact_root(paths)
    paths.labels_path.write_text(json.dumps(labels, indent=2), encoding="utf-8")


def load_labels(paths: ArtifactPaths) -> list[str]:
    text = paths.labels_path.read_text(encoding="utf-8")
    labels = json.loads(text)
    if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
        raise ValueError("Invalid labels.json format")
    return labels


def load_joblib(path: Path) -> object:
    return joblib.load(path)
