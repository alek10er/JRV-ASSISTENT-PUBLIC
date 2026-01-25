from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from jarvis.commands.user_commands import UserCommand, UserCommandStore


class CommandCreatorWidget(QtWidgets.QWidget):
    def __init__(self, store: UserCommandStore) -> None:
        super().__init__()
        self._store = store
        self._store.load()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        self.name_input = QtWidgets.QLineEdit()
        self.type_select = QtWidgets.QComboBox()
        self.type_select.addItems(["site", "app", "hotkey"])
        self.payload_input = QtWidgets.QLineEdit()
        browse_button = QtWidgets.QPushButton("Выбрать файл")
        browse_button.clicked.connect(self._pick_file)

        payload_layout = QtWidgets.QHBoxLayout()
        payload_layout.addWidget(self.payload_input)
        payload_layout.addWidget(browse_button)

        form.addRow("Название", self.name_input)
        form.addRow("Тип", self.type_select)
        form.addRow("Данные", payload_layout)

        layout.addLayout(form)

        buttons_layout = QtWidgets.QHBoxLayout()
        add_button = QtWidgets.QPushButton("Сохранить")
        delete_button = QtWidgets.QPushButton("Удалить")
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)

        add_button.clicked.connect(self._save_command)
        delete_button.clicked.connect(self._delete_command)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemClicked.connect(self._fill_from_item)

        layout.addLayout(buttons_layout)
        layout.addWidget(self.list_widget)

        self._refresh_list()

    def _refresh_list(self) -> None:
        self.list_widget.clear()
        for command in self._store.list_commands():
            self.list_widget.addItem(f"{command.name} ({command.command_type})")

    def _pick_file(self) -> None:
        if self.type_select.currentText() != "app":
            return
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите приложение", filter="Executable (*.exe)")
        if path:
            self.payload_input.setText(path)

    def _save_command(self) -> None:
        name = self.name_input.text().strip()
        payload = self.payload_input.text().strip()
        if not name or not payload:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        command_type = self.type_select.currentText()
        if not self._store.update_command(name, command_type, payload):
            self._store.add_command(UserCommand(name=name, command_type=command_type, payload=payload))
        self._refresh_list()

    def _delete_command(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            return
        self._store.delete_command(name)
        self._refresh_list()

    def _fill_from_item(self, item: QtWidgets.QListWidgetItem) -> None:
        text = item.text()
        name = text.split("(")[0].strip()
        for command in self._store.list_commands():
            if command.name == name:
                self.name_input.setText(command.name)
                self.type_select.setCurrentText(command.command_type)
                self.payload_input.setText(command.payload)
                break
