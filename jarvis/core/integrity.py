from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class IntegrityResult:
    ok: bool
    missing: List[str]


def check_integrity(base_dir: Path) -> IntegrityResult:
    required_paths = [
        base_dir / "vosk-model",
        base_dir / "sound",
        base_dir / "configs",
        base_dir / "configs" / "corrections.json",
        base_dir / "configs" / "phrases.json",
        base_dir / "configs" / "settings.json",
        base_dir / "configs" / "sounds.json",
        base_dir / "configs" / "user_commands.json",
    ]

    missing = [str(path) for path in required_paths if not path.exists()]
    return IntegrityResult(ok=not missing, missing=missing)
