from __future__ import annotations

import logging
import subprocess
import webbrowser
from dataclasses import dataclass
from typing import Optional

import keyboard

from jarvis.commands.builtin import BUILTIN_COMMANDS
from jarvis.commands.user_commands import UserCommand, UserCommandStore

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    ok: bool
    message: str
    command_name: Optional[str] = None


class CommandExecutor:
    def __init__(self, store: UserCommandStore) -> None:
        self._store = store

    def execute(self, text: str) -> CommandResult:
        lowered = text.lower()
        for phrase, handler in BUILTIN_COMMANDS.items():
            if phrase in lowered:
                try:
                    message = handler()
                    return CommandResult(True, message, phrase)
                except Exception as exc:
                    logger.error("Ошибка команды %s: %s", phrase, exc)
                    return CommandResult(False, "Ошибка выполнения", phrase)

        user_command = self._store.find_match(lowered)
        if user_command:
            return self._execute_user(user_command)

        return CommandResult(False, "Команда не найдена")

    def _execute_user(self, command: UserCommand) -> CommandResult:
        try:
            if command.command_type == "site":
                webbrowser.open(command.payload)
                return CommandResult(True, "Открываю сайт", command.name)
            if command.command_type == "app":
                subprocess.Popen(command.payload)
                return CommandResult(True, "Запускаю приложение", command.name)
            if command.command_type == "hotkey":
                keyboard.send(command.payload)
                return CommandResult(True, "Отправляю сочетание", command.name)
            return CommandResult(False, "Неизвестный тип команды", command.name)
        except Exception as exc:
            logger.error("Ошибка пользовательской команды %s: %s", command.name, exc)
            return CommandResult(False, "Ошибка пользовательской команды", command.name)
