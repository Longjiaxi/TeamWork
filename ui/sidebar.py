from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QPushButton, QCheckBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize


class ChatItemWidget(QWidget):
    def __init__(self, chat_name):
        super().__init__()
        self.chat_name = chat_name
        self.is_dark = False
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4,2,4,2)
        layout.setSpacing(4)

        self.checkbox = QCheckBox()
        self.checkbox.setVisible(False)

        self.btn_name = QPushButton(chat_name)
        self.btn_name.setStyleSheet("QPushButton{border:none;background:transparent;text-align:left;}")

        self.btn_del = QPushButton("×")
        self.btn_del.setFixedSize(24,24)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.btn_name, stretch=1)
        layout.addWidget(self.btn_del)

    def set_batch_mode(self, open_batch:bool):
        self.checkbox.setVisible(open_batch)

    def set_dark_mode(self, enable:bool):
        self.is_dark = enable
        if enable:
            self.btn_name.setStyleSheet("QPushButton{border:none;background:transparent;text-align:left;color:#eeeeee;}")
            self.btn_del.setStyleSheet("QPushButton{border:none;background:transparent;color:#cccccc;} QPushButton:hover{color:#ff6b6b;}")
        else:
            self.btn_name.setStyleSheet("QPushButton{border:none;background:transparent;text-align:left;color:#222222;}")
            self.btn_del.setStyleSheet("QPushButton{border:none;background:transparent;color:#666666;} QPushButton:hover{color:#ff4444;}")


class Sidebar(QListWidget):
    new_chat_clicked = Signal()
    chat_switch = Signal(str)
    chat_delete = Signal(str)
    enter_batch_mode = Signal()
    exit_batch_mode = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setSpacing(6)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        font = QFont("微软雅黑", 10)
        self.setFont(font)
        self.batch_open = False
        self.is_dark = False

        self.clear()

        # ========== 自定义顶部行：新建聊天 + 批量≡按钮 ==========
        top_item = QListWidgetItem()
        top_widget = QWidget()
        top_widget.setStyleSheet("background: transparent;")
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(4, 4, 4, 4)
        top_layout.setSpacing(4)

        btn_new = QPushButton("＋新建聊天")
        btn_new.clicked.connect(self.new_chat_clicked.emit)
        self.add_btn_anim(btn_new)

        self.btn_batch = QPushButton("≡")
        self.btn_batch.setFixedSize(32, 32)
        self.add_btn_anim(self.btn_batch)
        self.btn_batch.clicked.connect(self.toggle_batch_mode)

        top_layout.addWidget(btn_new)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_batch)

        top_item.setSizeHint(top_widget.sizeHint())
        self.addItem(top_item)
        self.setItemWidget(top_item, top_widget)

        # 分割线
        sep_item = QListWidgetItem("───────────────────")
        sep_item.setFlags(Qt.NoItemFlags)
        self.addItem(sep_item)

    def add_btn_anim(self, btn: QPushButton):
        anim_down = QPropertyAnimation(btn, b"geometry")
        anim_down.setDuration(80)
        anim_up = QPropertyAnimation(btn, b"geometry")
        anim_up.setDuration(80)

        def pressed():
            r = btn.geometry()
            anim_down.setStartValue(r)
            anim_down.setEndValue(r.adjusted(1, 1, -1, -1))
            anim_down.start()

        def released():
            r = btn.geometry()
            anim_up.setStartValue(r)
            anim_up.setEndValue(r.adjusted(-1, -1, 1, 1))
            anim_up.start()

        btn.pressed.connect(pressed)
        btn.released.connect(released)

    def toggle_batch_mode(self):
        self.batch_open = not self.batch_open
        if self.batch_open:
            self.enter_batch_mode.emit()
        else:
            self.exit_batch_mode.emit()
        self.set_all_chat_item_batch(self.batch_open)

    def set_all_chat_item_batch(self, enable: bool):
        for i in range(self.count()):
            item = self.item(i)
            w = self.itemWidget(item)
            if w and hasattr(w, "set_batch_mode"):
                w.set_batch_mode(enable)

    def get_selected_chat_names(self):
        selected = []
        for i in range(self.count()):
            item = self.item(i)
            w = self.itemWidget(item)
            if w and hasattr(w, "checkbox") and hasattr(w, "chat_name"):
                if w.checkbox.isChecked():
                    selected.append(w.chat_name)
        return selected

    def toggle_select_all(self):
        widget_list = []
        all_checked = True
        for i in range(self.count()):
            item = self.item(i)
            w = self.itemWidget(item)
            if w and hasattr(w, "checkbox"):
                widget_list.append(w)
                if not w.checkbox.isChecked():
                    all_checked = False
        new_state = not all_checked
        for w in widget_list:
            w.checkbox.setChecked(new_state)

    def add_chat(self, chat_name):
        item = QListWidgetItem()
        chat_widget = ChatItemWidget(chat_name)
        item.setSizeHint(QSize(180,36))
        self.addItem(item)
        self.setItemWidget(item, chat_widget)
        # ✅ 修复lambda参数被bool覆盖的bug
        chat_widget.btn_name.clicked.connect(lambda checked=False, w=chat_widget: self.chat_switch.emit(w.chat_name))
        chat_widget.btn_del.clicked.connect(lambda checked=False, w=chat_widget: self.chat_delete.emit(w.chat_name))
        chat_widget.set_batch_mode(self.batch_open)
        return chat_widget

    def set_dark_mode(self, enable: bool):
        self.is_dark = enable
        if enable:
            self.setStyleSheet("""
            QListWidget{
                background:#1e1e1e;
                border:1px solid #3a3a3a;
                border-radius:10px;
                outline:none;
            }
            QListWidget::item{
                background:transparent;
            }
            """)
            btn_normal_style = """
            QPushButton {
                border: none;
                background-color: #323232;
                padding: 4px 8px;
                font-size: 14px;
                border-radius:6px;
                color:#eeeeee;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            """
            btn_batch_style = """
            QPushButton {
                border: none;
                background-color: #323232;
                font-size: 18px;
                border-radius:6px;
                color:#eeeeee;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            """
        else:
            self.setStyleSheet("""
            QListWidget{
                background:#ffffff;
                border:1px solid #DCDFE6;
                border-radius:10px;
                outline:none;
            }
            QListWidget::item{
                background:transparent;
            }
            """)
            btn_normal_style = """
            QPushButton {
                border: none;
                background-color: #f3f4f6;
                padding: 4px 8px;
                font-size: 14px;
                border-radius:6px;
                color:#444444;
            }
            QPushButton:hover {
                background-color:#e5e7eb;
            }
            """
            btn_batch_style = """
            QPushButton {
                border: none;
                background-color: #f3f4f6;
                font-size: 18px;
                border-radius:6px;
                color:#444444;
            }
            QPushButton:hover {
                background-color:#e5e7eb;
            }
            """
        self.btn_batch.setStyleSheet(btn_batch_style)
        for w in self.findChildren(QPushButton):
            if w != self.btn_batch:
                w.setStyleSheet(btn_normal_style)
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if hasattr(widget, "set_dark_mode"):
                widget.set_dark_mode(enable)
