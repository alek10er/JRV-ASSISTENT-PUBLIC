from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Iterable, Optional

import sounddevice as sd
import soundfile as sf

logger = logging.getLogger(__name__)


def play_sound(path: Path) -> None:
    try:
        data, samplerate = sf.read(str(path), dtype="float32")
        sd.play(data, samplerate)
    except Exception as exc:
        logger.error("Ошибка воспроизведения звука %s: %s", path, exc)


def play_random(paths: Iterable[Path]) -> Optional[Path]:
    items = list(paths)
    if not items:
        return None
    choice = random.choice(items)
    play_sound(choice)
    return choice
