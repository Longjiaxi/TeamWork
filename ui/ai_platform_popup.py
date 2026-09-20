from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QSize
import webbrowser
from pathlib import Path


class FirstPopup(QWidget):
    """第一层弹窗：应用按钮"""
    def __init__(self, parent, second_popup):
        super().__init__(parent)
        self.second_popup = second_popup
        self.setObjectName("AiPlatformPopup")
        self.setWindowFlags(Qt.Widget)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(40,40,40,40)
        layout.setSpacing(30)

        self.btn_app = QPushButton("应用")
        self.btn_app.setFixedSize(120,45)
        self.btn_app.clicked.connect(self.open_second)
        layout.addWidget(self.btn_app, alignment=Qt.AlignCenter)

        self.close_btn = QPushButton("关闭")
        self.close_btn.setFixedHeight(40)
        self.close_btn.clicked.connect(self.hide)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.hide()
        self._rect = None

    def open_second(self):
        self.hide()
        if self._rect:
            self.second_popup.update_size(self._rect)
        self.second_popup.show()

    def update_size(self, rect):
        self._rect = rect
        self.setGeometry(rect)


class AiSelectPopup(QWidget):
    """第二层弹窗：6个AI按钮【优化版】"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AiPlatformPopup")
        self.setWindowFlags(Qt.Widget)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.icon_root = Path(__file__).parent.parent / "icons"
        print("图标文件夹路径：", self.icon_root)

        self.ai_list = [
            {"name":"豆包", "icon":"doubao.png", "url":"https://www.doubao.com"},
            {"name":"Kimi", "icon":"kimi-.png", "url":"https://kimi.moonshot.cn"},
            {"name":"通义千问", "icon":"qianwen.png", "url":"https://tongyi.aliyun.com"},
            {"name":"文心一言", "icon":"wenxin.png", "url":"https://yiyan.baidu.com"},
            {"name":"DeepSeek", "icon":"deepseek.png", "url":"https://chat.deepseek.com"},
            {"name":"ChatGLM", "icon":"chatglm.png", "url":"https://chatglm.cn"},
        ]

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(32)

        # 标题
        title_label = QLabel("AI应用入口")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color:#222;")
        main_layout.addWidget(title_label)

        row1 = QHBoxLayout()
        row1.setSpacing(24)
        row2 = QHBoxLayout()
        row2.setSpacing(24)

        for index, item in enumerate(self.ai_list):
            btn = QPushButton()
            btn.setFixedSize(160,160)
            icon_path = self.icon_root / item["icon"]
            btn.setIcon(QIcon(str(icon_path)))
            btn.setIconSize(QSize(72,72))
            btn.setText(item["name"])
            # 卡片圆角、阴影、悬浮变色样式
            btn.setStyleSheet("""
                QPushButton{
                    background-color:#ffffff;
                    border:1px solid #e8e8e8;
                    border-radius:18px;
                    text-align:center;
                    padding-top:18px;
                    font-size:14px;
                    color:#222222;
                }
                QPushButton:hover{
                    border:1px solid #409eff;
                    background-color:#f5faff;
                }
                QPushButton:pressed{
                    background-color:#e8f4ff;
                }
            """)
            url = item["url"]
            btn.clicked.connect(lambda checked, u=url: webbrowser.open(u))
            if index <3:
                row1.addWidget(btn)
            else:
                row2.addWidget(btn)

        main_layout.addLayout(row1)
        main_layout.addLayout(row2)
        main_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(self.hide)
        main_layout.addWidget(close_btn)

        self.setLayout(main_layout)
        self.hide()

    def update_size(self, rect):
        self.setGeometry(rect)


# 保留AiPlatformPopup类名，main_window完全不用修改
class AiPlatformPopup(FirstPopup):
    def __init__(self, parent):
        self._second_pop = AiSelectPopup(parent)
        super().__init__(parent, self._second_pop)
