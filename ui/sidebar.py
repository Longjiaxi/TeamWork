from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve


class Sidebar(QListWidget):
    # 信号定义保留（防止编译报错，暂时不接业务逻辑）
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

        # 新建聊天按钮
        btn_new = QPushButton("＋新建聊天")
        # 【重点】注释掉业务信号发射，只保留UI按钮
        # btn_new.clicked.connect(self.new_chat_clicked.emit)
        self.add_btn_anim(btn_new)

        # 批量多选按钮
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

        # 分割线
        sep_item = QListWidgetItem("───────────────────")
        sep_item.setFlags(Qt.NoItemFlags)
        self.addItem(sep_item)

        # 初始化加载浅色样式
        self.set_dark_mode(False)

    def add_btn_anim(self, btn:QPushButton):
        """侧边栏按钮按压动画"""
        anim_down = QPropertyAnimation(btn, b"geometry")
        anim_down.setDuration(80)
        anim_up = QPropertyAnimation(btn, b"geometry")
        anim_up.setDuration(80)
        def pressed():
            r=btn.geometry()
            anim_down.setStartValue(r)
            anim_down.setEndValue(r.adjusted(1,1,-1,-1))
            anim_down.start()
        def released():
            r=btn.geometry()
            anim_up.setStartValue(r)
            anim_up.setEndValue(r.adjusted(-1,-1,1,1))
            anim_up.start()
        btn.pressed.connect(pressed)
        btn.released.connect(released)

    def add_chat(self, name):
        list_item = QListWidgetItem()
        custom_widget = ChatListItem(name)
        # 【注释业务信号】只渲染UI，点击item不会触发会话切换/删除
        # custom_widget.switch_chat.connect(self.chat_switch.emit)
        # custom_widget.delete_chat.connect(self.chat_delete.emit)
        list_item.setSizeHint(custom_widget.sizeHint())
        self.addItem(list_item)
        self.setItemWidget(list_item, custom_widget)

    def toggle_batch_mode(self):
        self.batch_open = not self.batch_open
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if isinstance(widget, ChatListItem):
                widget.set_batch_mode(self.batch_open)
        # 【注释业务信号】批量模式切换只修改UI，不再通知主窗口
        # if self.batch_open:
        #     self.enter_batch_mode.emit()
        # else:
        #     self.exit_batch_mode.emit()

    def get_checked_chat_names(self):
        res = []
        for i in range(self.count()):
            item = self.item(i)
            w = self.itemWidget(item)
            if isinstance(w, ChatListItem) and w.get_checked():
                res.append(w.chat_name)
        return res

    def set_dark_mode(self, enable: bool):
        self.is_dark = enable
        if enable:
            # 深色模式
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
            # 浅色模式
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
        # 批量按钮优先赋值
        self.btn_batch.setStyleSheet(btn_batch_style)
        # 其余普通按钮
        for w in self.findChildren(QPushButton):
            if w != self.btn_batch:
                w.setStyleSheet(btn_normal_style)
