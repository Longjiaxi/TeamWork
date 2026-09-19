from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QToolButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import webbrowser
from pathlib import Path


class AiPlatformPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AiPlatformPopup")
        self.setAttribute(Qt.WA_StyledBackground, True)

        # 自动定位icons目录：当前ui文件夹上级目录下的icons
        self.icon_dir = Path(__file__).parent.parent / "icons"

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        title = QLabel("选择AI平台")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold;")
        main_layout.addWidget(title)

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        # 加大按钮之间的横向间距
        row1.setSpacing(25)
        row2.setSpacing(25)

        # 平台配置：名称、跳转链接、对应图标文件名
        ai_list = [
            ("豆包", "https://www.doubao.com", "doubao.png"),
            ("Kimi", "https://kimi.moonshot.cn", "kimi-.png"),
            ("文心一言", "https://yiyan.baidu.com", "wenxin.png"),
            ("通义千问", "https://tongyi.aliyun.com", "qianwen.png"),
            ("DeepSeek", "https://chat.deepseek.com", "deepseek.png"),
            ("ChatGLM", "https://chatglm.cn", "chatglm.png"),
        ]

        for idx, (name, url, icon_file) in enumerate(ai_list):
            btn = QToolButton()
            btn.setText(name)
            # 加载对应图标
            btn.setIcon(QIcon(str(self.icon_dir / icon_file)))
            # 缩小图标尺寸，给文字预留更多空间
            btn.setIconSize(QSize(48, 48))
            # 文字显示在图标下方
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            # 加宽按钮、适度加高，彻底解决文字拥挤
            btn.setFixedSize(170, 110)

            btn.setStyleSheet("""
                QToolButton{
                    font-size:15px;
                    border-radius:12px;
                    border: 1px solid #cccccc;
                    background-color:#f8f8f8;
                    padding: 12px 8px;
                }
                QToolButton:hover{
                    background-color:#e8f2ff;
                    border-color:#409eff;
                }
            """)
            # 绑定跳转事件
            btn.clicked.connect(lambda checked, u=url: webbrowser.open(u))

            if idx < 3:
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

        self.hide()

    def update_size(self, rect):
        self.setGeometry(rect)
