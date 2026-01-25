from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class LoadingScreen(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jarvis 5.1")
        self.setFixedSize(420, 200)
        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("Инициализация...")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)

    def update_status(self, text: str, value: int) -> None:
        self.label.setText(text)
        self.progress.setValue(value)
        QtWidgets.QApplication.processEvents()
