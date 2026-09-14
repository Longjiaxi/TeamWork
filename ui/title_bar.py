from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QComboBox
)
from PySide6.QtCore import Signal



class TitleBar(QWidget):
    # 切换主题信号
    switch_theme_signal = Signal()
    agent_tab_clicked = Signal()
    add_tab_clicked = Signal()
    home_tab_clicked = Signal()  # 首页点击信号
    # 新增：麦克风切换信号，传给主窗口同步全局录音实例
    mic_device_switch_signal = Signal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("TitleBar")
        self.setFixedHeight(50)

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(12, 0, 12, 0)
        root_layout.setSpacing(6)

        # 左侧标签容器
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(4)

        # 首页标签
        self.btn_home = QPushButton("🏠 首页")
        self.btn_home.setObjectName("tab_home")
        self.btn_home.clicked.connect(self.home_tab_clicked.emit)
        # 智能体标签
        self.btn_agent = QPushButton("✧ 智能体")
        self.btn_agent.setObjectName("tab_agent")
        self.btn_agent.clicked.connect(self.agent_tab_clicked.emit)
        # 加号按钮
        self.btn_add = QPushButton("+")
        self.btn_add.setObjectName("tab_add")
        self.btn_add.clicked.connect(self.add_tab_clicked.emit)

        tab_layout.addWidget(self.btn_home)
        tab_layout.addWidget(self.btn_agent)
        tab_layout.addWidget(self.btn_add)

        # 中间弹性空白
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # 右侧原有功能按钮
        self.theme_btn = QPushButton("☀ 浅色模式")
        self.theme_btn.setObjectName("theme_btn")
        self.setting_btn = QPushButton("⚙ 设置")
        self.setting_btn.setObjectName("setting_btn")
        self.close_btn = QPushButton("✖")
        self.close_btn.setObjectName("close_btn")
        self.theme_btn.clicked.connect(self.switch_theme_signal.emit)

        # 布局顺序：左侧标签 → 空白弹性区 → 麦克风下拉 → 主题/设置/关闭
        root_layout.addWidget(tab_widget)
        root_layout.addItem(spacer)
        root_layout.addWidget(self.mic_combo)
        root_layout.addSpacing(8)
        root_layout.addWidget(self.theme_btn)
        root_layout.addWidget(self.setting_btn)
        root_layout.addWidget(self.close_btn)

        self.is_dark = False
        self.update_style()

