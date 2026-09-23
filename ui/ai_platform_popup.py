from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QStackedWidget, QHBoxLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import webbrowser
from pathlib import Path


class AiPlatformPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AiPlatformPopup")
        self.setAttribute(Qt.WA_StyledBackground, True)
        # 铺满父容器（右侧对话区域）
        if parent:
            self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet("background-color:#ffffff;")

        self.icon_dir = Path(__file__).parent.parent / "icons"

        self.ai_list = [
            {"name": "ChatGLM",   "icon": "chatglm.png",   "url": "https://chatglm.cn/"},
            {"name": "DeepSeek",  "icon": "deepseek.png",  "url": "https://www.deepseek.com/"},
            {"name": "豆包",      "icon": "doubao.png",    "url": "https://www.doubao.com/"},
            {"name": "Kimi",      "icon": "kimi-.png",     "url": "https://kimi.moonshot.cn/"},
            {"name": "通义千问",  "icon": "qianwen.png",   "url": "https://tongyi.aliyun.com/"},
            {"name": "文心一言",  "icon": "wenxin.png",    "url": "https://yiyan.baidu.com/"},
        ]

        self.stack = QStackedWidget()
        self.page_select = QWidget()

        self.init_select_page()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.stack.addWidget(self.page_select)
        self.stack.setCurrentWidget(self.page_select)

    def init_select_page(self):
        layout = QVBoxLayout(self.page_select)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(30)

        title = QLabel("选择AI平台")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#222;")
        layout.addWidget(title)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0,0,0,0)

        for index, item in enumerate(self.ai_list):
            btn = QPushButton()
            btn.setFixedSize(160, 160)

            icon_path = self.icon_dir / item["icon"]
            btn.setIcon(QIcon(str(icon_path)))
            btn.setIconSize(QSize(80, 80))
            btn.setText(item["name"])

            btn.setStyleSheet("""
                QPushButton {
                    text-align: bottom;
                    padding-bottom: 12px;
                    font-size: 14px;
                    border-radius: 12px;
                    border: 1px solid #e5e7eb;
                    background-color: #ffffff;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #f3f4f6;
                    border-color: #d1d5db;
                }
                QPushButton:pressed {
                    background-color: #e5e7eb;
                }
            """)
            # 点击按钮，调用系统浏览器打开网页
            btn.clicked.connect(lambda checked=False, url=item["url"]: webbrowser.open(url))
            row = index // 3
            col = index % 3
            grid_layout.addWidget(btn, row, col)

        layout.addLayout(grid_layout)
        layout.addStretch()

        # 底部返回关闭按钮
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.setContentsMargins(0,10,0,10)
        self.close_popup_btn = QPushButton("← 返回关闭")
        self.close_popup_btn.setFixedHeight(42)
        self.close_popup_btn.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding:0 16px;
                border:none;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """)
        self.close_popup_btn.clicked.connect(self.hide)
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(self.close_popup_btn)
        bottom_btn_layout.addStretch()
        layout.addLayout(bottom_btn_layout)