from __future__ import annotations

import json
import logging
import queue
import threading
from dataclasses import dataclass
from typing import Callable, Optional

import sounddevice as sd
from vosk import KaldiRecognizer, Model

logger = logging.getLogger(__name__)


@dataclass
class RecognitionConfig:
    model_path: str
    samplerate: int = 16000
    device: Optional[int] = None


class VoskRecognizerWorker:
    def __init__(self, config: RecognitionConfig, on_result: Callable[[str], None]) -> None:
        self._config = config
        self._on_result = on_result
        self._queue: queue.Queue[bytes] = queue.Queue()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _callback(self, indata, frames, time, status) -> None:  # noqa: D401 - callback
        if status:
            logger.warning("Audio status: %s", status)
        self._queue.put(bytes(indata))

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        try:
            model = Model(self._config.model_path)
            recognizer = KaldiRecognizer(model, self._config.samplerate)
        except Exception as exc:
            logger.error("Ошибка загрузки модели Vosk: %s", exc)
            return

        try:
            with sd.RawInputStream(
                samplerate=self._config.samplerate,
                blocksize=8000,
                device=self._config.device,
                dtype="int16",
                channels=1,
                callback=self._callback,
            ):
                while not self._stop_event.is_set():
                    try:
                        data = self._queue.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            self._on_result(text)
        except Exception as exc:
            logger.error("Ошибка аудиопотока: %s", exc)
