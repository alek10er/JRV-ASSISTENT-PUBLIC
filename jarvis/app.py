from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import List, Tuple

import sounddevice as sd
from PySide6 import QtWidgets

from jarvis.audio.recognition import RecognitionConfig, VoskRecognizerWorker
from jarvis.audio.sound_player import play_random, play_sound
from jarvis.commands.executor import CommandExecutor
from jarvis.commands.user_commands import UserCommandStore
from jarvis.config.paths import AppPaths
from jarvis.config.settings import SettingsManager
from jarvis.constants import APP_NAME, APP_VERSION
from jarvis.core.hwid import get_hwid
from jarvis.core.integrity import check_integrity
from jarvis.core.logger import UILogHandler, setup_logging
from jarvis.core.supabase_client import SupabaseClient
from jarvis.ui.activation_dialog import ActivationDialog
from jarvis.ui.command_creator import CommandCreatorWidget
from jarvis.ui.loading_screen import LoadingScreen
from jarvis.ui.main_window import MainWindow
from jarvis.ui.welcome_window import WelcomeWindow
from jarvis.utils.files import load_json
from jarvis.utils.text_corrections import apply_corrections

logger = logging.getLogger(__name__)


def list_microphones() -> List[Tuple[int, str]]:
    devices = sd.query_devices()
    microphones = []
    for idx, device in enumerate(devices):
        if device.get("max_input_channels", 0) > 0:
            microphones.append((idx, device.get("name", f"Device {idx}")))
    return microphones


class JarvisController:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths
        self.settings_manager = SettingsManager(paths.configs_dir / "settings.json")
        self.settings = self.settings_manager.load()
        self.hwid = get_hwid()
        self.corrections = load_json(paths.configs_dir / "corrections.json", {})
        self.phrases = load_json(
            paths.configs_dir / "phrases.json",
            {"activation_phrases": [], "deactivation_phrases": []},
        )
        self.sounds = load_json(paths.configs_dir / "sounds.json", {})
        self.user_commands = UserCommandStore(paths.configs_dir / "user_commands.json")
        self.user_commands.load()
        self.executor = CommandExecutor(self.user_commands)
        self.worker: VoskRecognizerWorker | None = None
        self.state = "sleep"
        self.main_window: MainWindow | None = None

    def activate_if_needed(self) -> bool:
        if self.settings.activation_key and self.settings.hwid:
            logger.info("Проверка сохраненной активации")
            client = SupabaseClient(self.settings.supabase.url, self.settings.supabase.api_key)
            result = client.activate(self.settings.activation_key, self.settings.hwid)
            if result.ok:
                return True
            QtWidgets.QMessageBox.critical(None, "Ошибка", result.message)
            return False

        dialog = ActivationDialog()
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return False

        key = dialog.activation_key()
        if not key:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Ключ активации не введен")
            return False

        client = SupabaseClient(self.settings.supabase.url, self.settings.supabase.api_key)
        result = client.activate(key, self.hwid)
        if not result.ok:
            QtWidgets.QMessageBox.critical(None, "Ошибка", result.message)
            return False

        self.settings.activation_key = key
        self.settings.hwid = self.hwid
        self.settings_manager.save()
        return True

    def start_recognition(self, device_index: int | None) -> None:
        config = RecognitionConfig(model_path=str(self.paths.model_dir), device=device_index)
        self.worker = VoskRecognizerWorker(config, self.on_text)
        self.worker.start()

    def stop_recognition(self) -> None:
        if self.worker:
            self.worker.stop()

    def on_text(self, text: str) -> None:
        logger.info("Распознано: %s", text)
        corrected = apply_corrections(text, self.corrections)
        logger.info("После исправлений: %s", corrected)

        activation_phrases = [p.lower() for p in self.phrases.get("activation_phrases", [])]
        deactivation_phrases = [p.lower() for p in self.phrases.get("deactivation_phrases", [])]

        if self.state == "sleep":
            if any(phrase in corrected for phrase in activation_phrases):
                self.state = "active"
                self._update_status("Слушаю")
                self._play_sound("activation")
            return

        if any(phrase in corrected for phrase in deactivation_phrases):
            self.state = "sleep"
            self._update_status("Сон")
            self._play_sound("deactivation")
            return

        self._update_status("Выполняю команду")
        result = self.executor.execute(corrected)
        if result.ok:
            logger.info("Найдена команда: %s", result.command_name)
            self._play_success()
        else:
            logger.warning("Команда не найдена")
            self._play_sound("error")
        self._update_status("Слушаю")

    def _play_sound(self, key: str) -> None:
        value = self.sounds.get(key)
        if not value:
            return
        path = self.paths.sound_dir / value
        play_sound(path)

    def _play_success(self) -> None:
        values = self.sounds.get("success", [])
        paths = [self.paths.sound_dir / name for name in values]
        play_random(paths)

    def _update_status(self, status: str) -> None:
        if self.main_window:
            self.main_window.update_status(status)


def run() -> None:
    setup_logging()
    app = QtWidgets.QApplication(sys.argv)
    paths = AppPaths.detect()

    loading = LoadingScreen()
    loading.show()
    loading.update_status("Проверка файлов...", 10)
    integrity = check_integrity(paths.base_dir)
    if not integrity.ok:
        QtWidgets.QMessageBox.critical(
            None,
            "Ошибка",
            "Переустановите программу полностью. Не найдены файлы:\n"
            + "\n".join(integrity.missing),
        )
        sys.exit(1)

    controller = JarvisController(paths)
    loading.update_status("Проверка активации...", 40)
    if not controller.activate_if_needed():
        sys.exit(1)

    microphones = list_microphones()
    loading.update_status("Запуск интерфейса...", 70)
    welcome = WelcomeWindow(microphones, controller.settings.selected_microphone)

    def on_proceed(selected_name: str) -> None:
        controller.settings.selected_microphone = selected_name
        controller.settings_manager.save()
        command_creator = CommandCreatorWidget(controller.user_commands)
        main_window = MainWindow(command_creator)
        controller.main_window = main_window

        logger_handler = UILogHandler(main_window.append_log)
        logger_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(logger_handler)

        main_window.append_log(f"Версия: {APP_NAME}")
        main_window.show()
        welcome.close()

        device_index = None
        for idx, name in microphones:
            if name == selected_name:
                device_index = idx
                break

        controller.start_recognition(device_index)

    welcome.proceed.connect(on_proceed)

    loading.close()
    welcome.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
