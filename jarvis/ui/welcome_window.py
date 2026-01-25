from __future__ import annotations

from typing import List, Tuple

from PySide6 import QtCore, QtGui, QtWidgets


class WelcomeWindow(QtWidgets.QWidget):
    proceed = QtCore.Signal(str)

    def __init__(self, microphones: List[Tuple[int, str]], selected: str) -> None:
        super().__init__()
        self._microphones = microphones
        self._selected = selected
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle("Jarvis 5.1")
        self.setMinimumSize(640, 420)
        layout = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QLabel("Добро пожаловать в Jarvis 5.1")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold;")

        info = QtWidgets.QLabel(
            "О программе: голосовой помощник с офлайн распознаванием речи. "
            "Здесь будет описание возможностей Jarvis 5.1."
        )
        info.setWordWrap(True)

        self.microphone_combo = QtWidgets.QComboBox()
        for _, name in self._microphones:
            self.microphone_combo.addItem(name)
        if self._selected:
            idx = self.microphone_combo.findText(self._selected)
            if idx >= 0:
                self.microphone_combo.setCurrentIndex(idx)

        proceed_button = QtWidgets.QPushButton("Далее")
        proceed_button.clicked.connect(self._proceed)

        layout.addWidget(header)
        layout.addWidget(info)
        layout.addWidget(QtWidgets.QLabel("Выберите микрофон:"))
        layout.addWidget(self.microphone_combo)
        layout.addStretch()
        layout.addWidget(proceed_button)

        self.setStyleSheet(
            "QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #1c1c2b, stop:1 #2d2d44); color: #f0f0f0; }"
        )

    def _proceed(self) -> None:
        self.proceed.emit(self.microphone_combo.currentText())
