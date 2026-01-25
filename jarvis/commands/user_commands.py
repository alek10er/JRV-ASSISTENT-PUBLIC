from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class UserCommand:
    name: str
    command_type: str
    payload: str


class UserCommandStore:
    SCHEMA_VERSION = 1

    def __init__(self, path: Path) -> None:
        self._path = path
        self._commands: List[UserCommand] = []

    def load(self) -> List[UserCommand]:
        if not self._path.exists():
            self.save()
            return self._commands

        data = json.loads(self._path.read_text(encoding="utf-8"))
        items = data.get("commands", [])
        self._commands = [UserCommand(**item) for item in items]
        return self._commands

    def save(self) -> None:
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "commands": [command.__dict__ for command in self._commands],
        }
        self._path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def list_commands(self) -> List[UserCommand]:
        return list(self._commands)

    def add_command(self, command: UserCommand) -> None:
        self._commands.append(command)
        self.save()

    def update_command(self, name: str, command_type: str, payload: str) -> bool:
        for command in self._commands:
            if command.name == name:
                command.command_type = command_type
                command.payload = payload
                self.save()
                return True
        return False

    def delete_command(self, name: str) -> bool:
        for idx, command in enumerate(self._commands):
            if command.name == name:
                self._commands.pop(idx)
                self.save()
                return True
        return False

    def find_match(self, text: str) -> Optional[UserCommand]:
        lowered = text.lower()
        for command in self._commands:
            if command.name.lower() in lowered:
                return command
        return None
