from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame,
    QSizePolicy, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt
from ui.message_bubble import MessageBubble


class ChatArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("ChatArea")  # 用于全局QSS选择器

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 移除固定白色背景，交给全局主题控制
        self.scroll.setStyleSheet("border:none;")

        self.msg_container = QWidget()
        self.msg_container.setObjectName("msg_container")
        self.msg_layout = QVBoxLayout(self.msg_container)
        self.msg_layout.setSpacing(14)
        self.msg_layout.setAlignment(Qt.AlignTop)
        self.msg_layout.setContentsMargins(20, 20, 20, 20)

        self.scroll.setWidget(self.msg_container)
        main_layout.addWidget(self.scroll)

    def add_bubble(self, text, is_user, time_text=None):
        print("ChatArea add_bubble 执行，文本：", text)

        if time_text is None:
            from datetime import datetime
            time_text = datetime.now().strftime("%H:%M")

        bubble = MessageBubble(text, is_user)

        # 角色标签，去掉固定背景色，适配主题
        role_label = QLabel()
        role_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        role_label.setObjectName("role_label")
        role_label.setText("你" if is_user else "AI")

        # 时间标签
        time_label = QLabel(time_text)
        time_label.setObjectName("time_label")

        # 头部：角色 + 时间
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # 单条消息行
        msg_widget = QWidget()
        msg_layout = QVBoxLayout(msg_widget)
        msg_layout.setContentsMargins(0, 0, 0, 0)
        msg_layout.setSpacing(6)

        if is_user:
            # 用户消息：右对齐
            header_layout.addStretch(1)
            header_layout.addWidget(time_label)
            header_layout.addWidget(role_label)

            msg_layout.addLayout(header_layout)
            msg_layout.addWidget(bubble)

        else:
            # AI消息：左对齐，添加导出按钮
            header_layout.addWidget(role_label)
            header_layout.addWidget(time_label)
            header_layout.addStretch(1)

            # 导出按钮
            export_word_btn = QPushButton("导出 Word")
            export_excel_btn = QPushButton("导出 Excel")
            for btn in [export_word_btn, export_excel_btn]:
                btn.setObjectName("export_btn")
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(8)
            button_layout.addWidget(export_word_btn)
            button_layout.addWidget(export_excel_btn)
            button_layout.addStretch(1)

            msg_layout.addLayout(header_layout)
            msg_layout.addWidget(bubble)
            msg_layout.addLayout(button_layout)

        # ============ 外层wrapper布局 ============
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        if is_user:
            # 用户消息：靠右
            wrapper_layout.addStretch(1)
            wrapper_layout.addWidget(msg_widget)
        else:
            # AI消息：靠左
            wrapper_layout.addWidget(msg_widget, stretch=1)

        self.msg_layout.addWidget(wrapper)

        # 自动滚动到底部
        self.msg_container.adjustSize()
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())