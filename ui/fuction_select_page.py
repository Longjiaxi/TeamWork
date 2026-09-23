from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton
from PySide6.QtCore import Signal
# =========新增导入AI弹窗类=========
from ui.ai_platform_popup import AiPlatformPopup

class FunctionSelectPage(QWidget):
    # 新增页面跳转信号
    switch_app_page = Signal(str)
    goto_translate_signal = Signal()

    def __init__(self):
        super().__init__()
        self.is_dark = False
        # 保存弹窗实例，防止窗口被垃圾回收自动关闭
        self.ai_pop_window = None
        self.init_ui()
        self.update_style()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24,24,24,24)
        main_layout.setSpacing(20)

        self.title_label = QLabel("<h2>应用</h2>")
        main_layout.addWidget(self.title_label)
        grid = QGridLayout()
        grid.setSpacing(24)

        row0 = ["小程序","知识库","绘画","助手库","翻译","文件"]
        row1 = ["Code","OpenClaw","笔记"]
        self.button_list = []

        # 第一行按钮
        for idx,name in enumerate(row0):
            btn = QPushButton(name)
            btn.setFixedSize(130,100)
            # 改动：点击按钮触发自定义处理函数
            btn.clicked.connect(lambda checked,n=name: self.handle_app_click(n))
            grid.addWidget(btn, 0, idx)
            self.button_list.append(btn)
        # 第二行按钮
        for idx,name in enumerate(row1):
            btn = QPushButton(name)
            btn.setFixedSize(130,100)
            btn.setFixedSize(130,100)
            btn.clicked.connect(lambda checked,n=name: self.handle_app_click(n))
            grid.addWidget(btn, 1, idx)
            self.button_list.append(btn)

        main_layout.addLayout(grid)
        main_layout.addStretch()
        self.setLayout(main_layout)

    # =========新增：处理应用按钮点击逻辑=========
    def handle_app_click(self, app_name:str):
        if app_name == "小程序":
            # 点击小程序，弹出AI平台弹窗
            self.ai_pop_window = AiPlatformPopup(self)
            self.ai_pop_window.show()
        else:
            # 其他所有按钮保持原来逻辑，向外发送信号（原有功能完全保留）
            self.switch_app_page.emit(app_name)

    def update_style(self):
        if self.is_dark:
            page_style = """ QWidget{
    background-color:#1e1e1e;
    border:1px solid #3a3a3a;
    border-radius:12px;
}
            """
            btn_style = """ QPushButton{
    background-color:#323232;
    border:1px solid #444444;
    border-radius:10px;
    color:#eeeeee;
    font-size:13px;
}
QPushButton:hover{
    background-color:#3d3d3d;
    border-color:#505050;
}
QPushButton:pressed{
    background-color:#444444;
}
            """
            title_style = "color:#eeeeee;"
        else:
            page_style = """ QWidget{
    background-color:#ffffff;
    border:1px solid #DCDFE6;
    border-radius:12px;
}
            """
            btn_style = """ QPushButton{
    background-color:#f3f4f6;
    border:1px solid #e5e7eb;
    border-radius:10px;
    color:#444444;
    font-size:13px;
}
QPushButton:hover{
    background-color:#e9ebef;
    border-color:#dcdfe6;
}
QPushButton:pressed{
    background-color:#dde0e6;
}
            """
            title_style = "color:#333333;"

        self.setStyleSheet(page_style)
        self.title_label.setStyleSheet(title_style)
        for btn in self.button_list:
            btn.setStyleSheet(btn_style)

    def set_dark_mode(self, enable:bool):
        self.is_dark = enable
        self.update_style()

    def on_btn_translate_clicked(self):
        self.goto_translate_signal.emit()