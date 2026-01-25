from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    base_dir: Path
    configs_dir: Path
    sound_dir: Path
    model_dir: Path

    @classmethod
    def detect(cls) -> "AppPaths":
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).resolve().parents[2]

        return cls(
            base_dir=base_dir,
            configs_dir=base_dir / "configs",
            sound_dir=base_dir / "sound",
            model_dir=base_dir / "vosk-model",
        )
