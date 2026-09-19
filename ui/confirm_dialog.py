from PySide6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt


class AiSelectDialog(QDialog):
    def __init__(self, parent, web_view_callback):
        super().__init__(parent)
        self.web_view_callback = web_view_callback
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 遮罩
        mask = QWidget()
        mask.setStyleSheet("background-color:rgba(0,0,0,140);")
        mask_layout = QVBoxLayout(mask)

        # 卡片容器
        card = QWidget()
        card.setStyleSheet("background:#fff;border-radius:14px;padding:24px;")
        card_layout = QVBoxLayout(card)

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        card_layout.addLayout(row1)
        card_layout.addLayout(row2)

        ai_list = [
            ("豆包", "https://www.doubao.com"),
            ("Kimi", "https://kimi.moonshot.cn"),
            ("文心一言", "https://yiyan.baidu.com"),
            ("通义千问", "https://tongyi.aliyun.com"),
            ("DeepSeek", "https://chat.deepseek.com"),
            ("ChatGLM", "https://chatglm.cn"),
        ]

        for idx, (name, url) in enumerate(ai_list):
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton{
                    padding:16px 10px;min-width:130px;min-height:110px;font-size:14px;
                    border-radius:10px;background:#f7f7f7;border:none;
                }
                QPushButton:hover{background:#e8f0fe;}
            """)
            btn.clicked.connect(lambda checked, u=url: self.on_ai_selected(u))
            if idx < 3:
                row1.addWidget(btn)
            else:
                row2.addWidget(btn)

        mask_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(mask)

    def on_ai_selected(self, url):
        self.web_view_callback(url)
        self.close()

    def mousePressEvent(self, event):
        # 点击空白遮罩关闭弹窗
        if not self.childAt(event.pos()):
            self.close()
