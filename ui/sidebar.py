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
    # 新增信号：点击菜单按钮，通知主窗口显示底部操作栏
    menu_clicked = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setSpacing(2)
        self.batch_mode = False  # 标记当前是否开启批量多选

        # 顶部行：新建聊天 + ☰按钮
        top_item = QListWidgetItem()
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(4,4,4,4)
        top_layout.setSpacing(6)

        btn_new = QPushButton("+ 新建聊天")
        btn_new.clicked.connect(self.new_chat_clicked.emit)
        top_layout.addWidget(btn_new)

        # ====== 关键修复：增加拉伸，将☰按钮挤到最右侧 ======
        top_layout.addStretch(1)

        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(30,28)
        top_layout.addWidget(self.menu_btn)
        # 绑定菜单点击事件
        self.menu_btn.clicked.connect(self.on_menu_click)

        top_item.setSizeHint(QSize(200, 36))
        self.addItem(top_item)
        self.setItemWidget(top_item, top_widget)

        # 灰色分隔线
        sep_item = QListWidgetItem()
        sep_item.setFlags(Qt.NoItemFlags)
        sep_item.setSizeHint(QSize(200, 2))  # 高度2像素，横向铺满侧边栏
        self.addItem(sep_item)
        sep_widget = QWidget()
        sep_widget.setStyleSheet("background-color:#cccccc;")
        self.setItemWidget(sep_item, sep_widget)

    def on_menu_click(self):
        # 切换批量模式开关
        self.batch_mode = not self.batch_mode
        self.set_all_chat_item_batch(self.batch_mode)
        # 向外发送信号，通知主窗口显示/隐藏底部删除按钮
        self.menu_clicked.emit(self.batch_mode)

    def set_all_chat_item_batch(self, enable):
        for i in range(self.count()):
            item = self.item(i)
            w = self.itemWidget(item)
            # 跳过顶部按钮行、分割线，只处理对话条目
            if w and hasattr(w, "set_batch_mode"):
                w.set_batch_mode(enable)

    def add_chat(self, chat_name):
        item = QListWidgetItem()
        chat_widget = ChatItemWidget(chat_name)
        item.setSizeHint(QSize(200,36))
        self.addItem(item)
        self.setItemWidget(item, chat_widget)
        chat_widget.btn_name.clicked.connect(lambda checked, w=chat_widget: self.chat_switch.emit(w.chat_name))
        # 修复：实时读取控件最新chat_name，重命名后也能正确删除
        chat_widget.btn_del.clicked.connect(lambda checked, w=chat_widget: self.chat_delete.emit(w.chat_name))
        # 新增聊天默认不显示复选框
        chat_widget.set_batch_mode(False)
        # 返回聊天控件实例给主窗口
        return chat_widget

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
        # 强制关闭批量多选模式
        self.batch_mode = False
        self.set_all_chat_item_batch(False)
        self.menu_clicked.emit(False)
