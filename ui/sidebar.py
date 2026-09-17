from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QPushButton, QLabel, QMessageBox, QFrame
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve


class ChatListItem(QWidget):
    # 信号：选中对话、删除当前对话
    switch_chat = Signal()
    delete_chat = Signal()

    def __init__(self, chat_name):
        super().__init__()
        self.chat_name = chat_name
        self.batch_mode = False

        # 水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # 对话名称文本
        self.label_name = QLabel(chat_name)
        layout.addWidget(self.label_name)

        layout.addStretch() # 占位，把按钮挤到最右侧

        # ==========删除按钮 × 叉号正方形按钮==========
        self.btn_del = QPushButton("×")
        self.btn_del.setFixedSize(28, 28) # 正方形
        self.btn_del.setStyleSheet("""
            QPushButton{
                border:none;
                background:transparent;
                font-size:20px;
                color:#444444;
            }
            QPushButton:hover{
                background:#dddddd;
                border-radius:4px;
            }
        """)
        self.btn_del.clicked.connect(self.delete_chat.emit)
        layout.addWidget(self.btn_del)

        self.setLayout(layout)

    def set_batch_mode(self, open_flag):
        self.batch_mode = open_flag

    def get_checked(self):
        return False


class Sidebar(QListWidget):
    # 定义信号
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

        # ==========顶部条目：新建聊天 + 右侧≡批量按钮==========
        top_item = QListWidgetItem()
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(4, 4, 4, 4)
        top_layout.setSpacing(4)

        # 新建聊天按钮
        btn_new = QPushButton("＋新建聊天")
        btn_new.clicked.connect(self.new_chat_clicked.emit)
        self.add_btn_anim(btn_new)

        # 保留右上角批量≡按钮
        self.btn_batch = QPushButton("≡")
        self.btn_batch.setFixedSize(32, 32)
        self.btn_batch.clicked.connect(self.toggle_batch_mode)
        self.add_btn_anim(self.btn_batch)

        top_layout.addWidget(btn_new)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_batch)

        top_item.setSizeHint(top_widget.sizeHint())
        self.addItem(top_item)
        self.setItemWidget(top_item, top_widget)

        # =====================【新增：水平分割线】=====================
        line_item = QListWidgetItem()
        line_widget = QWidget()
        line_layout = QHBoxLayout(line_widget)
        line_layout.setContentsMargins(8, 4, 8, 4)
        line_layout.setSpacing(0)
        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        h_line.setStyleSheet("background:#dcdfe6; height:1px;")
        line_layout.addWidget(h_line)
        line_item.setSizeHint(line_widget.sizeHint())
        # ==========修复这一行，分割线不可选中==========
        line_item.setFlags(line_item.flags() & ~Qt.ItemIsSelectable)
        self.addItem(line_item)
        self.setItemWidget(line_item, line_widget)

        # 初始化主题样式
        self.set_dark_mode(False)

    def add_btn_anim(self, btn: QPushButton):
        """按钮点击动画"""
        anim_down = QPropertyAnimation(btn, b"geometry")
        anim_down.setDuration(80)
        anim_up = QPropertyAnimation(btn, b"geometry")
        anim_up.setDuration(80)

        def pressed():
            r = btn.geometry()
            anim_down.setStartValue(r)
            anim_down.setEndValue(r.adjusted(1,1,-1,-1))
            anim_down.start()

        def released():
            r = btn.geometry()
            anim_up.setStartValue(r)
            anim_up.setEndValue(r.adjusted(-1,-1,1,1))
            anim_up.start()

        btn.pressed.connect(pressed)
        btn.released.connect(released)

    def add_chat(self, name):
        """添加对话条目，每条对话带×删除按钮"""
        list_item = QListWidgetItem()
        custom_widget = ChatListItem(name)
        custom_widget.switch_chat.connect(lambda: self.chat_switch.emit(name))
        custom_widget.delete_chat.connect(lambda: self.chat_delete.emit(name))
        list_item.setSizeHint(custom_widget.sizeHint())
        self.addItem(list_item)
        self.setItemWidget(list_item, custom_widget)

    def toggle_batch_mode(self):
        """顶部≡批量按钮点击事件，预留功能"""
        self.batch_open = not self.batch_open
        if self.batch_open:
            self.enter_batch_mode.emit()
        else:
            self.exit_batch_mode.emit()

    def get_checked_chat_names(self):
        return []

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
                padding:4px 8px;
                font-size:14px;
                border-radius:6px;
                color:#eeeeee;
            }
            QPushButton:hover {
                background-color:#3d3d3d;
            }
            """
            # 深色模式分割线颜色
            for i in range(self.count()):
                item_w = self.itemWidget(self.item(i))
                if hasattr(item_w, "findChildren"):
                    frames = item_w.findChildren(QFrame)
                    for f in frames:
                        f.setStyleSheet("background:#444444;height:1px;")
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
                padding:4px 8px;
                font-size:14px;
                border-radius:6px;
                color:#444444;
            }
            QPushButton:hover {
                background-color:#e5e7eb;
            }
            """
        # 遍历所有按钮，排除批量按钮，设置样式
        for w in self.findChildren(QPushButton):
            if w != self.btn_batch:
                w.setStyleSheet(btn_normal_style)