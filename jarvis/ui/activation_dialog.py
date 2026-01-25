from __future__ import annotations

from PySide6 import QtWidgets


class ActivationDialog(QtWidgets.QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Активация Jarvis")
        self.setModal(True)
        layout = QtWidgets.QVBoxLayout(self)

        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText("Введите ключ активации")
        layout.addWidget(QtWidgets.QLabel("Введите ключ активации"))
        layout.addWidget(self.input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def activation_key(self) -> str:
        return self.input.text().strip()
