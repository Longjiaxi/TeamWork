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
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QThread, Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer
from ui.sidebar import Sidebar
from ui.title_bar import TitleBar
from ui.input_bar import InputBar
from ui.chat_area import ChatArea
from PySide6.QtWidgets import QFileDialog
import os
from PySide6.QtWidgets import QMessageBox


class AIRequestThread(QThread):
    """流式AI请求线程【对接通义千问】"""
    stream_signal = Signal(str)    # 流式返回文本
    finish_signal = Signal(str)    # 对话结束

    def __init__(self, context_list, prompt):
        super().__init__()
        self.context = context_list
        self.user_prompt = prompt

    def run(self):
        import requests
        # ========= 在这里填入你的 DashScope API Key =========
        api_key = "sk-ws-H.PHLIIYE.AKpG.MEUCIHwN-veYrNHmZ2apoLGGWjHRVgxygPuZuASSkW82wXYdAiEA67G3MSICyubQ9wvKC-Zigzqdl2PHyysJDt1nfQkRLVg"
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        messages = self.context.copy()
        # ========新增系统提示词，强制中文回答========
        system_msg = {"role": "system",
                      "content": "你是中文AI助手，所有回答必须使用中文，禁止使用英文，简洁清晰地回答用户问题。"}
        messages.insert(0, system_msg)  # 插到列表最前面
        messages.append({"role": "user", "content": self.user_prompt})
        data = {
            "model": "qwen-turbo",
            "messages": messages
        }
        try:
            resp = requests.post(url, headers=headers, json=data)
            res_json = resp.json()
            ai_full_text = res_json["choices"][0]["message"]["content"]
        except Exception as e:
            ai_full_text = f"请求异常：{str(e)}"
        self.finish_signal.emit(ai_full_text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Chat")
        self.setWindowIcon(QIcon("res/icon.png"))
        self.resize(1200, 800)

        self.context_history = []
        self.batch_mode = False
        # OCR引擎延迟初始化
        self.ocr_engine = None
        # 侧边栏折叠标记
        self.sidebar_expanded = True
        self.sidebar_origin_width = 200

        # ----------------------中心部件和整体布局----------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部标题栏
        self.title_bar = TitleBar()
        main_layout.addWidget(self.title_bar)

        # 水平布局：侧边栏 + 聊天主区域
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0,0,0,0)
        h_layout.setSpacing(0)
        main_layout.addLayout(h_layout)

        # 实例化侧边栏
        self.sidebar = Sidebar()
        h_layout.addWidget(self.sidebar)
        self.sidebar.menu_clicked.connect(self.on_sidebar_menu)
        self.sidebar.menu_btn.clicked.connect(self.on_toggle_batch)


        # 右侧分割线
        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setStyleSheet("background:#cccccc;")
        h_layout.addWidget(divider)

        # 右侧聊天面板，垂直布局：上方聊天展示区，底部输入框
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(12,12,12,12)
        chat_layout.setSpacing(10)

        # 聊天消息显示区域
        self.chat_display = ChatArea()
        chat_layout.addWidget(self.chat_display, stretch=1)

        # --------实例化我们的底部输入栏组件--------
        self.input_bar = InputBar()
        chat_layout.addWidget(self.input_bar)
        h_layout.addWidget(chat_area, stretch=1)

        # =====================信号绑定=====================
        # 新建聊天按钮信号
        self.sidebar.new_chat_clicked.connect(self.new_chat)
        # 选中对话
        self.sidebar.chat_switch.connect(self.switch_conversation)
        # 删除单条对话
        self.sidebar.chat_delete.connect(self.delete_conversation)

        # =========输入框组件信号绑定=========
        self.input_bar.sig_send_text.connect(self.on_send_text)
        self.input_bar.sig_file_selected.connect(self.on_select_file)
        self.input_bar.sig_img_selected.connect(self.on_select_image)
        self.input_bar.sig_voice_click.connect(self.on_voice_input)
        self.input_bar.sig_clear_click.connect(self.on_clear_chat)

        # 加载主题相关
        current_theme = "light"
        if current_theme == "light":
            self.title_bar.theme_btn.setText("☀ 浅色模式")
        else:
            self.title_bar.theme_btn.setText("🌙 夜间模式")

        # 底部批量操作栏【先创建按钮，再绑定！】
        self.batch_bar = QWidget()
        batch_layout = QHBoxLayout(self.batch_bar)
        self.batch_bar.setVisible(False)

        self.btn_batch_del = QPushButton("确定删除")
        self.btn_cancel = QPushButton("取消")

        # ==========事件绑定==========
        self.btn_batch_del.clicked.connect(self.batch_delete)
        # 取消按钮：关闭批量模式，和右上角三条杠关闭效果一致
        self.btn_cancel.clicked.connect(self.cancel_batch)

        batch_layout.addStretch()
        batch_layout.addWidget(self.btn_batch_del)
        batch_layout.addWidget(self.btn_cancel)
        main_layout.addWidget(self.batch_bar)

    # =========新建对话：自动寻找最小空缺编号=========
    def new_chat(self):
        # 新建对话清空上下文
        self.context_history = []
        name_list = []
        # 遍历侧边栏所有item，跳过顶部新建按钮 和 分割线这两行
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            widget = self.sidebar.itemWidget(item)
            if hasattr(widget, "chat_name"):
                try:
                    num = int(widget.chat_name.replace("对话", ""))
                    name_list.append(num)
                except:
                    pass
        # 寻找最小可用编号
        min_id = 1
        while min_id in name_list:
            min_id += 1
        new_name = f"对话{min_id}"
        self.sidebar.add_chat(new_name)

    # =========删除对话=========
    def delete_conversation(self, chat_name):
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            widget = self.sidebar.itemWidget(item)
            if hasattr(widget, "chat_name") and widget.chat_name == chat_name:
                self.sidebar.takeItem(i)
                break

    # 切换选中对话（预留，后续加载聊天记录）
    def switch_conversation(self, chat_name):
        pass

    # 侧边栏展开收缩
    def toggle_sidebar(self):
        pass

    # 主题切换
    def toggle_theme(self):
        pass

    # 批量删除相关函数
    def show_batch_bar(self):
        self.batch_bar.setVisible(True)

    def hide_batch_bar(self):
        self.batch_bar.setVisible(False)

    def on_toggle_batch(self):
        self.batch_mode = not self.batch_mode
        print(f"【MAIN DEBUG】主窗口批量模式 {self.batch_mode}")
        if self.batch_mode:
            self.show_batch_bar()
        else:
            self.hide_batch_bar()
        self.sidebar.set_all_chat_item_batch(self.batch_mode)

    def batch_delete(self):
        selected_names = self.sidebar.get_selected_chat_names()
        if not selected_names:
            QMessageBox.information(self, "提示", "请勾选要删除的对话！")
            return
        # 确认弹窗
        ret = QMessageBox.question(self, "确认删除", f"确定删除选中{len(selected_names)}条对话吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            for name in selected_names:
                self.delete_conversation(name)
        # 删除完成，自动退出批量模式
        self.sidebar.set_all_chat_item_batch(False)
        self.batch_mode = False
        self.hide_batch_bar()

    def on_sidebar_menu(self, batch_enable):
        if batch_enable:
            self.show_batch_bar()
        else:
            self.hide_batch_bar()

    def cancel_batch(self):
        # 取消按钮：关闭批量模式，和右上角☰关闭效果完全一致
        self.batch_mode = False
        self.sidebar.set_all_chat_item_batch(False)
        self.hide_batch_bar()

    # ----------------输入栏回调函数----------------
    def on_send_text(self, text):
        print("发送文本：", text)
        self.add_chat_bubble(text, is_user=True)
        # 用户消息存入上下文
        self.context_history.append({"role": "user", "content": text})

        # 启动AI请求子线程
        self.ai_thread = AIRequestThread(self.context_history, text)
        # 绑定AI完成信号
        self.ai_thread.finish_signal.connect(self.receive_ai_finish)
        self.ai_thread.start()

    def on_select_file(self, file_path):
        print("选择文件：", file_path)
        # 文件上传预留

    def on_select_image(self, img_path):
        print("选择图片：", img_path)
        # 图片上传预留

    def on_voice_input(self):
        print("语音输入点击")
        # 语音预留

    def on_clear_chat(self):
        print("清空对话")
        # 清空聊天展示区预留

    def add_chat_bubble(self, text, is_user):
        # 渲染消息气泡
        self.chat_display.add_bubble(text, is_user)

    def receive_ai_stream(self, chunk_text):
        # 流式分片，逐字输出
        print("AI片段：", chunk_text)

    def receive_ai_finish(self, full_text):
        # AI回答完毕，添加气泡并保存上下文
        self.add_chat_bubble(full_text, is_user=False)
        self.context_history.append({"role": "assistant", "content": full_text})

    # 语音识别、文件上传、AI对话逻辑全部预留占位
    def handle_ai_message(self):
        pass

    def upload_file(self):
        pass

    def speech_recognize(self):
        pass

    def closeEvent(self, event):
        pass


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
