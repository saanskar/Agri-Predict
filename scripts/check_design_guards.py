"""
@design-guard
role: Enforce that every Python source file starts with a design-guard block.
layer: service
non_goals:
- Full static analysis of guard contents.
boundaries:
  depends_on_layers: [service]
  exposes: [cli_script_exit_code]
invariants:
- All checked .py files must include "@design-guard" in the first 50 lines.
authority:
  decides: [which_files_to_check, enforcement_policy]
  delegates: []
extension_policy:
- Add ignore rules only for generated/vendor code; keep default strict.
failure_contract:
- Exit with non-zero status and print missing-file paths.
testing_contract:
- Covered indirectly by CI; keep logic deterministic and side-effect free.
references:
- docs/ADRs/0003-design-guards.md
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScanResult:
    missing: tuple[Path, ...]


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_EXCLUDES: tuple[str, ...] = (
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "artifacts",
)


def _should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return any(ex in parts for ex in DEFAULT_EXCLUDES)


def _has_design_guard(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return True
    head = "\n".join(text.splitlines()[:50])
    return "@design-guard" in head


def scan_repo(root: Path) -> ScanResult:
    missing: list[Path] = []
    for dirpath, _, filenames in os.walk(root):
        base = Path(dirpath)
        if _should_skip(base):
            continue
        for name in filenames:
            if not name.endswith(".py"):
                continue
            file_path = base / name
            if _should_skip(file_path):
                continue
            if not _has_design_guard(file_path):
                missing.append(file_path.relative_to(root))
    missing_sorted = tuple(sorted(missing))
    return ScanResult(missing=missing_sorted)


def main() -> int:
    result = scan_repo(ROOT)
    if not result.missing:
        print("OK: design-guard found in all checked Python files.")
        return 0

    print("ERROR: Missing @design-guard in the following files:")
    for path in result.missing:
        print(f"- {path.as_posix()}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
