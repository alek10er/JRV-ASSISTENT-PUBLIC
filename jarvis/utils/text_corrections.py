from __future__ import annotations

from typing import Dict


def apply_corrections(text: str, corrections: Dict[str, str]) -> str:
    corrected = text
    for wrong, right in sorted(corrections.items(), key=lambda item: len(item[0]), reverse=True):
        corrected = corrected.replace(wrong, right)
    return corrected
