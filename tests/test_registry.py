"""
@design-guard
role: Unit tests for ML artifact registry helpers.
layer: service
non_goals:
- Validate full training pipeline.
boundaries:
  depends_on_layers: [service]
  exposes: [pytest_tests]
invariants:
- Registry helpers are deterministic and filesystem-safe.
authority:
  decides: [registry_test_contract]
  delegates: []
extension_policy:
- Add tests when adding new artifact types.
failure_contract:
- Fail with clear assertions.
testing_contract:
- Unit tests only; use temporary directories.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pytest

from ml.registry import ArtifactPaths, ensure_artifact_root, load_joblib, load_labels, save_labels


def test_ensure_artifact_root_creates_directory(tmp_path: Path) -> None:
    paths = ArtifactPaths(root=tmp_path / "artifacts")
    assert not paths.root.exists()
    ensure_artifact_root(paths)
    assert paths.root.exists()


def test_save_and_load_labels_roundtrip(tmp_path: Path) -> None:
    paths = ArtifactPaths(root=tmp_path / "artifacts")
    save_labels(["a", "b", "c"], paths)
    assert load_labels(paths) == ["a", "b", "c"]


def test_load_labels_rejects_invalid_format(tmp_path: Path) -> None:
    paths = ArtifactPaths(root=tmp_path / "artifacts")
    ensure_artifact_root(paths)
    paths.labels_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    with pytest.raises(ValueError, match=r"Invalid labels\.json format"):
        load_labels(paths)


def test_load_joblib_loads_saved_object(tmp_path: Path) -> None:
    obj = {"x": 1, "y": 2}
    p = tmp_path / "obj.joblib"
    joblib.dump(obj, p)
    assert load_joblib(p) == obj
