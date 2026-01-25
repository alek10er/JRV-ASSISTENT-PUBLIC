from __future__ import annotations

from PySide6 import QtWidgets


class LogsPanel(QtWidgets.QTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)

    def append_log(self, text: str) -> None:
        self.append(text)
