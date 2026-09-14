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

#from ui.input_bar import InputBar
#from ui.model_selector import ModelSelector

#from ui.chat_item import ChatListItem

from PySide6.QtWidgets import QFileDialog

import os

#from ui.function_select_page import FunctionSelectPage
#from ui.chat_container_page import ChatContainerPage
from PySide6.QtWidgets import QStackedWidget

#from ui.knowledge_page import KnowledgePage
#from ui.miniprogram_page import MiniProgramPage
from PySide6.QtWebEngineWidgets import QWebEngineView
#from ui.translate_page import TranslatePage

from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
# ========== 新增：蓝牙耳机麦克风断线定时检测 ==========
from PySide6.QtCore import QTimer
#from audio_recorder import AudioRecorder
from PySide6.QtWidgets import QMessageBox
#from config import save_audio_selected_device
#import opencc





class AIRequestThread(QThread):
    """流式AI请求线程，逐段推送文本片段，结束返回完整文本"""
    stream_signal = Signal(str)    # 每收到一段文本触发
    finish_signal = Signal(str)    # 请求结束触发，返回完整内容

    def __init__(self, context_list, model_name):
        super().__init__()
        self.context = context_list
        self.model_name = model_name




class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

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


        # 标题栏加号信号绑定【新增】

        # 首页 → 返回聊天首页 index1

        # 智能体（暂时预留，后续再加页面）


        # 全局通栏水平分割线（模型上方，横跨整个窗口）
        # ==========================
        self.full_line = QFrame()
        self.full_line.setFrameShape(QFrame.HLine)
        self.full_line.setFrameShadow(QFrame.Plain)
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



        # 垂直竖分割线，紧贴侧边栏右边缘，边框完美对齐
        self.divider_vline = QFrame()
        self.divider_vline.setFrameShape(QFrame.VLine)
        self.divider_vline.setFrameShadow(QFrame.Plain)
        self.divider_vline.setStyleSheet("background-color:#cccccc; width:1px; border:none;")
        content_layout.addWidget(self.divider_vline)

        # =========右侧页面堆栈【新增】==========
        self.right_stack = QStackedWidget()
        # 页面实例




        # !!!先初始化LLMAPI，再创建翻译页面



        # 注册页面到堆栈
        # index0 应用页面
       # index1 聊天首页
 # index2 智能体
 # index3 知识库
 # index4 小程序
 # index5 【翻译页面】

        # 默认启动展示聊天页
        self.right_stack.setCurrentIndex(1)

        # 聊天页面内部布局（原有right_layout迁移进去）

        # ======================================

        # ==========================
        # 聊天管理器信号绑定
        # ==========================


        # 加载本地持久化会话，添加到侧边栏


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

        # 模型选择器

        # 初始化默认选中模型

        # 绑定模型切换信号


        # 布局：仅保留折叠按钮 + 模型下拉框
        top_row_layout.addWidget(self.btn_toggle_sidebar)

        top_row_layout.addStretch()



        # ==========================
        # 聊天区域 拉伸权重5（占5份高度）
        # ==========================



        # ==========================
        # 【核心修复：提前初始化全局音频实例，放在InputBar创建之前】
        # ==========================


        # ==========================
        # 输入区域（改为self.input_wrap，支持主题切换）拉伸权重1（占1份高度）
        # ==========================
        self.input_wrap = QWidget()
        wrap_layout = QVBoxLayout(self.input_wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(0)

        # 现在 global_audio_recorder 已提前定义，不会报未定义

        # 全部信号绑定放在实例创建之后，修复属性不存在报错
        self.input_bar.send_message.connect(self.send_message)
        self.input_bar.upload_file_signal.connect(self.open_file_upload)


        self.ocr_reader = None
        self.input_bar.clear_chat_signal.connect(self.clear_chat)

        # 仅添加一次，消除重复控件
        wrap_layout.addWidget(self.input_bar)

        # 浅色默认样式
        self.input_wrap.setStyleSheet("""
                QWidget {
                    border: 1px solid #cccccc;
                    border-radius: 18px;
                    background-color: #f8f8f8;
                }
                """)


        # 主题切换信号绑定


        # 小程序页面打开网页信号


        # ==========================
        # 批量删除操作底部栏（默认隐藏）
        # ==========================


        # 启动主题文字同步 + 输入框初始化样式


        # =========绑定所有按钮按压动画==========
        # 标题栏全部按钮
        self.add_button_press_anim(self.title_bar.btn_home)
        self.add_button_press_anim(self.title_bar.btn_agent)
        self.add_button_press_anim(self.title_bar.btn_add)
        self.add_button_press_anim(self.title_bar.theme_btn)
        self.add_button_press_anim(self.title_bar.setting_btn)
        self.add_button_press_anim(self.title_bar.close_btn)
        # 侧边栏折叠按钮
        self.add_button_press_anim(self.btn_toggle_sidebar)
        # 底部批量栏按钮
        self.add_button_press_anim(self.btn_batch_del)
        self.add_button_press_anim(self.btn_cancel_batch)



    # =========语音识别处理函数==========

    # 侧边栏展开/收起切换

    #批量删除

    # 切换深浅主题（同步横线、竖线、输入框背景边框）

    # 清空聊天消息

    # 切换对话加载历史

    # 删除对话

    # ========== 用户消息发送+保存（原有逻辑完全不变）==========

    # ========== 会话自动重命名（原有逻辑完全不变）==========

    # ========== 流式展示核心逻辑==========

    # 新建对话

    # 打开文件选择窗口

    # 图片上传弹窗

    # OCR图片识别

    # 读取文档内容

    # 清空当前会话消息弹窗

    # ========== 新增：定时检测麦克风/蓝牙耳机断线函数 ==========
