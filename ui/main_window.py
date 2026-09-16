from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QApplication,
    QPushButton,
    QFrame,
    QLabel,
    QDialog,
    QComboBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, Signal, Qt
from ui.sidebar import Sidebar
from ui.title_bar import TitleBar

# from core.conversation_manager import ConversationManager
# from styles.theme_manager import ThemeManager

# from core.api import LLMAPI
from PySide6.QtWidgets import QFileDialog

import os
# from core.logger import get_logger

# from core.agent_manager import AgentManager
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
# ========== 新增：蓝牙耳机麦克风断线定时检测 ==========
from PySide6.QtCore import QTimer
# from audio_recorder import AudioRecorder
from PySide6.QtWidgets import QMessageBox
# from config import save_audio_selected_device

# logger = get_logger("main_window")

class AIRequestThread(QThread):
    """流式AI请求线程【仅占位，业务逻辑全部移除】"""
    stream_signal = Signal(str)    # 每收到一段文本触发
    finish_signal = Signal(str)    # 请求结束触发，返回完整内容

    def __init__(self, context_list, model_name):
        super().__init__()
        self.context = context_list
        self.model_name = model_name
        # self.thread_log = get_logger("ai_thread")

    def run(self):
        # 业务代码全部移除，仅占位
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # logger.info("主窗口 MainWindow 开始初始化")
        self.setWindowTitle("AI Chat")
        # 设置窗体左上角图标
        self.setWindowIcon(QIcon("res/icon/app.png"))
        self.resize(900, 700)

        # OCR引擎 延迟初始化
        self.ocr_engine = None

        # 侧边栏折叠状态
        self.sidebar_expanded = True
        self.sidebar_origin_width = 200

        # ==========================
        # 中央窗口
        # ==========================
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # ==========================
        # 主布局（上下）
        # ==========================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # ==========================
        # 标题栏
        # ==========================
        self.title_bar = TitleBar()
        main_layout.addWidget(self.title_bar)
        # 标题栏加号信号绑定【注释业务信号】
        # self.title_bar.add_tab_clicked.connect(self.switch_to_function_page)
        # 首页 → 返回聊天首页 index1
        # self.title_bar.home_tab_clicked.connect(self.switch_to_chat_page)
        # 智能体（暂时预留，后续再加页面）
        # self.title_bar.agent_tab_clicked.connect(self.switch_to_agent_page)

        # 全局通栏水平分割线（模型上方，横跨整个窗口）
        # ==========================
        self.full_line = QFrame()

        self.full_line.setStyleSheet("background-color:#cccccc; height:1px; border:none;")
        main_layout.addWidget(self.full_line)

        # ==========================
        # 内容布局（左右：侧边栏 + 竖分割线 + 右侧面板）
        # ==========================
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addLayout(content_layout)

        # 左侧侧边栏
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)

        # 垂直竖分割线，紧贴侧边栏右边缘，边框完美对齐
        self.divider_vline = QFrame()

        self.divider_vline.setStyleSheet("background-color:#cccccc; width:1px; border:none;")
        content_layout.addWidget(self.divider_vline)



        # 注册页面到堆栈
          # index0 应用页面
           # index1 聊天首页
              # index2 智能体
          # index4 小程序
          # index5 【翻译页面】

        # 默认启动展示聊天页


        # 聊天页面内部布局（原有right_layout迁移进去）

        # ======================================
        # self.func_select_page.switch_app_page.connect(self.on_app_item_click)

        # ==========================
        # 聊天管理器信号绑定【全部注释业务】
        # ==========================
        # self.conversation_manager = ConversationManager()
        # self.agent_manager = AgentManager()  # 新增
        # self.sidebar.new_chat_clicked.connect(self.new_chat)
        # self.sidebar.chat_switch.connect(self.switch_conversation)
        # self.sidebar.chat_delete.connect(self.delete_conversation)
        # self.sidebar.enter_batch_mode.connect(self.show_batch_bar)
        # self.sidebar.exit_batch_mode.connect(self.hide_batch_bar)

        # 加载本地持久化会话，添加到侧边栏【注释业务加载】
        # for chat_name in self.conversation_manager.chat_name_list:
        #     self.sidebar.add_chat(chat_name)

        # ==========================
        # 顶部横向容器：折叠按钮 + 模型选择器
        # ==========================
        top_row_widget = QWidget()
        top_row_layout = QHBoxLayout(top_row_widget)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(8)

        self.btn_toggle_sidebar = QPushButton("◧")
        self.btn_toggle_sidebar.setFixedSize(34, 34)
        icon_font = QFont("微软雅黑", 20)
        icon_font.setBold(True)
        self.btn_toggle_sidebar.setFont(icon_font)
        self.btn_toggle_sidebar.setStyleSheet("""
        QPushButton {
            border: none;
            background: transparent;
        }
        QPushButton:hover {
            background: #e2e2e2;
            border-radius: 6px;
        }
        """)
        # self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)

        # 模型选择器

        # 初始化默认选中模型

        # 绑定模型切换信号
        # self.model_selector.model_changed.connect(self.on_model_switch)

        # 布局：仅保留折叠按钮 + 模型下拉框
        top_row_layout.addWidget(self.btn_toggle_sidebar)

        top_row_layout.addStretch()


        # ==========================
        # 聊天区域 拉伸权重5（占5份高度）
        # ==========================

        # ==========================
        # 【核心修复：提前初始化全局音频实例，放在InputBar创建之前】【注释音频业务】
        # ==========================
        # 全局录音实例，和标题栏麦克风设备同步
        # self.global_audio_recorder = AudioRecorder()
        # 2秒检测一次音频设备插拔/断线
        self.audio_check_timer = QTimer()
        self.audio_check_timer.setInterval(2000)
        # self.audio_check_timer.timeout.connect(self.check_audio_device_change)
        self.audio_check_timer.start()
        # 绑定麦克风切换信号，同步全局录音器设备ID
        # self.title_bar.mic_device_switch_signal.connect(self.sync_global_mic_device)

        # ==========================
        # 输入区域（改为self.input_wrap，支持主题切换）拉伸权重1（占1份高度）
        # ==========================
        self.input_wrap = QWidget()
        wrap_layout = QVBoxLayout(self.input_wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(0)

        # self.input_bar = InputBar(self.global_audio_recorder)

        # 全部信号绑定放在实例创建之后，修复属性不存在报错【注释】
        # self.input_bar.send_message.connect(self.send_message)
        # self.input_bar.upload_file_signal.connect(self.open_file_upload)
        # =========【新增绑定语音录音信号】==========
        # self.input_bar.voice_audio_signal.connect(self.handle_voice_recognize)

        self.ocr_reader = None
        # self.input_bar.clear_chat_signal.connect(self.clear_chat)

        # 仅添加一次，消除重复控件

        # 浅色默认样式
        self.input_wrap.setStyleSheet("""
                QWidget {
                    border: 1px solid #cccccc;
                    border-radius: 18px;
                    background-color: #f8f8f8;
                }
                """)

        # self.title_bar.switch_theme_signal.connect(self.toggle_theme)

        # 小程序页面打开网页信号
        # self.miniprogram_page.open_web_tab_signal.connect(self.open_web_view_page)
        # self.func_select_page.goto_translate_signal.connect(self.open_translate_page)

        # ==========================
        # 批量操作底部栏（默认隐藏）
        # ==========================
        self.batch_bar = QWidget()
        batch_layout = QHBoxLayout(self.batch_bar)
        batch_layout.setContentsMargins(16, 8, 16, 8)
        self.batch_bar.setStyleSheet("background:#f0f0f0;")

        self.btn_batch_del = QPushButton("批量删除选中话题")
        # self.btn_batch_del.clicked.connect(self.batch_delete_selected)
        self.btn_cancel_batch = QPushButton("取消批量")
        # self.btn_cancel_batch.clicked.connect(self.sidebar.toggle_batch_mode)

        batch_layout.addWidget(self.btn_batch_del)
        batch_layout.addStretch()
        batch_layout.addWidget(self.btn_cancel_batch)
        self.batch_bar.setVisible(False)
        main_layout.addWidget(self.batch_bar)

        # 启动主题文字同步 + 输入框初始化样式【注释ThemeManager业务】
        # current_theme = ThemeManager.get_theme()
        # logger.info(f"加载初始主题: {current_theme}")
        current_theme = "light"
        if current_theme == "light":
            self.title_bar.theme_btn.setText("☀ 浅色模式")
        else:
            self.title_bar.theme_btn.setText("🌙 深色模式")
            self.full_line.setStyleSheet("background-color:#383838; height:1px; border:none;")
            self.divider_vline.setStyleSheet("background-color:#383838; width:1px; border:none;")
            # 初始化深色输入框灰黑色背景
            self.input_wrap.setStyleSheet("""
                    QWidget {
                        border: 1px solid #444444;
                        border-radius: 18px;
                        background-color: #2a2a2a;
                    }
                    """)

        # =========绑定所有按钮按压动画==========
        # 标题栏全部按钮

        # 侧边栏折叠按钮

        # 底部批量栏按钮


        # logger.info("主窗口初始化完成")

    # =========【新增：语音识别处理函数】==========
    def handle_voice_recognize(self, audio_buffer):
        pass

    # 侧边栏展开/收起切换
    def toggle_sidebar(self):
        pass

    def show_batch_bar(self):
        pass

    def hide_batch_bar(self):
        pass

    #批量删除
    def batch_delete_selected(self):
        pass

    # 切换深浅主题（同步横线、竖线、输入框背景边框）
    def toggle_theme(self):
        pass

    # 清空聊天消息
    def clear_chat_area(self):
        pass

    # 切换对话加载历史
    def switch_conversation(self, chat_name):
        pass

    # 删除对话
    def delete_conversation(self, chat_name):
        pass

    # 发送消息【对接真实API，自动编号、多轮记忆】
    def send_message(self, data):
        pass

    # 新建对话【侧边栏按钮专用：永远生成全新对话】
    def new_chat(self):
        pass

    # 函数保留，后续如需按钮可启用
    def switch_current_session_agent(self):
        pass

    def change_session_agent(self, chat_title: str, new_agent_id: str):
        pass

    # 打开文件选择窗口
    def open_file_upload(self):
        pass

    # 图片上传弹窗
    def open_image_upload(self):
        pass

    # OCR图片识别
    def read_image_ocr(self, img_path):
        pass

    # 读取文档内容
    def read_file_text(self, file_path):
        pass

    # 清空当前会话消息弹窗
    def clear_chat(self):
        pass

    def switch_to_function_page(self):
        pass

    def switch_to_chat_page(self):
        pass

    def switch_to_agent_page(self):
        pass

    def on_app_item_click(self, app_name):
        pass

    def open_web_view_page(self, url):
        pass

    def open_translate_page(self):
        pass

    def show_select_agent_dialog(self):
        pass




    def on_model_switch(self, model_text):
        pass

    # ========== 新增：定时检测麦克风/蓝牙耳机断线函数 ==========
    def check_audio_device_change(self):
        pass

    def closeEvent(self, event):
        pass
