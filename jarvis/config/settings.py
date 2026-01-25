from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class RecognitionSettings:
    timeout: float = 6.0
    phrase_time_limit: float = 5.0
    energy_threshold: int = 300


@dataclass
class SupabaseSettings:
    url: str = "https://YOUR_PROJECT.supabase.co"
    api_key: str = "YOUR_ANON_KEY"


@dataclass
class AppSettings:
    activation_key: str = ""
    hwid: str = ""
    selected_microphone: str = ""
    recognition: RecognitionSettings = field(default_factory=RecognitionSettings)
    supabase: SupabaseSettings = field(default_factory=SupabaseSettings)


class SettingsManager:
    def __init__(self, path: Path) -> None:
        self._path = path
        self.settings = AppSettings()

    def load(self) -> AppSettings:
        if not self._path.exists():
            self.save()
            return self.settings

        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return self.settings

        self.settings = AppSettings(
            activation_key=data.get("activation_key", ""),
            hwid=data.get("hwid", ""),
            selected_microphone=data.get("selected_microphone", ""),
            recognition=RecognitionSettings(**data.get("recognition", {})),
            supabase=SupabaseSettings(**data.get("supabase", {})),
        )
        return self.settings

    def save(self) -> None:
        payload: Dict[str, Any] = {
            "activation_key": self.settings.activation_key,
            "hwid": self.settings.hwid,
            "selected_microphone": self.settings.selected_microphone,
            "recognition": self.settings.recognition.__dict__,
            "supabase": self.settings.supabase.__dict__,
        }
        self._path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
