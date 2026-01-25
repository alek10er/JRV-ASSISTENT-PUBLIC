from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from jarvis.ui.command_creator import CommandCreatorWidget
from jarvis.ui.logs_panel import LogsPanel


class MainWindow(QtWidgets.QMainWindow):
    status_changed = QtCore.Signal(str)

    def __init__(self, command_creator: CommandCreatorWidget) -> None:
        super().__init__()
        self.setWindowTitle("Jarvis 5.1")
        self.setMinimumSize(800, 600)
        self._logs_panel = LogsPanel()
        self._command_creator = command_creator
        self._build_ui()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        self.status_label = QtWidgets.QLabel("Сон")
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        button_layout = QtWidgets.QHBoxLayout()
        logs_button = QtWidgets.QPushButton("Логи")
        logs_button.clicked.connect(self._toggle_logs)
        button_layout.addWidget(logs_button)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._command_creator, "Создатель команд")

        layout.addWidget(self.status_label)
        layout.addLayout(button_layout)
        layout.addWidget(tabs)
        layout.addWidget(self._logs_panel)

        self._logs_panel.setVisible(False)
        self.setCentralWidget(central)

    def update_status(self, status: str) -> None:
        self.status_label.setText(status)

    def append_log(self, text: str) -> None:
        self._logs_panel.append_log(text)

    def _toggle_logs(self) -> None:
        self._logs_panel.setVisible(not self._logs_panel.isVisible())
