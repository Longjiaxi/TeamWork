from PySide6.QtWidgets import (QListWidget, QListWidgetItem, QWidget, QHBoxLayout,
                               QPushButton, QCheckBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtCore import QSize


class ChatItemWidget(QWidget):
    def __init__(self, chat_name):
        super().__init__()
        self.chat_name = chat_name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4,4,4,4)
        layout.setSpacing(6)

        self.checkbox = QCheckBox()
        self.checkbox.setVisible(False)
        layout.addWidget(self.checkbox)

        self.btn_name = QPushButton(chat_name)
        self.btn_name.setFlat(True)
        layout.addWidget(self.btn_name, stretch=1)

        self.btn_del = QPushButton("×")
        self.btn_del.setFixedSize(24,24)
        layout.addWidget(self.btn_del)
        self.setMinimumHeight(36)

    def set_batch_mode(self, enable: bool):
        self.checkbox.setVisible(enable)
        if not enable:
            self.checkbox.setChecked(False)


class Sidebar(QListWidget):
    new_chat_clicked = Signal()
    chat_switch = Signal(str)
    chat_delete = Signal(str)
    menu_clicked = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setSpacing(2)
        self.batch_mode = False

    def on_menu_click(self):
        self.batch_mode = not self.batch_mode
        self.set_all_chat_item_batch(self.batch_mode)
        self.menu_clicked.emit(self.batch_mode)

    def set_all_chat_item_batch(self, enable):
        for i in range(self.count()):
            item = self.item(i)
            w = self.itemWidget(item)
            if w and hasattr(w, "set_batch_mode"):
                w.set_batch_mode(enable)

    def add_chat(self, chat_name):
        item = QListWidgetItem()
        chat_widget = ChatItemWidget(chat_name)
        item.setSizeHint(chat_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, chat_widget)
        chat_widget.btn_name.clicked.connect(lambda: self.chat_switch.emit(chat_name))
        chat_widget.btn_del.clicked.connect(lambda: self.chat_delete.emit(chat_name))
        chat_widget.set_batch_mode(False)

    def get_selected_chat_names(self):
        selected = []
        for i in range(self.count()):
            item = self.item(i)
            w = self.itemWidget(item)
            if w and hasattr(w, "checkbox"):
                if w.checkbox.isChecked():
                    selected.append(w.chat_name)
        return selected

    def close_batch_mode(self):
        self.batch_mode = False
        self.set_all_chat_item_batch(False)
        self.menu_clicked.emit(False)
