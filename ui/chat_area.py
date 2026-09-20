from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer


class ChatBubble(QFrame):
    def __init__(self, is_user: bool):
        super().__init__()
        self.is_user = is_user
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8,6,8,6)
        layout.setSpacing(4)

        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.label)

        if is_user:
            # 用户气泡 靠右，蓝色
            self.setStyleSheet("""
                QFrame{background:#409EFF;border-radius:12px;}
                QLabel{color:#ffffff;}
            """)
        else:
            # AI气泡靠左，灰色
            self.setStyleSheet("""
                QFrame{background:#f0f0f0;border-radius:12px;}
                QLabel{color:#222222;}
            """)


class ChatArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("ChatArea")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(12)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border:none;")
        scroll_content = QWidget()
        self.msg_layout = QVBoxLayout(scroll_content)
        self.msg_layout.setAlignment(Qt.AlignTop)
        self.msg_layout.setSpacing(12)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 思考动画
        self.thinking_bubble = None
        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(self.update_thinking_dot)
        self.dot_index = 0

        # 当前正在打字的AI气泡
        self.current_ai_bubble = None

    def update_thinking_dot(self):
        dot_list = ["思考中.", "思考中..", "思考中..."]
        if self.thinking_bubble:
            self.thinking_bubble.label.setText(dot_list[self.dot_index % 3])
            self.dot_index += 1

    def show_thinking(self):
        if self.thinking_bubble is not None:
            return
        # AI思考气泡靠左
        wrap_widget = QWidget()
        h_layout = QHBoxLayout(wrap_widget)
        h_layout.setContentsMargins(0,0,0,0)
        bubble = ChatBubble(is_user=False)
        bubble.label.setText("思考中.")
        h_layout.addWidget(bubble)
        h_layout.addStretch()
        self.msg_layout.addWidget(wrap_widget)
        self.thinking_bubble = bubble
        self.thinking_timer.start(400)

    def hide_thinking(self):
        self.thinking_timer.stop()
        if self.thinking_bubble:
            wrap = self.thinking_bubble.parentWidget()
            self.msg_layout.removeWidget(wrap)
            wrap.deleteLater()
            self.thinking_bubble = None

    def create_empty_ai_bubble(self):
        """创建空白AI气泡，用来逐字填充"""
        wrap_widget = QWidget()
        h_layout = QHBoxLayout(wrap_widget)
        h_layout.setContentsMargins(0,0,0,0)
        bubble = ChatBubble(is_user=False)
        bubble.label.setText("")
        h_layout.addWidget(bubble)
        h_layout.addStretch()
        self.msg_layout.addWidget(wrap_widget)
        self.current_ai_bubble = bubble

    def append_ai_char(self, char):
        """追加单个文字到当前AI气泡"""
        if self.current_ai_bubble:
            old_text = self.current_ai_bubble.label.text()
            self.current_ai_bubble.label.setText(old_text + char)

    def add_bubble(self, text, is_user):
        """添加完整消息气泡（用户消息用这个）"""
        wrap_widget = QWidget()
        h_layout = QHBoxLayout(wrap_widget)
        h_layout.setContentsMargins(0,0,0,0)
        bubble = ChatBubble(is_user)
        bubble.label.setText(text)
        if is_user:
            h_layout.addStretch()
            h_layout.addWidget(bubble)
        else:
            h_layout.addWidget(bubble)
            h_layout.addStretch()
        self.msg_layout.addWidget(wrap_widget)

    def clear(self):
        # 清空所有消息
        while self.msg_layout.count() > 0:
            item = self.msg_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.thinking_bubble = None
        self.current_ai_bubble = None
        self.thinking_timer.stop()