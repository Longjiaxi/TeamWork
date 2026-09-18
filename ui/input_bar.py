from PySide6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QFileDialog, QTextEdit, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QCursor


class InputBar(QWidget):
    sig_file_selected = Signal(str)
    sig_img_selected = Signal(str)
    sig_voice_click = Signal()
    sig_clear_click = Signal()
    sig_send_text = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InputBar")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        input_container = QFrame()
        input_container.setObjectName("input_container")
        # 删除固定白色背景，边框交给全局主题控制
        input_container.setStyleSheet("""
            QFrame#input_container {
                border: 1px solid;
                border-radius: 8px;
            }
        """)

        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(6)
        input_layout.setContentsMargins(8, 8, 8, 8)

        self.text_edit = QTextEdit()
        self.text_edit.setFrameShape(QFrame.NoFrame)
        self.text_edit.setPlaceholderText("给 AI 发送消息 (Enter发送, Shift+Enter换行)")
        self.text_edit.setMaximumHeight(70)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
            }
        """)

        button_bar = QWidget()
        button_bar.setStyleSheet("background-color: transparent;")
        button_layout = QHBoxLayout(button_bar)
        button_layout.setSpacing(6)
        button_layout.setContentsMargins(0, 0, 0, 0)

        btn_upload = QPushButton("📄")
        btn_upload.setToolTip("上传文件")
        btn_upload.setCursor(QCursor(Qt.PointingHandCursor))
        btn_upload.setObjectName("func_btn")
        btn_upload.clicked.connect(self.on_upload)

        btn_img = QPushButton("🖼️")
        btn_img.setToolTip("添加图片")
        btn_img.setCursor(QCursor(Qt.PointingHandCursor))
        btn_img.setObjectName("func_btn")
        btn_img.clicked.connect(self.on_image)

        btn_voice = QPushButton("🎤")
        btn_voice.setToolTip("语音输入")
        btn_voice.setCursor(QCursor(Qt.PointingHandCursor))
        btn_voice.setObjectName("func_btn")
        btn_voice.clicked.connect(self.on_voice)

        btn_clear = QPushButton("🗑️")
        btn_clear.setToolTip("删除对话")
        btn_clear.setCursor(QCursor(Qt.PointingHandCursor))
        btn_clear.setObjectName("func_btn")
        btn_clear.clicked.connect(self.on_clear)

        btn_send = QPushButton("⬆️ 发送")
        btn_send.setCursor(QCursor(Qt.PointingHandCursor))
        btn_send.setObjectName("send_btn")
        btn_send.clicked.connect(self.on_send)

        button_layout.addWidget(btn_upload)
        button_layout.addWidget(btn_img)
        button_layout.addWidget(btn_voice)
        button_layout.addWidget(btn_clear)
        button_layout.addStretch()
        button_layout.addWidget(btn_send)

        input_layout.addWidget(self.text_edit)
        input_layout.addWidget(button_bar)

        main_layout.addWidget(input_container)
        self.setLayout(main_layout)

    def on_send(self):
        content = self.text_edit.toPlainText().strip()
        if content:
            self.sig_send_text.emit(content)
            self.text_edit.clear()

    def on_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择要上传的文件", "C:/", "所有文件 (*.*)"
        )
        if file_path:
            self.sig_file_selected.emit(file_path)

    def on_image(self):
        img_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", r"C:\Users\asus\AppData\Roaming\yysls",
            "图片 (*.png *.jpg *.jpeg *.bmp)"
        )
        if img_path:
            self.sig_img_selected.emit(img_path)

    def on_voice(self):
        self.sig_voice_click.emit()

    def on_clear(self):
        self.sig_clear_click.emit()