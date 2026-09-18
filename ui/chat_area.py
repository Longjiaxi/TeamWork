from PySide6.QtWidgets import (     QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame,     QSizePolicy, QHBoxLayout, QPushButton )
from PySide6.QtCore import Qt
from ui.message_bubble import MessageBubble

class ChatArea(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("border:none; background-color:#ffffff;")

        self.msg_container = QWidget()
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
        # 角色标签
        role_label = QLabel()
        role_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        role_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                background-color: #f5f5f5;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                padding: 2px 8px;
            }
        """)
        role_label.setText("你" if is_user else "AI")

        # 时间标签
        time_label = QLabel(time_text)
        time_label.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 12px;
            }
        """)

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
            # 用户消息：右对齐，【不添加导出按钮】
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
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #d9d9d9;
                        border-radius: 6px;
                        padding: 4px 10px;
                        font-size: 12px;
                        color: #333333;
                    }
                    QPushButton:hover {
                        background-color: #f0f7ff;
                        border-color: #409eff;
                    }
                """)
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
            # 用户消息：靠右，固定最大宽度
            wrapper_layout.addStretch(1)
            wrapper_layout.addWidget(msg_widget)
        else:
            # AI消息：靠左，给拉伸权重，让气泡横向拉长
            wrapper_layout.addWidget(msg_widget, stretch=1)

        self.msg_layout.addWidget(wrapper)

        # 自动滚动到底部
        self.msg_container.adjustSize()
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    # ===================== 新增 clear 方法（和add_bubble同级缩进！）=====================
    def clear(self):
        # 清空所有消息气泡
        while self.msg_layout.count() > 0:
            item = self.msg_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
