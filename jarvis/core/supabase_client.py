from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests

from jarvis.constants import SUPABASE_TABLE

logger = logging.getLogger(__name__)


@dataclass
class ActivationResult:
    ok: bool
    message: str


class SupabaseClient:
    def __init__(self, url: str, api_key: str) -> None:
        self._url = url.rstrip("/")
        self._api_key = api_key

    def _headers(self) -> dict:
        return {
            "apikey": self._api_key,
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def find_subscription(self, key: str) -> Optional[dict]:
        try:
            response = requests.get(
                f"{self._url}/rest/v1/{SUPABASE_TABLE}",
                headers=self._headers(),
                params={"subscription_key": f"eq.{key}"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                return None
            return data[0]
        except requests.RequestException as exc:
            logger.error("Supabase request failed: %s", exc)
            return None

    def update_hwid(self, record_id: int, hwid: str) -> bool:
        try:
            response = requests.patch(
                f"{self._url}/rest/v1/{SUPABASE_TABLE}",
                headers=self._headers(),
                params={"id": f"eq.{record_id}"},
                json={"device_count": hwid},
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.error("Supabase update failed: %s", exc)
            return False

    def activate(self, key: str, hwid: str) -> ActivationResult:
        record = self.find_subscription(key)
        if not record:
            return ActivationResult(False, "Неверный ключ активации")

        device = str(record.get("device_count", "0"))
        record_id = record.get("id")
        if device in {"0", "", "None"}:
            if record_id is None:
                return ActivationResult(False, "Ошибка записи устройства")
            updated = self.update_hwid(record_id, hwid)
            if not updated:
                return ActivationResult(False, "Не удалось сохранить устройство")
            return ActivationResult(True, "Активация успешна")

        if device == hwid:
            return ActivationResult(True, "Активация подтверждена")

        return ActivationResult(False, "Incorrect HWID")
