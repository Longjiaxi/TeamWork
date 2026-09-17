from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class MessageBubble(QFrame):
    def __init__(self, text, is_user):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14,10,14,10)
        layout.setSpacing(0)

        label = QLabel(text)
        label.setWordWrap(True)  # 开启自动换行，气泡自适应高度
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if is_user:
            label.setMaximumWidth(540)
        else:
            label.setMaximumWidth(760)

        layout.addWidget(label)

        if is_user:
            self.setStyleSheet("""
                QFrame{background:#409eff;border-radius:12px;}
                QLabel{color:white;font-size:14px;}
            """)
        else:
            self.setStyleSheet("""
                QFrame{background:#f0f0f0;border-radius:12px;}
                QLabel{color:#222;font-size:14px;}
            """)
