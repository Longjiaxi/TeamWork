from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Signal

class TitleBar(QWidget):
    # 信号定义
    switch_theme_signal = Signal(bool)
    sync_code_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("TitleBar")
        self.setFixedHeight(50)
        self.is_dark = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # 左侧按钮
        self.btn_home = QPushButton("🏠 首页")
        self.btn_agent = QPushButton("◇ 智能体")
        self.btn_add = QPushButton("+")
        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_agent)
        layout.addWidget(self.btn_add)

        # 弹性空间，把右边控件推到最右侧
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # ====== 代码自动同步按钮 ======
        self.sync_btn = QPushButton("🔁 代码自动同步")
        self.sync_btn.clicked.connect(self.sync_code_signal.emit)
        # 深蓝色样式，和截图一致
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background-color:#22406b;
                color:white;
                border-radius:6px;
                padding:6px 12px;
                border:none;
            }
            QPushButton:hover{background-color:#2c548c;}
        """)

        # 右侧其他按钮
        self.theme_btn = QPushButton("☀️ 浅色模式")
        self.theme_btn.clicked.connect(self.on_theme_click)
        self.btn_setting = QPushButton("⚙️ 设置")

        layout.addWidget(self.sync_btn)
        layout.addWidget(self.theme_btn)
        layout.addWidget(self.btn_setting)


    def on_theme_click(self):
        self.is_dark = not self.is_dark
        self.switch_theme_signal.emit(self.is_dark)
        if self.is_dark:
            self.theme_btn.setText("🌙 深色模式")
        else:
            self.theme_btn.setText("☀️ 浅色模式")
